from user.manager import UserManager
import user.manager as user_manager


def test_get_users(tmp_path, monkeypatch):
    monkeypatch.setattr(user_manager, "USERS_DIR", tmp_path)

    (tmp_path / "carlos").mkdir()
    (tmp_path / "juan").mkdir()

    users = UserManager.get_users()

    assert users == ["carlos", "juan"]


def test_user_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(user_manager, "USERS_DIR", tmp_path)

    (tmp_path / "carlos").mkdir()

    assert UserManager.user_exists("carlos") is True
    assert UserManager.user_exists("juan") is False


def test_create_user(tmp_path, monkeypatch):
    monkeypatch.setattr(user_manager, "USERS_DIR", tmp_path)

    result = UserManager.create_user("carlos")

    assert result is True
    assert (tmp_path / "carlos").is_dir()


def test_create_existing_user(tmp_path, monkeypatch):
    monkeypatch.setattr(user_manager, "USERS_DIR", tmp_path)

    (tmp_path / "carlos").mkdir()

    result = UserManager.create_user("carlos")

    assert result is False
