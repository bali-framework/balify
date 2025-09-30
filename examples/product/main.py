from datetime import datetime
from balify import O, o


class Product(O):
    title: str
    stock: int
    create_at: datetime
    updated_at: datetime


o.serve(Product)


# FIXME: Remove the expose app code
print("--> Expose App(%s)" % id(o._app))
app = o._app
