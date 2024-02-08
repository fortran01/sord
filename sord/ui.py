import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QListWidget,
)


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


class EC2ListScreen(QDialog):
    def __init__(self, parent=None):
        super(EC2ListScreen, self).__init__(parent)
        self.setWindowTitle("EC2 Instances")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.ec2ListWidget = QListWidget()
        # Placeholder for EC2 instances
        self.ec2ListWidget.addItem("EC2 Instance 1")
        self.ec2ListWidget.addItem("EC2 Instance 2")
        layout.addWidget(self.ec2ListWidget)

        self.buttonRDP = QPushButton("Connect via RDP", self)
        self.buttonRDP.clicked.connect(self.handleRDP)
        layout.addWidget(self.buttonRDP)

        self.setLayout(layout)

    def handleRDP(self):
        # Placeholder for RDP connection logic
        selectedInstance = self.ec2ListWidget.currentItem().text()
        print(f"Connecting to {selectedInstance} via RDP...")


def main():
    app = QApplication(sys.argv)
    login = LoginScreen()

    if login.exec() == QDialog.DialogCode.Accepted:
        ec2ListScreen = EC2ListScreen()
        ec2ListScreen.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
