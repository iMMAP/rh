from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate using their email and password.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticates a user based on the provided email and password.

        Args:
            request (HttpRequest): The current request object.
            email (str): The email of the user to authenticate.
            password (str): The password of the user to authenticate.

        Returns:
            User: The authenticated user if successful, None otherwise.
        """
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user

    def get_user(self, user_id):
        """
        Retrieves a user instance based on the user ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User: The user instance if found, None otherwise.
        """
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
