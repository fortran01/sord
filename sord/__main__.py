import sys
from PyQt6.QtWidgets import QApplication
from .ui.pre_check_screen import PreCheckScreen
from .ui.login_screen import LoginScreen
from .ui.ec2_list_screen import EC2ListScreen


def main():
    app = QApplication(sys.argv)
    preCheck = PreCheckScreen()

    if preCheck.exec() == PreCheckScreen.DialogCode.Accepted:
        login = LoginScreen()
        if login.exec() == LoginScreen.DialogCode.Accepted:
            ec2ListScreen = EC2ListScreen()
            ec2ListScreen.show()
            sys.exit(app.exec())


if __name__ == "__main__":
    sys.exit(main())
