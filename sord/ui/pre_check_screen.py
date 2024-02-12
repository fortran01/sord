import sys
import os
import configparser
import subprocess
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal


class PreCheckScreen(QWidget):
    accepted = pyqtSignal()

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
        self.retryButton = None
        self.accountIdInput = None
        self.roleNameInput = None
        self.ssoRegionInput = None
        self.profileRegionInput = None
        self.ssoUrlInput = None
        self.submitButton = None

    def startPreCheck(self):
        self.showRetryButton()
        self.performChecks()

    def performChecks(self):
        self.awsCliCheckResult = self.checkAWSCLI()
        self.sessionManagerPluginCheckResult = self.checkSessionManagerPlugin()
        self.updateCheckLabel(
            self.awsCliCheckResult, self.sessionManagerPluginCheckResult
        )
        self.configCheckResult = self.checkConfig()

        if (
            self.awsCliCheckResult
            and self.sessionManagerPluginCheckResult
            and self.configCheckResult
        ):
            self.accepted.emit()

    def determine_config_path(self):
        try:
            if sys.platform.startswith(("linux", "darwin")):
                return os.path.expanduser("~/.aws/config")
            elif sys.platform.startswith("win32"):
                return os.path.join(os.environ["USERPROFILE"], ".aws\\config")
            else:
                return None
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred while determining the config path: {e}. Please try again.",
            )
            return None

    def checkAWSCLI(self):
        try:
            subprocess.check_output(["aws", "--version"], stderr=subprocess.STDOUT)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def checkSessionManagerPlugin(self):
        try:
            output = subprocess.check_output(
                ["session-manager-plugin"], stderr=subprocess.STDOUT
            ).decode()
            return (
                "The Session Manager plugin was installed successfully. Use the AWS CLI to start a session."
                in output
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def updateCheckLabel(self, awsCliFound=True, sessionManagerPluginFound=True):
        try:
            if awsCliFound:
                self.checkLabel.setText("✓ AWS CLI tool found.")
            else:
                self.checkLabel.setText(
                    "✕ AWS CLI tool not found. AWS CLI tool is not installed. "
                    "Please install it to proceed.<br>Installation instructions: "
                    "<a href='https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html'>AWS CLI Installation Guide</a>"
                )
                self.checkLabel.setOpenExternalLinks(True)
                if not self.retryButton:
                    self.showRetryButton()
            if sessionManagerPluginFound:
                self.checkLabel.setText(
                    self.checkLabel.text() + "<br>✓ Session Manager plugin found."
                )
            else:
                self.checkLabel.setText(
                    self.checkLabel.text() + "<br>✕ Session Manager plugin not found. "
                    "Please install it to proceed.<br>Installation instructions: "
                    "<a href='https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html'>Session Manager Plugin Installation Guide</a>"
                )
                self.checkLabel.setOpenExternalLinks(True)
                if not self.retryButton:
                    self.showRetryButton()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred while updating the check label: {e}. Please try again.",
            )

    def checkConfig(self):
        try:
            config = configparser.ConfigParser()
            if self.config_path and os.path.exists(self.config_path):
                config.read(self.config_path)
                if config.has_section("profile for-sso") and config.has_section(
                    "sso-session my-sso"
                ):
                    self.checkLabel.setText(
                        self.checkLabel.text()
                        + "<br>✓ AWS config file found and valid."
                    )
                    return True
                else:
                    self.checkLabel.setText(
                        self.checkLabel.text()
                        + "<br>✕ AWS config file found but invalid. "
                        + "For more information on configuring your profile with SSO, visit: "
                        + "<a href='https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html'>AWS CLI SSO Configuration Guide</a>"
                    )
                    self.checkLabel.setOpenExternalLinks(True)
                    self.requestConfigInput()
                    return False
            else:
                self.checkLabel.setText(
                    self.checkLabel.text() + "<br>✕ AWS config files not found."
                )
                self.requestConfigInput()
                return False
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while checking the AWS config: {e}. Please try again.",
            )
            return False

    def showRetryButton(self):
        try:
            layout = self.layout()
            if not self.retryButton:
                self.retryButton = QPushButton("Check Again", self)
                self.retryButton.clicked.connect(self.performChecks)
                layout.addWidget(self.retryButton)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred while showing the retry button: {e}. Please try again.",
            )

    def requestConfigInput(self):
        try:
            layout = self.layout()

            if not self.accountIdInput:
                self.accountIdInput = QLineEdit(self)
                self.accountIdInput.setPlaceholderText(
                    "Enter SSO account id (e.g. 111122223333)"
                )
                layout.addWidget(self.accountIdInput)

            if not self.roleNameInput:
                self.roleNameInput = QLineEdit(self)
                self.roleNameInput.setPlaceholderText(
                    "Enter SSO role name (e.g. AWSReadOnlyAccess)"
                )
                layout.addWidget(self.roleNameInput)

            if not self.ssoRegionInput:
                self.ssoRegionInput = QLineEdit(self)
                self.ssoRegionInput.setPlaceholderText(
                    "Enter the SSO region (default us-east-2)"
                )
                layout.addWidget(self.ssoRegionInput)

            if not self.profileRegionInput:
                self.profileRegionInput = QLineEdit(self)
                self.profileRegionInput.setPlaceholderText(
                    "Enter the AWS Account region (default us-west-2)"
                )
                layout.addWidget(self.profileRegionInput)

            if not self.ssoUrlInput:
                self.ssoUrlInput = QLineEdit(self)
                self.ssoUrlInput.setPlaceholderText(
                    "Enter SSO start URL (e.g. https://provided-domain.awsapps.com/start)"
                )
                layout.addWidget(self.ssoUrlInput)

            if not self.submitButton:
                self.submitButton = QPushButton("Submit", self)
                self.submitButton.clicked.connect(self.onSubmit)
                layout.addWidget(self.submitButton)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred while requesting config input: {e}. Please try again.",
            )

    def onSubmit(self):
        try:
            account_id = self.accountIdInput.text()
            role_name = self.roleNameInput.text()
            sso_region = (
                self.ssoRegionInput.text()
                if self.ssoRegionInput.text()
                else "us-east-2"
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

            self.performChecks()  # Recheck the configuration after submission
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while submitting the configuration: {e}. Please try again.",
            )
