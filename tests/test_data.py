from datetime import datetime

from balify import O


def test_data_define_should_as_orm():
    class User(O):
        name: str
        age: int
        email: str
        create_at: datetime
        updated_at: datetime
