# sord

The `sord` tool is used for signing in to AWS SSO and accessing EC2 machines via RDP.

## Features

- Filter and display only those EC2 instances that are tagged with "Owner" equal to the email address of the logged-in user.

## Requirements

- [AWS CLI Tool](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Session Manager Plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)

## Usage

Download the latest release from the [releases page](https://github.com/fortran01/sord/releases). If none of the releases are compatible with your system, you can build the tool from source.

```bash
curl -L https://github.com/fortran01/sord/archive/refs/heads/main.zip -o sord-main.zip
unzip sord-main.zip
cd sord-main
make install
source venv/bin/activate
make pyinstaller-build
./dist/sord # Run the tool
```

## Development

- Make utility

Set up the environment using the provided Makefile. Follow these steps:

1. Ensure you have `make` installed on your system. You can check this by running `make --version` in your terminal. Install or update `make` if needed.
2. Install the necessary dependencies by running `make install` or `make all`.
3. Create a Python virtual environment by running `python3 -m venv --prompt sord venv`. Activate it by running `source venv/bin/activate`.
4. Verify the installation by running `sord --version`. If the tool is installed correctly, it should display the version number.
5. Run the tool for example by running `python -m sord --help`.
6. Exit the virtual environment by running `deactivate`.

## Known Issues

- During download, the Windows executable may be flagged as a virus (e.g., Trojan:Win32/Sabsik.FL.A!ml) by Windows Defender. This is a false positive. Use the zipped Windows executable instead.
- Windows Defender SmartScreen may block the tool from running because it is not signed. You can bypass this by clicking "More info" and then "Run anyway".
- Some virus installers detect "Win32/Wacapew.C!ml" in the executable. This is a false positive. The tool is safe to use. See [PyInstaller Issue #5668](https://github.com/pyinstaller/pyinstaller/issues/5668) and check the Github Action workflow `release-app.yml` for the steps that builds and releases the tool.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
