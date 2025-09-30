from datetime import datetime
from balify import O, o, auth


class Product(O):
    title: str
    stock: int
    create_at: datetime
    updated_at: datetime


# # Serve `Product` without auth
# o.serve(Product)

# Serve `Product` with auth
o.serve(Product.depends(auth))


# FIXME: Remove the expose app code
print("--> Expose App(%s)" % id(o._app))
app = o._app
