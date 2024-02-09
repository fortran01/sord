from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QMessageBox,
)
from PyQt6.QtCore import QTimer
from ..ec2 import EC2Client
import re


class Ec2Screen(QDialog):
    def __init__(self, parent=None):
        super(Ec2Screen, self).__init__(parent)
        self.setWindowTitle("EC2 Instances")
        self.setGeometry(100, 100, 600, 400)

        self.ec2_client = EC2Client()

        layout = QVBoxLayout()

        self.ec2ListWidget = QListWidget()
        self.populate_ec2_instances()
        layout.addWidget(self.ec2ListWidget)

        self.powerButton = QPushButton("Toggle Power", self)
        self.powerButton.clicked.connect(self.handlePowerToggle)
        layout.addWidget(self.powerButton)

        self.buttonRDP = QPushButton("Connect via RDP", self)
        self.buttonRDP.clicked.connect(self.handleRDP)
        layout.addWidget(self.buttonRDP)

        self.buttonRefresh = QPushButton("Refresh", self)
        self.buttonRefresh.clicked.connect(self.refresh_ec2_instances_and_reset_timer)
        layout.addWidget(self.buttonRefresh)

        self.setLayout(layout)

        self.refreshTimer = QTimer(self)
        self.refreshTimer.timeout.connect(self.refresh_ec2_instances_and_reset_timer)
        self.refreshTimer.start(10000)  # Refresh every 10 seconds

    def populate_ec2_instances(self):
        try:
            self.ec2ListWidget.clear()  # Clear the list before populating
            instances = self.ec2_client.get_ec2_instances_for_owner()
            for reservation in instances["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_id = instance["InstanceId"]
                    instance_name = next(
                        (
                            tag["Value"]
                            for tag in instance["Tags"]
                            if tag["Key"] == "Name"
                        ),
                        "No Name",
                    )
                    instance_state = instance["State"]["Name"]
                    display_text = f"{instance_name} ({instance_id}) - {instance_state}"
                    self.ec2ListWidget.addItem(display_text)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to populate EC2 instances: {e}. Please try again.",
            )

    def refresh_ec2_instances_and_reset_timer(self):
        try:
            self.populate_ec2_instances()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh EC2 instances: {e}. Please try again.",
            )

    def handleRDP(self):
        try:
            selectedInstance = self.ec2ListWidget.currentItem().text()
            print(f"Connecting to {selectedInstance} via RDP...")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to initiate RDP connection: {e}. Please try again.",
            )

    def handlePowerToggle(self):
        try:
            currentItemText = self.ec2ListWidget.currentItem().text()
            instanceIdPattern = r"i-\w+"
            match = re.search(instanceIdPattern, currentItemText)
            if match:
                selectedInstance = match.group()
                toggle_result = self.ec2_client.toggle_ec2_instance_state(
                    selectedInstance
                )
                QMessageBox.information(self, "Status", toggle_result)
                self.refresh_ec2_instances_and_reset_timer()  # Refresh immediately after toggling
        except AttributeError as e:
            QMessageBox.critical(
                self,  # Assuming 'self' is a QWidget, adjust as necessary
                "Error",
                f"An unexpected error occurred: {e}. Please try again.",
            )
