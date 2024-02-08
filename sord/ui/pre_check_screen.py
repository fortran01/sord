import sys
import os
import configparser
import subprocess
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)


class PreCheckScreen(QDialog):
    def __init__(self, parent=None):
        super(PreCheckScreen, self).__init__(parent)
        self.setWindowTitle("Pre-Check")
        self.setGeometry(
            100, 100, 500, 300
        )  # Adjusted size to make placeholder text visible

        layout = QVBoxLayout()

        self.checkLabel = QLabel("Checking system requirements...", self)
        layout.addWidget(self.checkLabel)

        self.setLayout(layout)

        self.config_path = self.determine_config_path()
        self.awsCliCheckResult = self.checkAWSCLI()
        self.updateCheckLabel(self.awsCliCheckResult)
        self.checkConfig()

    def determine_config_path(self):
        if sys.platform.startswith(("linux", "darwin")):
            return os.path.expanduser("~/.aws/config")
        elif sys.platform.startswith("win32"):
            return os.path.join(os.environ["USERPROFILE"], ".aws\\config")
        else:
            return None

    def checkAWSCLI(self):
        try:
            subprocess.check_output(["aws", "--version"], stderr=subprocess.STDOUT)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.updateCheckLabel(False)
            return False

    def updateCheckLabel(self, awsCliFound=True):
        if awsCliFound:
            self.checkLabel.setText("✓ AWS CLI tool found.")
        else:
            self.checkLabel.setText(
                "✕ AWS CLI tool not found. AWS CLI tool is not installed. "
                "Please install it to proceed.<br>Installation instructions: "
                "<a href='https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html'>AWS CLI Installation Guide</a>"
            )
            self.checkLabel.setOpenExternalLinks(True)
            if not hasattr(self, "retryButton"):
                self.showRetryButton()

    def checkConfig(self):
        config = configparser.ConfigParser()
        if self.config_path and os.path.exists(self.config_path):
            config.read(self.config_path)
            if config.has_section("profile for-sso") and config.has_section(
                "sso-session my-sso"
            ):
                self.checkLabel.setText(
                    self.checkLabel.text() + "<br>✓ AWS config file found and valid."
                )
                if self.awsCliCheckResult:
                    self.showContinueScreen()
            else:
                self.checkLabel.setText(
                    self.checkLabel.text() + "<br>✕ AWS config file found but invalid."
                )
                self.requestConfigInput()
        else:
            self.checkLabel.setText(
                self.checkLabel.text() + "<br>✕ AWS config files not found."
            )
            self.requestConfigInput()

    def showRetryButton(self):
        layout = self.layout()
        self.retryButton = QPushButton("Retry", self)
        self.retryButton.clicked.connect(self.retryCheck)
        layout.addWidget(self.retryButton)

    def retryCheck(self):
        self.awsCliCheckResult = self.checkAWSCLI()
        self.updateCheckLabel(self.awsCliCheckResult)
        self.checkConfig()

    def requestConfigInput(self):
        layout = self.layout()

        self.accountIdInput = QLineEdit(self)
        self.accountIdInput.setPlaceholderText(
            "Enter SSO account id (e.g. 111122223333)"
        )
        layout.addWidget(self.accountIdInput)

        self.roleNameInput = QLineEdit(self)
        self.roleNameInput.setPlaceholderText(
            "Enter SSO role name (e.g. AWSReadOnlyAccess)"
        )
        layout.addWidget(self.roleNameInput)

        self.ssoRegionInput = QLineEdit(self)
        self.ssoRegionInput.setPlaceholderText(
            "Enter the SSO region (default us-east-2)"
        )
        layout.addWidget(self.ssoRegionInput)

        # Ask for profile region input
        self.profileRegionInput = QLineEdit(self)
        self.profileRegionInput.setPlaceholderText(
            "Enter the AWS Account region (default us-west-2)"
        )
        layout.addWidget(self.profileRegionInput)

        self.ssoUrlInput = QLineEdit(self)
        self.ssoUrlInput.setPlaceholderText(
            "Enter SSO start URL (e.g. https://provided-domain.awsapps.com/start)"
        )
        layout.addWidget(self.ssoUrlInput)

        self.submitButton = QPushButton("Submit", self)
        self.submitButton.clicked.connect(self.onSubmit)
        layout.addWidget(self.submitButton)

    def onSubmit(self):
        account_id = self.accountIdInput.text()
        role_name = self.roleNameInput.text()
        sso_region = (
            self.ssoRegionInput.text() if self.ssoRegionInput.text() else "us-east-2"
        )
        profile_region = (
            self.profileRegionInput.text()
            if self.profileRegionInput.text()
            else "us-west-2"
        )
        sso_start_url = self.ssoUrlInput.text()

        config = configparser.ConfigParser()
        config.read(self.config_path)  # Read existing config to append to it
        if not config.has_section("profile for-sso"):
            config.add_section("profile for-sso")
        config.set("profile for-sso", "sso_session", "my-sso")
        config.set("profile for-sso", "sso_account_id", account_id)
        config.set("profile for-sso", "sso_role_name", role_name)
        config.set("profile for-sso", "region", profile_region)
        config.set("profile for-sso", "output", "json")

        if not config.has_section("sso-session my-sso"):
            config.add_section("sso-session my-sso")
        config.set("sso-session my-sso", "sso_region", sso_region)
        config.set("sso-session my-sso", "sso_start_url", sso_start_url)
        config.set(
            "sso-session my-sso", "sso_registration_scopes", "sso:account:access"
        )

        with open(self.config_path, "w") as configfile:  # Append to the config file
            config.write(configfile)

        self.checkConfig()  # Recheck the configuration after submission

    def showContinueScreen(self):
        layout = self.layout()
        continueButton = QPushButton("Continue", self)
        continueButton.clicked.connect(self.accept)
        layout.addWidget(continueButton)
