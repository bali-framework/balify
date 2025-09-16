from datetime import datetime

from balify import va


def test_data_define_should_as_orm():
    class User(va):
        name: str
        age: int
        email: str
        create_at: datetime
        updated_at: datetime
