import pytest
from app.auth import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hashing():
    plain = "SuperSecret123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_generation_and_decoding():
    payload = {"sub": "12345678-1234-5678-1234-567812345678", "role": "admin"}
    token = create_access_token(payload)
    assert isinstance(token, str)
    assert len(token) > 20

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == payload["sub"]
    assert decoded["role"] == payload["role"]


def test_jwt_invalid_token():
    assert decode_access_token("invalid.token.here") is None
