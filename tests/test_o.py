from datetime import datetime
from fastapi.testclient import TestClient
from starlette import status


def test_imports():
    from balify import O, o  # noqa


def test_serve():
    from balify import O, o

    class User(O):
        name: str
        age: int
        email: str
        create_at: datetime
        updated_at: datetime

    o.serve(User)

    client = TestClient(o._app)

    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["items"] == []
