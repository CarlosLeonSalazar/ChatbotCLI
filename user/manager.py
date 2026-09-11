from config.config import USERS_DIR


class UserManager:
    """Gestor de usuarios"""

    @staticmethod
    def get_users():
        """obtener listado de usuarios"""

        if not USERS_DIR.exists():
            return []

        return sorted([user.name for user in USERS_DIR.iterdir() if user.is_dir()])

    @staticmethod
    def user_exists(user_id):
        """Verifica si un usuario existe."""
        user_path = USERS_DIR / user_id

        return user_path.is_dir()

    @staticmethod
    def create_user(user_id):
        """Crea un nuevo usuario."""
        user_path = USERS_DIR / user_id

        if user_path.exists():
            return False

        try:
            user_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return False
