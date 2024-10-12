---
layout: sub-navigation
order: 7
title: How to publish a release
---


Only mambers of the uktrade GitHub organisation may publish a release. If you are a member of the uktrade GitHub organsation:

1. Go to the [stream-unzip GitHub releases page](https://github.com/uktrade/stream-unzip/releases).

2. Click on "Draft a new release".

3. Click on "Choose a tag".

4. Enter a new tag name in the form vX.Y.Z, where X.Y.Z is the [Semver 2.0](https://semver.org/) version for this release, and press enter. Note that Semver 2.0 allows backwards incompatible changes in any release where X=0.

5. Click on "Generate release notes"

6. Modify the release notes if desired. No changes are often acceptable if PR titles are descriptive.

7. Click on "Publish release"

GitHub actions then automatically publishes this release to the [stream-unzip package on PyPI](https://pypi.org/project/stream-unzip/). You can monitor this process in the [GitHub actions page for stream-unzip](https://github.com/uktrade/stream-unzip/actions).
