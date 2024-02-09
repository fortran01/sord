import subprocess
import webbrowser
import re
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QApplication,
    QTextEdit,
    QMessageBox,  # Added for error handling
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor
from ..ec2 import EC2Client  # Import EC2Client to use check_sso_session_validity


class LoginWorker(QThread):
    output_signal = pyqtSignal(
        str
    )  # Signal to emit the stdout of the login process incrementally
    finished_signal = pyqtSignal(
        int
    )  # Signal to emit the return code of the login process

    def run(self):
        try:
            process = subprocess.Popen(
                ["aws", "sso", "login", "--profile=for-sso"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            for line in process.stdout:
                self.output_signal.emit(line)
            process.stdout.close()
            retcode = process.wait()
            self.finished_signal.emit(retcode)
        except subprocess.CalledProcessError as e:
            self.output_signal.emit(f"SSO login failed: {e.output}")
        except Exception as e:
            self.output_signal.emit(f"An unexpected error occurred: {e}")


class LoginScreen(QWidget):
    accepted = pyqtSignal()  # Add this signal to indicate completion

    def __init__(self, parent=None):
        super(LoginScreen, self).__init__(parent)
        self.setWindowTitle("AWS SSO Login")
        self.setGeometry(
            100, 100, 500, 400
        )  # Adjusted size to make all text visible without scrolling

        layout = QVBoxLayout()

        self.infoLabel = QLabel("Click 'Login' to authenticate via AWS SSO", self)
        layout.addWidget(self.infoLabel)

        self.outputTextEdit = QTextEdit(
            self
        )  # Changed to QTextEdit to display real-time output
        self.outputTextEdit.setReadOnly(True)
        layout.addWidget(self.outputTextEdit)

        self.buttonLogin = QPushButton("Login", self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout.addWidget(self.buttonLogin)

        self.setLayout(layout)

    def handleLogin(self):
        try:
            ec2_client = EC2Client()
            if ec2_client.check_sso_session_validity():
                self.outputTextEdit.insertPlainText(
                    "Valid SSO session found. No need to login again.\n"
                )
                self.buttonLogin.setText("Continue")  # Change button text to "Continue"
                self.buttonLogin.clicked.disconnect()  # Disconnect the previous slot
                self.buttonLogin.clicked.connect(
                    self.emitAccepted
                )  # Connect to accept the dialog
            else:
                self.loginWorker = LoginWorker()
                self.loginWorker.output_signal.connect(self.onLoginOutput)
                self.loginWorker.finished_signal.connect(self.onLoginFinished)
                self.loginWorker.start()
                self.buttonLogin.hide()  # Hide the login button immediately after starting the login process
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred during login: {e}. Please try again.",
            )

    def onLoginOutput(self, output):
        try:
            self.outputTextEdit.moveCursor(QTextCursor.MoveOperation.End)
            self.outputTextEdit.insertPlainText(output)
            url_match = re.search(
                r"https://device.sso.[a-z0-9-]+.amazonaws.com/", output
            )
            code_match = re.search(r"code: (\S+)", output)
            if url_match and code_match:
                QApplication.clipboard().setText(
                    f"{url_match.group(0)}\nCode: {code_match.group(1)}"
                )
                webbrowser.open(url_match.group(0))  # Automatically open the browser
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred while processing login output: {e}. Please try again.",
            )

    def onLoginFinished(self, retcode):
        try:
            if retcode == 0:  # Check if the login process finished successfully
                self.accepted.emit()  # Emit accepted signal instead of self.accept()
                if not hasattr(
                    self, "continueButton"
                ):  # Check if the continue button does not exist
                    self.continueButton = QPushButton("Continue", self)
                    self.layout().addWidget(self.continueButton)
                    self.continueButton.clicked.connect(
                        self.emitAccepted
                    )  # Connect the continue button to a method that emits accepted
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred after login finished: {e}. Please try again.",
            )

    def emitAccepted(self):
        try:
            self.accepted.emit()  # Emit the accepted signal
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred while emitting the accepted signal: {e}. Please try again.",
            )
