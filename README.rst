|checks| |tests| |codecov| |maintainability| |coverage|
|pre-commit| |black| |pep8| |semver|


Python library for BER-TLV en-/decoding.

Glossary
--------
BER
  Basic Encoding Rules is a standard encoding format for ASN.1.
  See `X.690 BER encoding`_ on Wikipedia.
TLV
  Encoding scheme which consists of the fields tag, length and value.
  See Type-length-value_ on Wikipedia.

References
----------
- `X.690 BER encoding`_
- Type-length-value_
- `ISO 7816-4 Annex D`_


.. |checks| image:: https://github.com/philipschoemig/BER-TLV/workflows/Checks/badge.svg
   :target: https://github.com/philipschoemig/BER-TLV/actions?query=workflow%3AChecks
   :alt: Checks

.. |tests| image:: https://github.com/philipschoemig/BER-TLV/workflows/Tests/badge.svg
   :target: https://github.com/philipschoemig/BER-TLV/actions?query=workflow%3ATests
   :alt: Tests

.. |codecov| image:: https://codecov.io/gh/philipschoemig/BER-TLV/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/philipschoemig/BER-TLV
   :alt: Code Coverage

.. |maintainability| image:: https://api.codeclimate.com/v1/badges/0231c41187cd922b6329/maintainability
   :target: https://codeclimate.com/github/philipschoemig/BER-TLV/maintainability
   :alt: Maintainability

.. |coverage| image:: https://api.codeclimate.com/v1/badges/0231c41187cd922b6329/test_coverage
   :target: https://codeclimate.com/github/philipschoemig/BER-TLV/test_coverage
   :alt: Test Coverage

.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: black

.. |pep8| image:: https://img.shields.io/badge/code%20style-pep8-orange.svg
   :target: https://www.python.org/dev/peps/pep-0008/
   :alt: pep8

.. |semver| image:: https://img.shields.io/badge/semver-2.0.0-black.svg
   :target: https://semver.org/spec/v2.0.0.html
   :alt: Semantic Versioning

.. _X.690 BER encoding: https://en.wikipedia.org/wiki/X.690#BER_encoding
.. _Type-length-value: https://en.wikipedia.org/wiki/Type-length-value
.. _ISO 7816-4 Annex D: https://cardwerk.com/iso7816-4-annex-d-use-of-basic-encoding-rules-asn-1/
