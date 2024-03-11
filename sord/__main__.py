import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox
from sord.ui.pre_check_screen import PreCheckScreen
from sord.ui.login_screen import LoginScreen
from sord.ui.ec2_screen import Ec2Screen
from sord import __version__  # Import the version


class MainApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"AWS Utility - v{__version__}")  # Include the version in the window title
        self.setGeometry(100, 100, 500, 400)

        self.stack = QVBoxLayout()

        self.preCheckScreen = PreCheckScreen()
        self.loginScreen = LoginScreen()

        self.preCheckScreen.accepted.connect(self.showLoginScreen)
        self.loginScreen.accepted.connect(self.showEc2Screen)

        self.stack.addWidget(self.preCheckScreen)

        centralWidget = QWidget()
        centralWidget.setLayout(self.stack)
        self.setCentralWidget(centralWidget)

        self.preCheckScreen.startPreCheck()  # Add this line to start the precheck

    def showLoginScreen(self):
        self.preCheckScreen.setParent(None)
        self.stack.addWidget(self.loginScreen)

    def showEc2Screen(self):
        self.loginScreen.setParent(None)
        self.ec2Screen = Ec2Screen()
        self.stack.addWidget(self.ec2Screen)


def main():
    try:
        app = QApplication(sys.argv)
        mainWindow = MainApplicationWindow()
        mainWindow.show()
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(
            None,
            "Application Error",
            f"An error occurred: {str(e)}\n\nThe application will now exit.",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
