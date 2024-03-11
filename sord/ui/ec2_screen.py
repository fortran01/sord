from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QMessageBox,
    QLabel,
    QDialogButtonBox,
    QAbstractItemView,  # Added import here
)
from PyQt6.QtCore import QTimer, Qt
from ..ec2 import EC2Client
import re
import os
import subprocess


class Ec2Screen(QDialog):
    def __init__(self, parent=None):
        super(Ec2Screen, self).__init__(parent)
        self.setWindowTitle("EC2 Instances")
        self.setGeometry(100, 100, 600, 400)

        self.ec2_client = EC2Client()

        layout = QVBoxLayout()

        self.labelSessionManagerConnected = QLabel("Session Manager Connected:")
        layout.addWidget(self.labelSessionManagerConnected)

        self.ec2ListWidgetSessionManagerConnected = QListWidget()
        self.ec2ListWidgetSessionManagerConnected.setObjectName(
            "ec2ListWidgetSessionManagerConnected"
        )
        self.ec2ListWidgetSessionManagerConnected.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        layout.addWidget(self.ec2ListWidgetSessionManagerConnected)

        self.labelSessionManagerNotConnected = QLabel("Session Manager Not Connected:")
        layout.addWidget(self.labelSessionManagerNotConnected)

        self.ec2ListWidgetSessionManagerNotConnected = QListWidget()
        self.ec2ListWidgetSessionManagerNotConnected.setObjectName(
            "ec2ListWidgetSessionManagerNotConnected"
        )
        self.ec2ListWidgetSessionManagerNotConnected.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        layout.addWidget(self.ec2ListWidgetSessionManagerNotConnected)

        self.populate_ec2_instances()

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

        self.ec2ListWidgetSessionManagerConnected.itemSelectionChanged.connect(
            lambda: self.clearOtherSelectionBasedOnItemSelection(
                self.ec2ListWidgetSessionManagerConnected,
                self.ec2ListWidgetSessionManagerNotConnected,
            )
        )
        self.ec2ListWidgetSessionManagerNotConnected.itemSelectionChanged.connect(
            lambda: self.clearOtherSelectionBasedOnItemSelection(
                self.ec2ListWidgetSessionManagerNotConnected,
                self.ec2ListWidgetSessionManagerConnected,
            )
        )
        self.updateRDPButtonState()  # Initially disable the RDP button if no instance is selected

    def clearOtherSelectionBasedOnItemSelection(self, sender, other):
        # If any item is selected in the sender widget, clear selection in the other widget
        if sender.selectedItems():
            print(f"Clearing selection in '{other.objectName()}' because '{sender.objectName()}' has selected items.")
            for index in range(other.count()):
                item = other.item(index)
                item.setSelected(False)
        self.updateRDPButtonState()

    def populate_ec2_instances(self):
        try:
            self.ec2ListWidgetSessionManagerConnected.clear()
            self.ec2ListWidgetSessionManagerNotConnected.clear()
            instances = self.ec2_client.get_ec2_instances_for_owner()
            first_instance_added = False
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
                    if self.ec2_client.check_instance_session_manager_connection(
                        instance_id
                    ):
                        self.ec2ListWidgetSessionManagerConnected.addItem(display_text)
                        if not first_instance_added:
                            self.ec2ListWidgetSessionManagerConnected.setCurrentRow(0)
                            first_instance_added = True
                    else:
                        self.ec2ListWidgetSessionManagerNotConnected.addItem(
                            display_text
                        )
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
            selectedInstance = (
                self.ec2ListWidgetSessionManagerConnected.currentItem()
                or self.ec2ListWidgetSessionManagerNotConnected.currentItem()
            )
            if selectedInstance is None:
                QMessageBox.critical(
                    self,
                    "Error",
                    "No EC2 Instance selected or the selected instance is not connected to Session Manager.",
                )
                return
            selectedInstanceText = selectedInstance.text()
            instanceIdPattern = r"i-\w+"
            match = re.search(instanceIdPattern, selectedInstanceText)
            if match:
                instance_id = match.group()
                instance_name = selectedInstanceText.split(" ")[
                    0
                ]  # Assuming the first word is the instance name
                (
                    host,
                    local_port,
                    process_id,
                    rdp_file_path,
                ) = self.ec2_client.initiate_rdp_connection(instance_id, instance_name)
                print(host, local_port, process_id, rdp_file_path)
                if host and local_port and rdp_file_path:
                    self.showRDPDialog(instance_id, host, local_port, rdp_file_path)
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to initiate RDP connection. Please check if the instance is connected and try again.",
                    )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "No valid instance selected for RDP connection.",
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to initiate RDP connection due to an error: {e}. Please ensure the instance is connected and try again.",
            )

    def showRDPDialog(self, instance_id, host, local_port, rdp_file_path):
        dialog = QDialog(self)
        dialog.setWindowTitle("RDP Connection Details")
        layout = QVBoxLayout()

        infoLabel = QLabel(
            f"Connect to {instance_id} via RDP using the following details:"
        )
        layout.addWidget(infoLabel)

        hostLabel = QLabel(f"Hostname: {host}")
        hostLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(hostLabel)

        portLabel = QLabel(f"Port: {local_port}")
        portLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(portLabel)

        rdpFileLinkLabel = QLabel(f"RDP File Path: {rdp_file_path}")
        rdpFileLinkLabel.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(rdpFileLinkLabel)

        openRDPButton = QPushButton("Open RDP File")
        openRDPButton.clicked.connect(lambda: self.openRDPFile(rdp_file_path))
        layout.addWidget(openRDPButton)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttonBox.accepted.connect(dialog.accept)
        layout.addWidget(buttonBox)

        dialog.setLayout(layout)
        dialog.exec()

    def openRDPFile(self, rdp_file_path):
        if os.path.exists(rdp_file_path):
            if os.name == "nt":  # Windows
                subprocess.Popen(["mstsc", rdp_file_path])
            else:  # macOS and Linux
                subprocess.run(["open", rdp_file_path], check=True)
        else:
            QMessageBox.critical(
                self,
                "Error",
                "RDP file does not exist. Please ensure it was created correctly.",
            )

    def handlePowerToggle(self):
        try:
            currentItemText = self.getCurrentItemText()
            instanceIdPattern = r"i-\w+"
            match = re.search(instanceIdPattern, currentItemText)
            if match:
                selectedInstance = match.group()
                print(f"Toggling power state for instance: {selectedInstance}")
                toggle_result = self.ec2_client.toggle_ec2_instance_state(
                    selectedInstance
                )
                QMessageBox.information(self, "Status", toggle_result)
                self.refresh_ec2_instances_and_reset_timer()  # Refresh immediately after toggling
        except AttributeError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred: {e}. Please try again.",
            )

    def getCurrentItemText(self):
        if self.ec2ListWidgetSessionManagerConnected.currentItem():
            return self.ec2ListWidgetSessionManagerConnected.currentItem().text()
        elif self.ec2ListWidgetSessionManagerNotConnected.currentItem():
            return self.ec2ListWidgetSessionManagerNotConnected.currentItem().text()
        else:
            raise AttributeError("No instance selected")

    def updateRDPButtonState(self):
        # Enable the RDP button if an instance under "Session Manager Connected" is selected,
        # and disable it if an instance under "Session Manager Not Connected" is selected
        isInstanceConnectedSelected = (
            len(self.ec2ListWidgetSessionManagerConnected.selectedItems()) > 0
        )
        isInstanceNotConnectedSelected = (
            len(self.ec2ListWidgetSessionManagerNotConnected.selectedItems()) > 0
        )
        self.buttonRDP.setEnabled(
            isInstanceConnectedSelected and not isInstanceNotConnectedSelected
        )
