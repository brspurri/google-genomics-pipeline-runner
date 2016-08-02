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
"""
So if you have a series of such files, batch them together:

 --input "gs://bucket/sample1/chrMT.bam gs://bucket/sample1/chrY.bam gs://<etc>"

Example Usage:

  * Build the provided docker image to build Samtools version 1.3.1. See Dockerfile for
  * python example.py \
        --project {PROJECT_NAME} \
        --name MyPipeline \
        --storage_output gs://{OUTPUT_BUCKET} \
        --storage_logging gs://{LOG_BUCKET} \
        --docker_image gcr.io/{PROJECT_NAME}/{TOOL}/{TAG}
"""

import os
import sys
import json
import argparse

# Import the library required to obtain your
#   Google Cloud SDK credentials
from oauth2client.client import GoogleCredentials

# Add the parent directory to the path so that the pipeline_runner library can be found.
_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../')
if os.path.isfile(os.path.join(_path, 'pipeline_runner', '__init__.py')):
    sys.path.insert(0, _path)

# Import the pipeline helper
from runner.pipeline_runner import Pipeline

# Set the global scope variables
credentials = GoogleCredentials.get_application_default()

# Parse the command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--project', action='store', dest='project')
parser.add_argument('--name', action='store', dest='name')
parser.add_argument('--docker_image', action='store', dest='docker_image')
parser.add_argument('--storage_output', action='store', dest='storage_output')
parser.add_argument('--storage_logging', action='store', dest='storage_logging')


def build_simple_example_pipeline():
    """
    Example to build a basic
    :return:
    """
    args = parser.parse_args()
    pipeline = Pipeline(credentials,
                        args.project,
                        args.name,
                        args.docker_image,
                        args.storage_output,
                        args.storage_logging)

    # Example disk name: can be any string. default size is 500gb.
    disk_name = 'mydisk'

    # Example mount point: the location where the abive disk will be mounted on the VM
    mount_point = '/mnt/data'

    # Add the disk to the configuration
    pipeline.add_disk(disk_name, mount_point)

    # Example input BAM file. Must be a google storage path: gs://bucket/key
    example_input_file = ('gs://genomics-public-data/ftp-trace.ncbi.nih.gov/1000genomes/'
                          'ftp/technical/pilot3_exon_targetted_GRCh37_bams/data/NA06986/'
                          'alignment/NA06986.chromMT.ILLUMINA.bwa.CEU.exon_targetted.20100311.bam')

    # Add the input file to the configuration
    pipeline.add_input(disk_name, example_input_file)

    # Build an very simple samtools index command for the pipeline to run
    pipeline.command = ('mkdir -p /mnt/data/output && '
                        'find /mnt/data/input && '
                        'for f in $(/bin/ls /mnt/data/input); do '
                        '  echo ${f}; '
                        '  samtools index /mnt/data/input/${f} /mnt/data/output/${f}.bai; '
                        'done')
    pipeline.command = 'ls -la {mount_point}/input'.format(mount_point=mount_point)

    # Build the configutation
    config = pipeline.build()

    # Output the config to STDOUT
    sys.stdout.write('Pipeline Arguments:\n')
    sys.stdout.write(json.dumps(config, indent=4, sort_keys=True))
    sys.stdout.write('\n')

    # Run the pipeline on Google Genomics infastructure
    operation = pipeline.run()

    # Output the response to STDOUT
    sys.stdout.write('Pipeline Response:\n')
    sys.stdout.write(json.dumps(operation, indent=4, sort_keys=True))
    sys.stdout.write('\n')

    # Polling
    sys.stdout.write('Polling NOT YER IMPLEMENTED. Stay tuned...\n')


if __name__ == "__main__":
    build_simple_example_pipeline()

