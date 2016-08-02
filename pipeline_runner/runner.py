#!/usr/bin/python
#
# The MIT License (MIT)
# Copyright (c) 2016 Brett Spurrier
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import os
import base64

# Google's API client library is required to
#   build the service call to the Google Genomics API.
from googleapiclient.discovery import build


# Set the Google Genomics Version number to be used in the service building.
# Note: This WILL change!
GOOGLE_GENOMICS_VERSION = 'v1alpha2'

# Google Storage version
GOOGLE_STORAGE_VERSION = 'v1'


class Pipeline:
    """
    Wrapper/helper for Google Genomics Pipeline API. This is being built to remove some of the redundant code
    that is present in the pipeline example code (https://github.com/brspurri/pipelines-api-examples).

    Please see example.py for example usages.
    """

    def __init__(self,
                 credentials,
                 project,
                 name,
                 docker_image,
                 storage_output,
                 storage_logging,
                 memory=3.75,
                 cores=1,
                 zones=list()):
        """
        Google Genomics Pipeline API wrapper/helper to make the generation
        of pipeline configurations and execution much simpler.
        Documentation is provided here, inline, so its time to get dirty in the code.

        :param credentials: Google Genomic credentials. Obtain via Google Genomics SDK.
        :param project: Name of the billable Google Storage project.
        :param name: Name of the current pipeline run.
        :param docker_image: Docker image endpoint. If private Google Compute MUST have access to the repo.
        :param storage_output: Path to the Google Storage bucket to transfer the output files to.
        :param storage_logging: Path to the Google Storage bucket to transfer the log files to.
        :param memory: Memory in GBs. [Default: 3.75].
        :param cores: Number of processors. [Default: 1].
        :param zones: List of available Google Compute zones.
        """

        # Set the credentials. Obtain from Google Cloud SDK.
        #   Follow the insstructions found here:
        #   https://cloud.google.com/genomics/install-genomics-tools
        self.credentials = credentials

        # Sets the name of the project
        #   This MUST match a billing-enabled project.
        #   You may find a list of your projects, enable billing, or create a new one here:
        #   https://console.cloud.google.com/home/dashboard
        self.project = project

        # Name of the pipeline run. You may set this to any string (alphanumeric?)
        self.name = name

        # Path to the Google Storge bucket in which the output files
        #   are transferred to upon pipeline completion.
        self.storage_output = storage_output

        # Path to the Google Storge bucket in which the log files
        #   are transferred to upon pipeline completion.
        self.storage_logging = storage_logging

        # Docker image endpoint.
        #   If this is in GCR, then the endpoint would look like: gcr.io/{project}/{tool}/{tag}
        #   This may also be a public dockerhub name: i.e., ubuntu
        self.docker_image = docker_image

        # Relative path of the input folder. All files specified in
        #   add_input() will be transferred to this folder.
        self.mounted_input_folder = 'input'

        # Relative path of the output folder. All files present in this folder
        #   at the end of execution will be transferred to the Google Storage bucket
        #   specified in self.storage_output
        self.mounted_output_folder = 'output'

        # Specifies the command to run on pipeline instantiation
        self.command = None

        # (Optional) Override for the memory to use with the VM.
        #   Default is 3.75 GB, but you may set this to any integer (be reasonable though!)
        self.memory = memory

        # (Optional) Override for the number of processors run the VM on.
        #   Default is 1, but you may set this to any integer (be reasonable though!)
        self.cores = cores

        # (Optional) Set the Google Compute zones.
        #   By default, Google Compute Engine chooses the zone(s) for you.
        #   More information can be found here:
        #   https://cloud.google.com/compute/docs/regions-zones/regions-zones
        self.zones = zones

        # (Internal) _disks: Disks to be mounted to the VM.
        self._disks = []            # ephemeralPipeline
        self._disk_resources = []   # pipelineArgs

        # (Internal) _inputs: Input parameters (keys) and their
        #   Google Storage paths (keys) to be transferred to the VM.
        #   Structure looks like:
        #      {
        #         filename_1: google_storage_path_1,
        #         filename_2: google_storage_path_2,
        #         ...
        #      }
        self._inputs = {}

        # (Internal) _outputs: Output parameters to transfer back to
        #   Google Storage (self.mounted_output_folder) after completion.
        self._outputs = []

        # (Internal) _pipeline: class variable for the pipeline config.
        #   Build by calling the build() command
        self._pipeline = {}

        # Create the storage service
        self.storage = build('storage', GOOGLE_STORAGE_VERSION, credentials=credentials)

        # Create the genomics service
        self.genomics = build('genomics', GOOGLE_GENOMICS_VERSION, credentials=self.credentials)

    def set_command(self, command, base64encoded=False):
        """
        Set the command to run on the Google Compute VM.
        This command is run AFTER all input files are transfered to the VM.

        :param command: Bash string command to execute.
        :param base64encoded: Option to base64 encode your command. Helpful for commands with special characters.
        """
        if base64encoded:
            self.command = base64.b64decode(command)
        else:
            self.command = command

    def add_disk(self, name, mount_point, size=None, autodelete=True):
        """
        Adds a disk to be mounted to the Google Compute VM.
        Adds the output path to the VM, and specifies that all files
        within the output path be transfered to Google Storage upon pipeline completion.

        :param name: Name of the disk. (alphnumeric?)
        :param mount_point: Path to mount the drive.
        :param size: Gb value for the disk size. NoneType sets Google Compute to 500gb. [Default: NoneType].
        :param autodelete: Specifies if the drive should be deleted on pipeline completion. [Default: True].
        """

        # Build the ephemeralPipeline disk parameter
        disk = {
            'name': name,
            'autoDelete': autodelete,
            'mountPoint': mount_point,
        }
        self._disks.append(disk)

        # Build the pipelineArgs disk parameter
        disk = {
            'name': name,
            'sizeGb': size
        }
        self._disk_resources.append(disk)

        # Build the output folder parameter `
        o = {
            'name': 'outputPath',
            'description': 'Output storage path file for: {}'.format(self.name),
            'localCopy': {
                'path': '{}/*'.format(self.mounted_output_folder),
                'disk': name
            }
        }
        self._outputs.append(o)

    def add_input(self, disk_name, gs_input):
        """
        Adds an input file to be transfered from a Google Storage path
        to the VM mounted input folder.

        :param disk_name: Name of the disk mounted to the VM. See add_disk().
        :param gs_input: Google Storage path for the file to be transferred to the VM.
        """
        f = {
            'name': 'inputFile{}'.format(len(self._inputs.values())),
            'description': 'Input file for: {}'.format(self.name),
            'localCopy': {
                'path': self.mounted_input_folder + '/' + os.path.basename(gs_input),
                'disk': disk_name
            }
        }

        # See __init__() for details about te structure of self._inputs.
        self._inputs[gs_input] = f

    def build(self):
        """
        Builds the pipeline configuration.
        The configuration follows the structure outlined here:
           https://cloud.google.com/genomics/reference/rest/v1alpha2/pipelines/run
        """

        # Pipeline configuration
        pipeline = {

            # Establish the ephemeral pipeline
            'ephemeralPipeline': {

                # Project properties
                'projectId': self.project,
                'name': self.name,
                'description': 'Run {} on one or more files via Google Genomics'.format(self.name),

                # Resources
                'resources': {

                    # Create a data disk that is attached to the VM and destroyed when the
                    # pipeline terminates.
                    'disks': self._disks,
                },

                # Specify the Docker image to use along with the command
                'docker': {

                    # Docker image name
                    'imageName': self.docker_image,

                    # Command to run
                    'cmd': self.command,
                },

                # Copy the passed input files to the VM's input_folder on disk_name fromGS
                'inputParameters': self._inputs.values(),

                # Copy the processed output files from the VM's input_folder on disk_name to GS
                'outputParameters': self._outputs
            },

            # Set the resources
            'pipelineArgs': {
                'projectId': self.project,

                # Override the resources needed for this pipeline
                'resources': {

                    # Set the memory
                    'minimumRamGb': self.memory,

                    # Set the minimum number of cored
                    'minimumCpuCores': self.cores,

                    # For the data disk, specify the size
                    'disks': self._disk_resources
                },

                # Map the input files to the input file keys
                'inputs': {
                    'inputFile{}'.format(i): f for i, f in enumerate(self._inputs.keys())
                    },

                # Pass the user-specified Cloud Storage destination path of the samtools output
                'outputs': {
                    'outputPath': self.storage_output
                },

                # Pass the user-specified Cloud Storage destination for pipeline logging
                'logging': {
                    'gcsPath': self.storage_logging
                }
            }
        }

        # Set the zones. If NoneType, use the Google Genomics
        #   default by do not including it in the resources.
        if self.zones:
            pipeline['pipelineArgs']['resources'] = self.zones

        # Set the class variable self.pipeline the pipeline args
        self._pipeline = pipeline

        # Return the pipeline confguration.
        #   The data returned is not necessarily needed since it is also
        #   stored in self._pipeline, however, this can be useful for debugging.
        return pipeline

    def run(self):

        # Run the pipeline
        return self.genomics.pipelines().run(body=self._pipeline).execute()
