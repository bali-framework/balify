from datetime import datetime
from fastapi.testclient import TestClient
from starlette import status


def test_va_import():
    from balify import va  # noqa


def test_serve():
    from balify import va

    class User(va):
        name: str
        age: int
        email: str
        create_at: datetime
        updated_at: datetime

    va.serve(User)

    client = TestClient(va._application)

    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["items"] == []
