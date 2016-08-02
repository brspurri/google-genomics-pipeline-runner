google-genomics-pipeline-runner
===============================

**Disclaimer**: Google Genomics Pipeline API is in **alpha** development and will certainly break with
coming versions. I will do my best to maintain current compatibility, but do feel free
to submit issues (or better yet, pull requests)

--------

**Overview**: This project is a helper for generating simple, Google Genomics Pipeline configurations as python objects.
Information about the Pipeline API may be found at: https://cloud.google.com/genomics/reference/rest/v1alpha2/pipelines

`google-genomics-pipeline-runner` is designed to very simple to configure, and very quick to deploy workable,
scalable, bioinformatics pipelines on the Google Genomics Cloud infastructure.

-------

**Installing**:
```
NOT YET IMPLEMENTED
```

However, it *will be* `pip install google-genomics-pipeline-runner`

-------

**Maintainer**: `brett.spurrier@gmail.com`

-------

Examples
--------

There is currently one simple example located in the `examples/simple` folder of this repository.
More will be coming, and the complexity will be increasing. For now, please read the simple example
 as a way to setup a `pipeline_runner.Pipeline()` object run a single task through the Google Genomics Pipeline API.