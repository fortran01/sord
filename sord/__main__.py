import sys
from PyQt6.QtWidgets import QApplication
from .ui.pre_check_screen import PreCheckScreen
from .ui.login_screen import LoginScreen
from .ui.ec2_screen import Ec2Screen


def main():
    app = QApplication(sys.argv)
    preCheck = PreCheckScreen()

    if preCheck.exec() == PreCheckScreen.DialogCode.Accepted:
        login = LoginScreen()
        if login.exec() == LoginScreen.DialogCode.Accepted:
            ec2Screen = Ec2Screen()
            ec2Screen.show()
            sys.exit(app.exec())


if __name__ == "__main__":
    sys.exit(main())
