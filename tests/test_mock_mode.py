"""Test script to verify mock mode for local development."""

import logging

from shared.helper_db import db_select_user_from_geheimnis

logging.basicConfig(level=logging.INFO)


def test_login_with_mock_credentials() -> None:
    user_id, username = db_select_user_from_geheimnis("test")
    assert user_id == 1
    assert username == "Torben"


def test_login_with_wrong_password() -> None:
    user_id, username = db_select_user_from_geheimnis("wrong_password")
    assert user_id == 0
    assert username == ""
