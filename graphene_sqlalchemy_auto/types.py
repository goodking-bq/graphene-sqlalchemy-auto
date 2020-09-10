import graphene
import sqlalchemy
from graphene.types.utils import yank_fields_from_attrs
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy.converter import Dynamic
from graphene_sqlalchemy.registry import get_global_registry
from graphene_sqlalchemy.types import construct_fields

try:
    from graphene_sqlalchemy.converter import default_connection_field_factory
except:
    from graphene_sqlalchemy.types import default_connection_field_factory
finally:
    pass
class DatabaseId(graphene.Interface):
    """
    auto add database id as dbId
    """
    db_id = graphene.Int(description="real database id")


class SQLAlchemyInputObjectType(graphene.InputObjectType):
    """
    auto generate graphene input object types
    """

    @classmethod
    def __init_subclass_with_meta__(
            cls, model=None, registry=None, only_fields=None, exclude_fields=None, **options
    ):
        if exclude_fields is None:
            exclude_fields = []
        if only_fields is None:
            only_fields = []
        if not registry:
            registry = get_global_registry()
        auto_exclude = []
        foreign_keys = []
        # always pull ids out to a separate argument
        for col in sqlalchemy.inspect(model).columns:
            if col.foreign_keys:
                foreign_keys.append(col.name)
                continue
            if (col.primary_key and col.autoincrement) or (
                    isinstance(col.type, sqlalchemy.types.TIMESTAMP)
                    and col.server_default is not None
            ):
                auto_exclude.append(col.name)
        sqlalchemy_fields = yank_fields_from_attrs(
            construct_fields(
                obj_type=SQLAlchemyObjectTypes().get(model),
                model=model,
                registry=registry,
                only_fields=tuple(only_fields),
                exclude_fields=tuple(exclude_fields + auto_exclude),
                connection_field_factory=default_connection_field_factory,
                batching=True,
            ),
            _as=graphene.Field,
        )
        # Add all of the fields to the input type

        for key, value in sqlalchemy_fields.items():
            if not (isinstance(value, Dynamic) or hasattr(cls, key)):
                if key in foreign_keys:
                    value = graphene.ID(description="graphene global id")
                setattr(cls, key, value)
        for key, value in model.__mapper__.relationships.items():  # many to many input,you should input [dbIds]
            if isinstance(value.secondary, sqlalchemy.Table):
                value = graphene.List(graphene.ID)
                setattr(cls, key, value)
        super(SQLAlchemyInputObjectType, cls).__init_subclass_with_meta__(**options)


class SQLAlchemyObjectTypes(object):
    """
    manager SQLAlchemyObjectType
    because can't create multiple times
    is Singleton
    """

    all_types = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            orig = super(SQLAlchemyObjectTypes, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance

    def get(self, model):
        name = model.__name__ + "OutputType"
        if name in self.all_types:
            return self.all_types.get(name)
        else:
            if hasattr(model, "id") and not hasattr(model, "db_id"):
                model.db_id = model.id
            t = SQLAlchemyObjectType.create_type(
                name, model=model, interfaces=(graphene.relay.Node, DatabaseId)
            )
            self.all_types[name] = t
            return t
