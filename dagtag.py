from airflow.plugins_manager import AirflowPlugin
from airflow.www.security import AirflowSecurityManager
from flask_appbuilder.security.sqla.models import User
from airflow.models.serialized_dag import SerializedDagModel


class TagBasedPermissionManager(AirflowSecurityManager):
    """
    Custom Security Manager to enforce tag-based DAG permissions.
    """

    def get_user_permissions(self, user: User):
        """
        Dynamically assigns permissions to DAGs based on tags and user role.
        """
        # Fetch all DAGs from the Airflow metadata database
        all_dags = SerializedDagModel.read_all_dags()  # Dynamically fetch DAGs

        user_permissions = {}

        for dag_id, dag in all_dags.items():
            # Get the tags for the DAG
            dag_tags = set(dag.get("tags", []))

            # Define role-based tag access rules
            if user.role.name == "b2b_viewer":
                allowed_tags = {"b2b"}  # Tags allowed for this role
            elif user.role.name == "b2c_viewer":
                allowed_tags = {"b2c"}  # Tags allowed for this role
            elif user.role.name in ["admin", "ops", "viewer"]:
                allowed_tags = dag_tags  # Full access for these roles
            else:
                allowed_tags = set()  # No access for other roles

            # Check if the user role has access to this DAG based on tags
            if dag_tags & allowed_tags:
                user_permissions[dag_id] = {"can_read": True, "can_edit": user.role.name != "viewer"}
            else:
                user_permissions[dag_id] = {"can_read": False, "can_edit": False}

        return user_permissions

    def has_access(self, permission_name, view_name, user: User):
        """
        Override the access check to dynamically filter DAGs based on tag permissions.
        """
        # Get user-specific permissions
        user_permissions = self.get_user_permissions(user)

        # Extract the DAG ID from the view name
        dag_id = view_name.split(".")[-1]  # View name often ends with the DAG ID

        # Check the user's permissions for the given DAG ID
        if dag_id in user_permissions:
            if permission_name == "can_read" and user_permissions[dag_id]["can_read"]:
                return True
            if permission_name == "can_edit" and user_permissions[dag_id]["can_edit"]:
                return True

        # Default: Deny access
        return False


class TagFilterPlugin(AirflowPlugin):
    """
    Plugin to register the TagBasedPermissionManager.
    """
    name = "tag_filter_plugin"
    security_manager_class = TagBasedPermissionManager
