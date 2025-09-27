import logging

from datetime import date, datetime  # Entity field type

import humps  # noqa
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from .resource import RouterGenerator
from .utils import pluralize

from .decorators import action

from sqlmodel import Field, SQLModel, Session, create_engine, select


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"


engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


class _OMeta(type):
    """Metaclass for `O` object

    Bind FastAPI instance to `O`

    TODO: Compare `Metaclass` and `__init_subclass__`, then choose one in for `_OMeta`
    """

    _app = FastAPI()

    def __new__(cls, *args, **kwargs):
        meta = super().__new__(cls, *args, **kwargs)

        meta._app = FastAPI()
        meta._app = add_pagination(cls._app)

        return meta

    @property
    def _endpoint(self):
        if self._o_endpoint:  # noqa
            endpoint = self._o_endpoint  # noqa
        else:
            # Generate endpoint from resource name
            name = self.__name__.replace("Resource", "")
            words = humps.decamelize(name).split("_")
            words[-1] = pluralize(words[-1])
            endpoint = "-".join(words)

        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        return endpoint

    def as_router(self):
        print("--> Generate routers in App(%s)" % id(self._app))
        return RouterGenerator(self)()


GREETERS = [{"name": "Josh"}]


class O(metaclass=_OMeta):
    """O is a proxy for model, schema, resource

    model is SQLAlchemy/SQLModel model
    schema is Pydantic model
    resource is Restful resource
    """

    schema = None  # the schema is SQLModel instance

    @classmethod
    def serve(cls, *entities) -> None:

        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/")
        def hello():
            return {"Hello": "World", "Powered by": "balify router"}

        cls._app.include_router(router, prefix="/router1")

        for entity in entities:
            print("--> Serve entity `%s` in App(%s)" % (str(entity), id(cls._app)))
            cls._app.include_router(entity.as_router(), prefix="/users")

        # Generate all SQLModel schemas to database
        create_db_and_tables()

    @action()
    def list(self):
        """Generic `list` method

        TODO: implement the pagination and filter expressions like `bali`

        User.query().filter(*get_filters_expr(User, **schema_in.filters))

        """
        with Session(engine) as session:
            statement = select(self.schema)
            targets = session.exec(statement).all()
            print("--> Generic list method get targets: %s" % targets)
            return targets

    @action()
    def get(self, pk=None):

        with Session(engine) as session:
            statement = select(self.schema).where(self.schema.id == pk)  # type: ignore
            target = session.exec(statement).first()

        return target

    @action()
    def create(self, schema_in):
        """Generic create method"""
        print("--> self if %s(type: %s)" % (self, type(self)))
        print("--> self.schema: %s" % self.schema)
        print("--> param schema_in: %s" % schema_in)
        # self.schema(**schema_in)  # type: ignore

        with Session(engine) as session:

            # # Option 1: Commit schema_in directly
            # # sqlalchemy.orm.exc.DetachedInstanceError:
            # # Instance <UserSQLModel at 0x7748e76918a0> is not bound to a Session;
            # # attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)
            # session.add(schema_in)

            # Option 2: Create New schema instance
            target = self.schema(**schema_in.model_dump())  # type: ignore
            session.add(target)
            session.commit()
            session.refresh(target)

            print("--> target: %s (type: %s)" % (target, type(target)))
            print("--> target.id: %d" % target.id)

        return target

    @action()
    def update(self, schema_in=None, pk=None):

        with Session(engine) as session:
            statement = select(self.schema).where(self.schema.id == pk)  # type: ignore
            target = session.exec(statement).first()

            for k, v in schema_in.model_dump().items():  # type: ignore
                if v is not None:
                    setattr(target, k, v)

            session.add(target)
            session.commit()
            session.refresh(target)

        return target

    @action()
    def delete(self, pk=None):
        with Session(engine) as session:
            statement = select(self.schema).where(self.schema.id == pk)  # type: ignore
            target = session.exec(statement).first()
            session.delete(target)
            session.commit()

        return {"result": True}


# I found that `O, o` in `from balify import O, o` look like an cute emontion.
# May be I can split the metaclass to uppercase `O` and lowercase `o`.
# Uppercase `O` for define entity, could be translate to model, schema and resource.
# Lowercase `o` for FastAPI instance, provide `serve` functionality.
#
# On the other hand, using both the uppercase O and the lowercase o helps developers
# form good coding style habits.
o = O
