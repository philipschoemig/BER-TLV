.. image:: https://github.com/philipschoemig/BER-TLV/workflows/Tests/badge.svg
   :target: https://github.com/philipschoemig/BER-TLV/actions?query=workflow%3ATests
   :alt: Tests

.. image:: https://api.codeclimate.com/v1/badges/0231c41187cd922b6329/maintainability
   :target: https://codeclimate.com/github/philipschoemig/BER-TLV/maintainability
   :alt: Maintainability

.. image:: https://api.codeclimate.com/v1/badges/0231c41187cd922b6329/test_coverage
   :target: https://codeclimate.com/github/philipschoemig/BER-TLV/test_coverage
   :alt: Test Coverage

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: black

.. image:: https://img.shields.io/badge/code%20style-pep8-orange.svg
   :target: https://www.python.org/dev/peps/pep-0008/
   :alt: pep8

About
=====
Python library for BER-TLV en-/decoding.

Glossary
========
BER
  Basic Encoding Rules is a standard encoding format for ASN.1.
  See `X.690 BER encoding`_ on Wikipedia.
TLV
  Encoding scheme which consists of the fields tag, length and value.
  See Type-length-value_ on Wikipedia.

References
==========
- `X.690 BER encoding`_
- Type-length-value_
- `ISO 7816-4 Annex D`_

.. _X.690 BER encoding: https://en.wikipedia.org/wiki/X.690#BER_encoding
.. _Type-length-value: https://en.wikipedia.org/wiki/Type-length-value
.. _ISO 7816-4 Annex D: https://cardwerk.com/iso7816-4-annex-d-use-of-basic-encoding-rules-asn-1/
