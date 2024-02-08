from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QListWidget


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
