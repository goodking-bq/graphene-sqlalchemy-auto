from collections import OrderedDict

import graphene
from graphene.types.generic import GenericScalar
from graphene.types.objecttype import ObjectTypeOptions
from graphene_sqlalchemy import SQLAlchemyConnectionField
from graphene_sqlalchemy.types import sort_argument_for_object_type

from .filter import filter_query
from .types import SQLAlchemyObjectTypes


class CustomConnectionField(SQLAlchemyConnectionField):
    def __init__(self, connection, *args, **kwargs):
        """
        add default query
        filters
        limit
        offset
        """
        model = connection.Edge.node._type._meta.model
        if "filters" not in kwargs:
            kwargs.setdefault("filters", sort_argument_for_object_type(model))
        elif "filters" in kwargs and kwargs["filters"] is None:
            del kwargs["filters"]
        if "limit" not in kwargs:
            kwargs.setdefault("limit", sort_argument_for_object_type(model))
        elif "limit" in kwargs and kwargs["limit"] is None:
            del kwargs["limit"]
        if "offset" not in kwargs:
            kwargs.setdefault("offset", sort_argument_for_object_type(model))
        elif "offset" in kwargs and kwargs["offset"] is None:
            del kwargs["offset"]
        super(CustomConnectionField, self).__init__(connection, *args, **kwargs)

    @classmethod
    def get_query(cls, model, info, **args):
        query = super(CustomConnectionField, cls).get_query(model, info, **args)
        if args.get("filters"):
            query = filter_query(query, model, args["filters"])
        if "limit" in args:
            query = query.limit(args["limit"])
        if "offset" in args:
            query = query.offset(args["offset"])
        return query


class CustomConnection(graphene.relay.Connection):
    """
    CustomConnection

        default add total count for query list
    """

    class Meta:
        abstract = True

    total_count = graphene.Int()

    @staticmethod
    def resolve_total_count(root, info):
        return root.iterable.limit(None).offset(None).count()


def model_connection(model):
    connection = CustomConnection.create_type(
        model.__name__ + "Connection", node=SQLAlchemyObjectTypes().get(model)
    )
    return CustomConnectionField(
        connection,
        filters=GenericScalar(),
        limit=graphene.types.Int(),
        offset=graphene.types.Int(),
    )


# first lower
def decapitalize(s, upper_rest=False):
    return s[:1].lower() + (s[1:].upper() if upper_rest else s[1:])


class QueryObjectType(graphene.ObjectType):
    @classmethod
    def __init_subclass_with_meta__(
            cls, declarative_base, exclude_models=None, _meta=None, **options
    ):
        """
        :param declarative_base: sqlalchemy's base
        :param exclude_models: exclude models
        :param _meta:
        :param options:
        :return:
        """
        if exclude_models is None:
            exclude_models = []
        if not _meta:
            _meta = ObjectTypeOptions(cls)
        fields = OrderedDict()
        fields["node"] = graphene.relay.Node.Field()
        if not isinstance(declarative_base, list):
            declarative_base = [declarative_base]
        for base in declarative_base:  # declarative_base can be mutil
            for model in base.registry.mappers:
                model_obj = model.class_
                if model_obj.__name__ in exclude_models:
                    continue
                fields.update(
                    {
                        decapitalize(model_obj.__name__): graphene.relay.Node.Field(
                            SQLAlchemyObjectTypes().get(model_obj)
                        ),
                        "%s_list" % decapitalize(model_obj.__name__): model_connection(model_obj),
                    }
                )
        if _meta.fields:
            _meta.fields.update(fields)
        else:
            _meta.fields = fields
        return super(QueryObjectType, cls).__init_subclass_with_meta__(
            _meta=_meta, **options
        )
