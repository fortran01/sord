from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton


class LoginScreen(QDialog):
    def __init__(self, parent=None):
        super(LoginScreen, self).__init__(parent)
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 200, 100)

        layout = QVBoxLayout()

        self.username = QLineEdit(self)
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QLineEdit(self)
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        self.buttonLogin = QPushButton("Login", self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout.addWidget(self.buttonLogin)

        self.setLayout(layout)

    def handleLogin(self):
        # Placeholder for login logic
        if self.username.text() == "user" and self.password.text() == "pass":
            self.accept()
        else:
            self.reject()
