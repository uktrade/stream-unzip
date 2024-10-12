---
layout: sub-navigation
order: 3
title: Limitations
---


Most ZIP files are stream-unzippable, however for technical reasons some are not. If a file is found to not be stream-unzippable, a NotStreamUnzippable exception will be raised.

The only way to address this is to change how the file is created. All member files in the ZIP must either be stored compressed, or stored without a "data descriptor", or if it has a non-zero length its length must be given in its "local header". Explanations of these terms can be found in the ZIP specification: [APPNOTE](https://support.pkware.com/pkzip/appnote).
