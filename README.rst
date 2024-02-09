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

Features
--------

- Filter and display only those EC2 instances that are tagged with "Owner" equal to the email address of the logged-in user

- Attributes, such as ${aws:PrincipalTag/Owner}, from an external Identity Provider, for example, AWS Managed AD, are not available in the session from aws sso login. It appears that the session from AWS SSO in the web uses a combination of federated user and assumed role, whereas the session from aws sso login relies solely on an assumed role. The policy below is designed to work in both scenarios. Notice the use of the StringLike condition and the aws:userid condition key.

.. code-block:: json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ssm:StartSession",
                "ssm:TerminateSession",
                "ssm:DescribeSessions"
            ],
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "aws:userid": [
                        "*${ec2:ResourceTag/Owner}"
                    ]
                }
            }
        }
    ]
}

Requirements
------------

* TODO

Usage
-----

* TODO

Development
-----------

- Make utility

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
