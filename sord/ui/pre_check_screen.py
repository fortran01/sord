import sys
import os
import configparser
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton


class PreCheckScreen(QDialog):
    def __init__(self, parent=None):
        super(PreCheckScreen, self).__init__(parent)
        self.setWindowTitle("Pre-Check")
        self.setGeometry(
            100, 100, 500, 300
        )  # Adjusted size to make placeholder text visible

        layout = QVBoxLayout()

        self.checkLabel = QLabel("Checking for AWS config files...", self)
        layout.addWidget(self.checkLabel)

        self.setLayout(layout)

        self.config_path = self.determine_config_path()
        self.checkConfig()

    def determine_config_path(self):
        if sys.platform.startswith(("linux", "darwin")):
            return os.path.expanduser("~/.aws/config")
        elif sys.platform.startswith("win32"):
            return os.path.join(os.environ["USERPROFILE"], ".aws\\config")
        else:
            return None

    def checkConfig(self):
        config = configparser.ConfigParser()
        if self.config_path and os.path.exists(self.config_path):
            config.read(self.config_path)
            if config.has_section("profile for-sso") and config.has_section(
                "sso-session my-sso"
            ):
                self.checkLabel.setText("✓ AWS config file found and valid.")
                self.accept()
            else:
                self.checkLabel.setText("✕ AWS config file found but invalid.")
                self.requestConfigInput()
        else:
            self.checkLabel.setText("✕ AWS config files not found.")
            self.requestConfigInput()

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

        self.regionInput = QLineEdit(self)
        self.regionInput.setPlaceholderText("Enter region (default us-west-2)")
        layout.addWidget(self.regionInput)

        self.ssoUrlInput = QLineEdit(self)
        self.ssoUrlInput.setPlaceholderText(
            "Enter SSO start URL (e.g. https://provided-domain.awsapps.com/start)"
        )
        layout.addWidget(self.ssoUrlInput)

        submitButton = QPushButton("Submit", self)
        submitButton.clicked.connect(self.onSubmit)
        layout.addWidget(submitButton)

    def onSubmit(self):
        account_id = self.accountIdInput.text()
        role_name = self.roleNameInput.text()
        region = self.regionInput.text() if self.regionInput.text() else "us-west-2"
        sso_start_url = self.ssoUrlInput.text()

        config = configparser.ConfigParser()
        config.read(self.config_path)  # Read existing config to append to it
        if not config.has_section("profile for-sso"):
            config.add_section("profile for-sso")
        config.set("profile for-sso", "sso_session", "my-sso")
        config.set("profile for-sso", "sso_account_id", account_id)
        config.set("profile for-sso", "sso_role_name", role_name)
        config.set("profile for-sso", "region", region)
        config.set("profile for-sso", "output", "json")

        if not config.has_section("sso-session my-sso"):
            config.add_section("sso-session my-sso")
        config.set("sso-session my-sso", "sso_region", region)
        config.set("sso-session my-sso", "sso_start_url", sso_start_url)
        config.set(
            "sso-session my-sso", "sso_registration_scopes", "sso:account:access"
        )

        with open(self.config_path, "a") as configfile:  # Append to the config file
            config.write(configfile)
        self.accept()
