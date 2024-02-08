====
sord
====


.. image:: https://img.shields.io/pypi/v/sord.svg
        :target: https://pypi.python.org/pypi/sord

.. image:: https://img.shields.io/travis/fortran01/sord.svg
        :target: https://travis-ci.com/fortran01/sord

.. image:: https://readthedocs.org/projects/sord/badge/?version=latest
        :target: https://sord.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




The `sord` tool is used for signing in to AWS SSO and accessing EC2 machines via RDP.


* Free software: MIT license


Features
--------

* TODO

Requirements
------------

* TODO

Usage
-----

* TODO

Development
-----------

- Make utility ([Make for Windows](https://gnuwin32.sourceforge.net/packages/make.htm), Make for Linux and Mac is usually pre-installed)

Set up the environment using the provided Makefile. Follow these steps:

1. Ensure you have `make` installed on your system. You can check this by running `make --version` in your terminal. Install or update `make` if needed.
2. Install the necessary dependencies by running `make install` or `make all`.
3. Create a Python virtual environment by running `python3 -m venv --prompt sord venv`. Activate it by running `source venv/bin/activate`.
4. Verify the installation by running `sord --version`. If the tool is installed correctly, it should display the version number.
5. Run the tool for example by running `python -m sord --help`.
6. Exit the virtual environment by running `deactivate`.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
