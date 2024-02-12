import os
import time
import boto3
import subprocess
import atexit
from .utils import check_local_port_availability, create_rdp_file


class EC2Client:
    def __init__(self, profile_name="for-sso"):
        self._profile_name = profile_name
        self.session = boto3.Session(profile_name=profile_name)
        self.client = self.session.client("ec2")
        self.ssm_client = self.session.client("ssm")
        self.sts_client = self.session.client("sts")
        self.email = None
        self.processes = []

    def get_logged_in_user_email(self):
        if not self.email:
            caller_identity = self.sts_client.get_caller_identity()
            arn = caller_identity.get("Arn", "")
            self.email = arn.split("/")[-1] if "/" in arn else "No email found"
        return self.email

    def get_ec2_instances_for_owner(self):
        if not self.email:
            self.get_logged_in_user_email()
        instances = self.client.describe_instances(
            Filters=[{"Name": "tag:Owner", "Values": [self.email]}]
        )
        return instances

    def check_sso_session_validity(self):
        try:
            self.client.describe_instances()
            return True
        except Exception as e:
            print(f"SSO session check failed: {e}")
            return False

    def toggle_ec2_instance_state(self, instance_id):
        try:
            instance = self.client.describe_instances(InstanceIds=[instance_id])
            state = instance["Reservations"][0]["Instances"][0]["State"]["Name"]
            if state == "running":
                self.client.stop_instances(InstanceIds=[instance_id])
                return f"Instance {instance_id} is stopping."
            elif state == "stopped":
                self.client.start_instances(InstanceIds=[instance_id])
                return f"Instance {instance_id} is starting."
            else:
                return f"Instance {instance_id} is in {state} state. No action taken."
        except Exception as e:
            return f"Error toggling instance state: {e}"

    def check_instance_session_manager_connection(self, instance_id):
        try:
            response = self.ssm_client.describe_instance_information(
                Filters=[
                    {"Key": "InstanceIds", "Values": [instance_id]},
                ]
            )
            instance_info = response.get("InstanceInformationList", [])
            if instance_info:
                ping_status = instance_info[0].get("PingStatus")
                if ping_status == "Online":
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            print(
                f"Error checking Session Manager connection for instance {instance_id}: {e}"
            )
            return False

    def initiate_rdp_connection(self, instance_id, instance_name):
        """
        Initiates an RDP connection to an EC2 instance.

        This method first attempts to create a port forwarding session for the specified EC2 instance.
        If successful, it then creates an RDP file configured to connect to the instance via the forwarded port
        and returns the file path to the RDP connection file.
        The instance name is sanitized to replace spaces with underscores for the RDP file name.

        :param instance_id: The ID of the EC2 instance to connect to.
        :param instance_name: The name of the EC2 instance, used for naming the RDP file.
        :return: A tuple containing 'localhost', the local port number, the process ID, and the RDP file path if successful, otherwise (None, None, None, None).
        """
        local_port, process_id = self._create_port_forwarding_session(instance_id)
        if local_port:
            sanitized_instance_name = instance_name.replace(" ", "_")
            rdp_file_path = create_rdp_file(
                instance_id, local_port, f"{sanitized_instance_name}.rdp"
            )
            return "localhost", local_port, process_id, rdp_file_path
        return None, None, None, None

    def _create_port_forwarding_session(self, instance_id, starting_local_port=33891):
        local_port = starting_local_port
        while not check_local_port_availability(local_port):
            local_port += 1
        try:
            command = (
                f"aws ssm start-session --target {instance_id} "
                f"--document-name AWS-StartPortForwardingSession "
                f"--parameters 'localPortNumber={local_port},portNumber=3389' "
                f"--profile {self._profile_name}"
            )
            process = subprocess.Popen(command, shell=True)
            self.processes.append(process)
            atexit.register(self._kill_process, process)
            print(
                f"Port forwarding session started on local port {local_port} with process ID {process.pid}"
            )
            return local_port, process.pid
        except Exception as e:
            print(f"Failed to start port forwarding session: {e}")
            return None, None

    def _kill_process(self, process):
        try:
            process.terminate()
            time.sleep(2)  # Wait for a little while before rechecking
            if process.poll() is None:  # Process has not terminated yet
                process.kill()
                print(f"Process {process.pid} forcefully terminated.")
            else:
                print(f"Process {process.pid} terminated successfully.")
            self._kill_session_manager_plugin()
        except Exception as e:
            print(f"Failed to terminate process {process.pid}: {e}")

    def _kill_session_manager_plugin(self):
        if os.name == "nt":  # For Windows
            soft_kill_command = "taskkill /im session-manager-plugin.exe"
            check_command = "tasklist | findstr session-manager-plugin.exe"
            force_kill_command = "taskkill /f /im session-manager-plugin.exe"
        else:  # For Unix-like OS
            soft_kill_command = "pkill session-manager-plugin"
            check_command = "pgrep session-manager-plugin"
            force_kill_command = "pkill -9 session-manager-plugin"
        try:
            subprocess.run(soft_kill_command, shell=True, check=True)
            time.sleep(2)  # Wait for a little while before rechecking
            check_process = subprocess.run(
                check_command, shell=True, stdout=subprocess.PIPE
            )
            if check_process.stdout:
                subprocess.run(force_kill_command, shell=True, check=True)
                print("Session Manager Plugin processes terminated forcefully.")
            else:
                print("Session Manager Plugin processes terminated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to terminate Session Manager Plugin processes: {e}")
