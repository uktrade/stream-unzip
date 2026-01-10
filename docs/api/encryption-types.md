---
layout: sub-navigation
sectionKey: API reference
eleventyNavigation:
    parent: API reference
order: 2
caption: API reference
title: Encryption types
---

Both the `stream_unzip.stream_unzip` and `stream_unzip.async_stream_unzip` functions take an `allowed_encrpytion_types` parameter specifies what encryption types are allowed. The parameters must be a Container of zero or more of the following types.

If a member file is encounted with an encryption type that is not in, a subclass of the `stream_unzip.EncryptionMechanismNotAllowed` exception is raised. See [Exception hierarchy](/api/exception-hierarchy/) for the specific exceptions.

### stream_unzip.NO_ENCRYPTION

Allow non-encrypted member files.

<hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible">

### stream_unzip.ZIP_CRYPTO

Allow member files encrypted with ZipCrypto.

<div class="govuk-warning-text">
  <span class="govuk-warning-text__icon" aria-hidden="true">!</span>
  <strong class="govuk-warning-text__text">
    <span class="govuk-visually-hidden">Warning</span>
    ZipCrypto is not secure enough for most uses
  </strong>
</div>

<hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible">

### stream_unzip.AE_1

Allow member files encrypted with AES according to the WinZip AE-1 specification. For this to function you must also pass at least one of `stream_unzip.AES_128`, `stream_unzip.AES_192`, or `stream_unzip.AES_256`.

<hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible">

### stream_unzip.AE_2

Allow member files encrypted with AES according to the WinZip AE-2 specification. For this to function you must also pass at least one of `stream_unzip.AES_128`, `stream_unzip.AES_192`, or `stream_unzip.AES_256`.

<hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible">

### stream_unzip.AES_128

Allow member files encrypted with AES using a 128 bit encryption key. For this to function you must also pass at least one of `stream_unzip.AE_1` or `stream_unzip.AE_2`.

<hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible">

### stream_unzip.AES_192

Allow member files encrypted with AES using a 192 bit encryption key. For this to function you must also pass at least one of `stream_unzip.AE_1` or `stream_unzip.AE_2`.

<hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible">

### stream_unzip.AES_256

Allow member files with AES using a 256 bit encryption key. For this to function you must also pass at least one of `stream_unzip.AE_1` or `stream_unzip.AE_2`.
