from airflow.plugins_manager import AirflowPlugin
from airflow.security import permissions
from airflow.models import DagBag
from airflow.www.security import AirflowSecurityManager
from flask_appbuilder.security.sqla.models import Role
from flask_appbuilder import expose
import boto3

class FolderPermissionPlugin(AirflowPlugin):
    name = "folder_permission_plugin"

    def __init__(self):
        self.s3_bucket = "your-bucket-name"  # Replace with your S3 bucket name
        self.role_folder_mapping = {
            "b2b": "b2b_viewer",
            "b2c": "viewer",
        }

    def get_dag_folders_from_s3(self):
        """
        Fetch DAG folders from S3 bucket.
        """
        s3_client = boto3.client("s3")
        response = s3_client.list_objects_v2(Bucket=self.s3_bucket, Prefix="dags/")
        folders = set()

        for obj in response.get("Contents", []):
            key = obj["Key"]
            folder = key.split("/")[1]  # Extract folder name
            if folder:
                folders.add(folder)

        return folders

    def assign_permissions(self):
        """
        Assign folder-based permissions to Airflow roles dynamically.
        """
        dag_bag = DagBag()
        folders = self.get_dag_folders_from_s3()

        for folder in folders:
            role_name = self.role_folder_mapping.get(folder)
            if role_name:
                # Get or create role
                role = self.get_or_create_role(role_name)
                for dag_id in dag_bag.dag_ids:
                    if dag_id.startswith(folder):
                        self.add_dag_permission(role, dag_id)

    def get_or_create_role(self, role_name):
        """
        Get or create an Airflow role.
        """
        security_manager = AirflowSecurityManager()
        role = security_manager.find_role(role_name)
        if not role:
            role = security_manager.create_role(role_name)
        return role

    def add_dag_permission(self, role, dag_id):
        """
        Add DAG-level permissions to a role.
        """
        security_manager = AirflowSecurityManager()
        permission_read = security_manager.find_permission_view_menu(permissions.ACTION_CAN_READ, dag_id)
        permission_edit = security_manager.find_permission_view_menu(permissions.ACTION_CAN_EDIT, dag_id)

        if permission_read and permission_read not in role.permissions:
            security_manager.add_permission_to_role(role, permission_read)

        if permission_edit and permission_edit not in role.permissions:
            security_manager.add_permission_to_role(role, permission_edit)
