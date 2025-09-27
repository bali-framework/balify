from datetime import datetime
from balify import O, o


class User(O):
    name: str
    age: int
    email: str
    create_at: datetime
    # updated_at: datetime


o.serve(User)


# FIXME: Remove the expose app code
print("--> Expose App(%s)" % id(o._app))
app = o._app
