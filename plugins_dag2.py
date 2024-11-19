from airflow.plugins_manager import AirflowPlugin
from airflow.www.security import AirflowSecurityManager
from flask_appbuilder.security.sqla.models import User
from airflow.models import DagBag

class FolderBasedPermissionManager(AirflowSecurityManager):
    """
    Custom Security Manager to enforce folder-level DAG permissions.
    """
    def get_user_permissions(self, user: User):
        """
        Dynamically assigns DAG-level permissions based on folder names.
        """
        # Load all DAGs in the environment
        dag_bag = DagBag()
        all_dags = dag_bag.dags

        user_permissions = {}
        for dag_id, dag in all_dags.items():
            # Extract the folder name from the DAG's file path
            folder_name = dag.fileloc.split("/dags/")[1].split("/")[0]

            # Assign permissions based on the folder name
            if folder_name == "b2b" and user.role.name == "b2b_viewer":
                user_permissions[dag_id] = {"can_read": True, "can_edit": False}
            elif folder_name == "b2c" and user.role.name == "b2c_viewer":
                user_permissions[dag_id] = {"can_read": True, "can_edit": False}
            else:
                user_permissions[dag_id] = {"can_read": False, "can_edit": False}

        return user_permissions

class FolderPermissionPlugin(AirflowPlugin):
    """
    Plugin to register the FolderBasedPermissionManager.
    """
    name = "folder_permission_plugin"
    security_manager_class = FolderBasedPermissionManager


class FolderBasedPermissionManager(AirflowSecurityManager):
    """
    Custom Security Manager to enforce folder-level DAG permissions.
    """
    def get_user_permissions(self, user: User):
        """
        Dynamically assigns DAG-level permissions based on S3 folder paths.
        """
        dag_bag = DagBag()
        all_dags = dag_bag.dags

        user_permissions = {}
        for dag_id, dag in all_dags.items():
            # Adjust the parsing logic for S3
            # Example: Extract the folder name from the file location
            folder_name = dag.fileloc.split("/dags/")[1].split("/")[0]

            # Assign permissions based on folder
            if folder_name == "b2b" and user.role.name == "b2b_viewer":
                user_permissions[dag_id] = {"can_read": True, "can_edit": False}
            elif folder_name == "b2c" and user.role.name == "b2c_viewer":
                user_permissions[dag_id] = {"can_read": True, "can_edit": False}
            else:
                user_permissions[dag_id] = {"can_read": False, "can_edit": False}

        return user_permissions
