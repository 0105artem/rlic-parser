import pytest
from jose import jwt

from app import schemas
from app.config import settings


def test_create_user(client):
    res = client.post("/users/", json={"email": "test@user.com", "password": "qwerty"})
    assert res.status_code == 201

    # Validates if response from create_user func has all fields via its pydantic model (schemas.UserResponse)
    # If not, pydantic will throw an error
    new_user = schemas.UserResponse(**res.json())
    assert new_user.email == "test@user.com"


def test_login_user(client, create_user):
    # test_create_user(client)
    res = client.post("/login", data={"username": create_user["email"], "password": create_user["password"]})
    assert res.status_code == 200

    login_output = schemas.Token(**res.json())
    # Decode /login response output to check user_id
    payload = jwt.decode(login_output.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get("user_id") == create_user["id"]
    assert login_output.token_type == "bearer"


@pytest.mark.parametrize("email, password, status_code", [
    ("not_an_email", "qwerty", 403),
    ("wrong_email@gmail.com", "qwerty", 403)
])
def test_incorrect_login(create_user, client):
    res = client.post("/login", data={"username": create_user["email"], "password": "wrongPassword"})
    assert res.status_code == 403
