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
        self.ec2ListWidget.clear()  # Clear the list before populating
        instances = self.ec2_client.get_ec2_instances_for_owner()
        for reservation in instances["Reservations"]:
            for instance in reservation["Instances"]:
                instance_id = instance["InstanceId"]
                instance_name = next(
                    (tag["Value"] for tag in instance["Tags"] if tag["Key"] == "Name"),
                    "No Name",
                )
                instance_state = instance["State"]["Name"]
                display_text = f"{instance_name} ({instance_id}) - {instance_state}"
                self.ec2ListWidget.addItem(display_text)

    def refresh_ec2_instances_and_reset_timer(self):
        self.populate_ec2_instances()

    def handleRDP(self):
        # Placeholder for RDP connection logic
        selectedInstance = self.ec2ListWidget.currentItem().text()
        print(f"Connecting to {selectedInstance} via RDP...")

    def handlePowerToggle(self):
        currentItemText = self.ec2ListWidget.currentItem().text()
        instanceIdPattern = r"i-\w+"
        match = re.search(instanceIdPattern, currentItemText)
        if match:
            selectedInstance = match.group()
            toggle_result = self.ec2_client.toggle_ec2_instance_state(selectedInstance)
            QMessageBox.information(self, "Status", toggle_result)
            self.refresh_ec2_instances_and_reset_timer()  # Refresh immediately after toggling
