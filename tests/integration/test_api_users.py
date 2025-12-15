import pytest
from unittest.mock import patch, MagicMock
from app.service.user_service import UserService

# ============================================================
# GET ALL USERS
# ============================================================

def test_get_all_users():
    users = [MagicMock(id=1), MagicMock(id=2)]
    with patch("app.domain.user_rules.get_users", return_value=users):
        result = UserService.get_all_users()
        assert result == users

# ============================================================
# GET USER BY ID
# ============================================================

def test_get_user_by_id_found():
    user = MagicMock(id=1)
    with patch("app.domain.user_rules.get_user_by_id", return_value=user):
        result = UserService.get_user_by_id(1)
        assert result == user

def test_get_user_by_id_not_found():
    with patch("app.domain.user_rules.get_user_by_id", return_value=None):
        result = UserService.get_user_by_id(999)
        assert result is None

# ============================================================
# AUTHORIZE USER
# ============================================================

def test_authorize_user_success():
    user = MagicMock()
    user.check_password.return_value = True
    with patch("app.domain.user_rules.get_user_by_username", return_value=user):
        result = UserService.authorize_user("testuser", "pass")
        assert result == user

def test_authorize_user_wrong_password():
    user = MagicMock()
    user.check_password.return_value = False
    with patch("app.domain.user_rules.get_user_by_username", return_value=user):
        result = UserService.authorize_user("testuser", "wrongpass")
        assert result is None

def test_authorize_user_not_found():
    with patch("app.domain.user_rules.get_user_by_username", return_value=None):
        result = UserService.authorize_user("nouser", "pass")
        assert result is None

# ============================================================
# REGISTRATION
# ============================================================

def test_registration_success():
    user = MagicMock()
    with patch("app.domain.user_rules.add_user", return_value=(user, None)):
        result = UserService.registration("nick", "email@test.com", "pass", "pass", "active", "user")
        assert result[0] == user
        assert result[1] is None

def test_registration_missing_fields():
    result = UserService.registration("", "email@test.com", "pass", "pass", "active", "user")
    assert result == (None, "Всі поля є обов'язковими")

# ============================================================
# DELETE USER
# ============================================================

def test_delete_user_success():
    with patch("app.domain.user_rules.delete_user", return_value=True):
        assert UserService.delete_user(1) is True

def test_delete_user_fail():
    with patch("app.domain.user_rules.delete_user", return_value=False):
        assert UserService.delete_user(999) is False

# ============================================================
# EDIT USER
# ============================================================

def test_edit_user_success():
    user = MagicMock()
    with patch("app.domain.user_rules.edit_user", return_value=(user, None)):
        result = UserService.edit_user(1, "nick", "email@test.com", "active", "user")
        assert result[0] == user

# ============================================================
# PASSWORD RESET REQUEST
# ============================================================

def test_request_password_reset_not_found():
    with patch("app.domain.user_rules.get_user_by_email", return_value=None):
        token, error = UserService.request_password_reset("missing@test.com")
        assert token is None
        assert "не знайдено" in error

def test_request_password_reset_success(monkeypatch):
    user = MagicMock()
    user.id = 1
    monkeypatch.setattr("app.domain.user_rules.get_user_by_email", lambda email: user)
    
    token, error = UserService.request_password_reset("user@test.com")
    assert token is not None
    assert error is None

# ============================================================
# RESET PASSWORD WITH TOKEN
# ============================================================

def test_reset_password_mismatch():
    result = UserService.reset_password_with_token("token", "pass1", "pass2")
    assert result == (False, "Паролі не співпадають")

def test_reset_password_invalid_token(monkeypatch):
    # Підмінюємо decode_token, щоб викликати помилку
    def fake_decode(token):
        raise Exception("Invalid")
    monkeypatch.setattr("app.service.user_service.decode_token", fake_decode)
    result = UserService.reset_password_with_token("token", "pass", "pass")
    assert "недійсний" in result[1]