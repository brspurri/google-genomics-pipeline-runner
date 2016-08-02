google-genomics-pipeline-runner
===============================

**Disclaimer**: Google Genomics Pipeline API is in **alpha** development and will certainly break with
coming versions. I will do my best to maintain current compatibility, but do feel free
to submit issues (or better yet, pull requests)

--------

**Overview**: `google-genomics-pipeline-runner` is a **Python** project designed as a helper for generating simple and easy to use, Google Genomics Pipeline configurations as python objects.
Information about the Pipeline API may be found at:
https://cloud.google.com/genomics/reference/rest/v1alpha2/pipelines

`google-genomics-pipeline-runner` is designed to very simple to configure, and very quick to deploy workable,
scalable, bioinformatics pipelines on the Google Genomics Cloud infastructure.

-------

**Installing**:
```
pip install git@github.com:brspurri/google-genomics-pipeline-runner.git
```

However, it *will soon be*:

```
pip install google-genomics-pipeline-runner
```

-------

**Maintainer**: `brett.spurrier@gmail.com`

-------

Basic Usage
-----------

*Prerequisites*:
-  Install the Google Cloud SDK: https://cloud.google.com/sdk/downloads
-  Start a new Google Cloud project, or choose already have an existing one ready and **billing enabled'**
-  Enable the Google APIs: `Genomics API`, `Google Cloud Storage`, `Google Cloud Strage JSON API`, and `Google Compute Engine`

*Description*:

This is a very basic example that uses the `google-genomics-pipeline-runner` to execute a pipeline via Google Genomics Pipeline API. This tiny example starts a Google Compute VM, pulls and runs an ubuntu docker image image, transfers `/mnt/data/inputs/MyFile.bam` from Google Storage to the running VM, executes `ls -lah /mnt/data/inputs/MyFile.bam > /mnt/data/outputs/test.txt` and finally transfers `/mnt/data/outputs/test.txt` back to the Google Storage bucket `gs://{MyLogsBucket}`. The VM is destroyed and all disks are unmounted by Google's infrastructure automatically.

*Python Usage*:
```
>>> # Imports
>>> from oauth2client.client import GoogleCredentials
>>> from pipeline_runner import Pipeline

>>> # Get the Google Credentials
>>> credentials = GoogleCredentials.get_application_default()

>>> # Build the pipeline configuration. Make sure to change the values inside the {} to the correct ones for your project
>>> p = Pipeline(credentials, '{MyGoogleProject}', 'MyPipelineName', 'ubuntu', 'gs://{MyOutputBucket}', 'gs://{MyLogsBucket}')

>>> # Mount a 50GB disk to the VM
>>> p.add_disk('mydatadisk', '/mnt/data', size=50)

>>> # Transfer the input file to the VM and add it to the configuration
>>> p.add_input('mydatadisk', 'gs://{MyPrivateOrPublicDataBucket}/path/to/MyFile.bam')

>>> # Execute samtools index on MyFile.bam
>>> p.command = 'ls -lah /mnt/data/inputs/MyFile.bam > /mnt/data/outputs/test.txt'

>>> # Build the configuration
>>> p.build()

>>> # Execute the pipeline
>>> operation = p.run()
>>> print operation
```

Full Examples
-------------

There is currently one simple example located in the `examples/simple` folder of this repository.
More will be coming, and the complexity will be increasing. For now, please read the simple example
 as a way to setup a `pipeline_runner.Pipeline()` object run a single task through the Google Genomics Pipeline API.

Final Thoughts
--------------

This is a personal project and subject to my personal time. I love the genomics/bioinformatics space,
so please be patient with the development of this library. I **heavily encourage** collaborations and/or
partnerships on all areas of my genomics-interests. Get in touch!