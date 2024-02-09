import boto3


class EC2Client:
    def __init__(self, profile_name="for-sso"):
        self.session = boto3.Session(profile_name=profile_name)
        self.client = self.session.client("ec2")

    def get_logged_in_user_email(self):
        sts_client = self.session.client("sts")
        caller_identity = sts_client.get_caller_identity()
        arn = caller_identity.get("Arn", "")
        email = arn.split("/")[-1] if "/" in arn else "No email found"
        return email

    def get_ec2_instances_for_owner(self):
        email = self.get_logged_in_user_email()
        instances = self.client.describe_instances(
            Filters=[{"Name": "tag:Owner", "Values": [email]}]
        )
        return instances

    def check_sso_session_validity(self):
        try:
            ec2_client = self.session.client("ec2")
            ec2_client.describe_instances()
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
