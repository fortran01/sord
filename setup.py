# https://github.com/httpie/cli/blob/master/setup.py

from setuptools import setup, find_packages

PROJECT_NAME = 'sord'
this_project = __import__(PROJECT_NAME)

# Note: keep requirements here to ease distributions packaging
tests_require = ["pytest"]
dev_require = [
    "pip",
    "bump2version",
    "wheel",
    "watchdog",
    "flake8",
    "coverage",
    "Sphinx",
    "twine",
    'click',
    'pytest',
]
install_requires = [
    'pip',
    'click',
]
install_requires_win_only = [
    "colorama>=0.2.4",
]

# bdist_wheel
extras_require = {
    "dev": dev_require,
    "test": tests_require,
    # https://wheel.readthedocs.io/en/latest/#defining-conditional-dependencies
    ':sys_platform == "win32"': install_requires_win_only,
}


def long_description():
    with open('README.rst', encoding='utf-8') as f:
        return f.read()


setup(
    name=PROJECT_NAME,
    version=this_project.__version__,
    description="The `sord` tool is used for signing in to AWS SSO and accessing EC2 machines via RDP.",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    url='https://github.com/fortran01/sord',
    author="Prem Rara",
    author_email='p@rara.dev',
    license="MIT license",
    packages=find_packages(include=[f"{PROJECT_NAME}", f"{PROJECT_NAME}.*"]),
    entry_points={
        'console_scripts': [
            'sord=sord.cli:main',
        ],
    },
    python_requires=">=3.10",
    extras_require=extras_require,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
