import subprocess
import webbrowser
import re
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QApplication,
    QTextEdit,
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor


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


class LoginScreen(QDialog):
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
        self.loginWorker = LoginWorker()
        self.loginWorker.output_signal.connect(self.onLoginOutput)
        self.loginWorker.finished_signal.connect(self.onLoginFinished)
        self.loginWorker.start()
        self.buttonLogin.hide()  # Hide the login button immediately after starting the login process

    def onLoginOutput(self, output):
        self.outputTextEdit.moveCursor(QTextCursor.MoveOperation.End)
        self.outputTextEdit.insertPlainText(output)
        url_match = re.search(r"https://device.sso.[a-z0-9-]+.amazonaws.com/", output)
        code_match = re.search(r"code: (\S+)", output)
        if url_match and code_match:
            QApplication.clipboard().setText(
                f"{url_match.group(0)}\nCode: {code_match.group(1)}"
            )
            webbrowser.open(url_match.group(0))  # Automatically open the browser

    def onLoginFinished(self, retcode):
        if retcode == 0:  # Check if the login process finished successfully
            self.continueButton = QPushButton(
                "Continue", self
            )  # Create a continue button
            self.layout().addWidget(self.continueButton)
            self.continueButton.clicked.connect(
                self.accept
            )  # Connect the continue button to accept the dialog
