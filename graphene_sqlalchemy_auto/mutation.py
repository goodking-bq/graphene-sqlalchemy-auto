# coding:utf-8
from __future__ import absolute_import, unicode_literals, annotations

from collections import OrderedDict

import graphene
from graphene.types.objecttype import ObjectTypeOptions
from graphql_relay.node.node import from_global_id
from sqlalchemy.exc import SQLAlchemyError

from .types import SQLAlchemyObjectTypes, SQLAlchemyInputObjectType

__author__ = "golden"
__date__ = "2019/8/2"


def input_to_dictionary(input):
    """Method to convert Graphene inputs into dictionary"""
    dictionary = {}
    for key in input:
        # Convert GraphQL global id to database id
        if input[key] is None:
            continue
        if key[-2:] == "id" and input[key] and not input[key].isdigit():
            input[key] = from_global_id(input[key])[1]
        if isinstance(input[key], (dict,)):
            input[key] = input_to_dictionary(input[key])
        dictionary[key] = input[key]
    return dictionary


class SQLAlchemyMutationOptions(ObjectTypeOptions):
    model = None  # type: Model
    create = False  # type: Boolean
    delete = False  # type: Boolean
    arguments = None  # type: Dict[str, Argument]
    output = None  # type: Type[ObjectType]
    resolver = None  # type: Callable
    session = None

class SQLAlchemyMutation(graphene.Mutation):
    @classmethod
    def __init_subclass_with_meta__(
            cls,
            model=None,
            session=None,
            create=False,
            delete=False,
            registry=None,
            arguments=None,
            only_fields=None,
            exclude_fields=None,
            **options
    ):
        if exclude_fields is None:
            exclude_fields = []
        if only_fields is None:
            only_fields = []
        meta = SQLAlchemyMutationOptions(cls)
        meta.create = create
        meta.model = model
        meta.delete = delete
        cls._session = session
        _out_name = "Edit"
        if meta.create is True:
            _out_name = "Create"
        if meta.delete is True:
            _out_name = "Delete"
        if arguments is None and not hasattr(cls, "Arguments"):
            arguments = {}
            # 不是创建
            if meta.create == False:
                arguments["id"] = graphene.ID(required=True)
            # 不是删除
            if meta.delete == False:
                input_meta = type(
                    "Meta",
                    (object,),
                    {"model": model, "exclude_fields": exclude_fields, "only_fields": only_fields},
                )
                input_type = type(
                    cls.__name__ + "Input", (SQLAlchemyInputObjectType,), {"Meta": input_meta}
                )

                arguments["input"] = graphene.Argument.mounted(input_type(required=True))
            else:
                _out_name = "Delete"
        cls.output = graphene.Field(lambda: SQLAlchemyObjectTypes().get(model), description="输出")
        cls.ok = graphene.Boolean(description="成功？")
        cls.message = graphene.String(description="更多信息")
        super(SQLAlchemyMutation, cls).__init_subclass_with_meta__(
            _meta=meta, arguments=arguments, **options
        )

    @classmethod
    def mutate(cls, self, info, **kwargs):
        kwargs = input_to_dictionary(kwargs)
        session = cls._session

        meta = cls._meta

        if meta.create:  # new data
            model = meta.model()
            session.add(model)
        else:  # update data
            model = session.query(meta.model).filter(meta.model.id == kwargs["id"]).first()
            if not model:
                return cls(output=None, ok=False, message="要操作的数据不存在")
        if meta.delete:  # delete data
            session.delete(model)
        else:

            def set_model_attributes(model, attrs):
                relationships = model.__mapper__.relationships
                for key, value in attrs.items():
                    if key in relationships:
                        if getattr(model, key) is None:
                            # instantiate class of the same type as the relationship target
                            setattr(model, key, relationships[key].mapper.entity)
                            set_model_attributes(getattr(model, key), value)
                        else:  # many to many
                            obj = relationships[key].mapper.entity
                            ids=[from_global_id(v)[1]  for v in value]
                            objects = session.query(obj).filter(obj.id.in_(ids)).all()
                            setattr(model, key, objects)
                    else:
                        setattr(model, key, value)

            set_model_attributes(model, kwargs["input"])
        try:
            session.commit()
        except SQLAlchemyError as e:
            return cls(output=None, ok=False, message="数据库操作报错：%s" % e.args[0])
        except Exception as e:
            return cls(output=None, ok=False, message="数据库操作报错：%s" % e.__str__())
        return cls(output=model, ok=True, message="操作成功")

    @classmethod
    def Field(cls, *args, **kwargs):
        return graphene.Field(
            cls._meta.output, args=cls._meta.arguments, resolver=cls._meta.resolver
        )


def model_create(model, session):
    name = "%sCreateMutation" % model.__name__
    meta = type("Meta", (object,), {"model": model, "create": True, "delete": False, "session": session})
    mutation = type(name, (SQLAlchemyMutation,), {"Meta": meta})
    return mutation


def model_update(model, session):
    name = "%sUpdateMutation" % model.__name__
    meta = type("Meta", (object,), {"model": model, "create": False, "delete": False, "session": session})
    mutation = type(name, (SQLAlchemyMutation,), {"Meta": meta})
    return mutation


def model_delete(model, session):
    name = "%sDeleteMutation" % model.__name__
    meta = type("Meta", (object,), {"model": model, "create": False, "delete": True, "session": session})
    mutation = type(name, (SQLAlchemyMutation,), {"Meta": meta})
    return mutation


class MutationObjectType(graphene.ObjectType):
    @classmethod
    def __init_subclass_with_meta__(cls, declarative_base, session, include_object=None, _meta=None, **options):
        if include_object is None:
            include_object = []
        if not _meta:
            _meta = ObjectTypeOptions(cls)
        fields = OrderedDict()
        include_object_names = list()
        for obj in include_object:
            action = "update"
            if obj._meta.create is True:
                action = "create"
            if obj._meta.delete is True:
                action = "delete"
            name = "%s%s" % (action, obj._meta.model.__name__)
            include_object_names.append(name)
            fields[name] = obj.Field()
        if not isinstance(declarative_base, list):
            declarative_base = [declarative_base]
        for base in declarative_base:  # declarative_base can be mutil
            for model in base.registry.mappers:
                model_obj = model.class_
                model_name = model_obj.__name__
                # if isinstance(model_obj, DefaultMeta):
                if "create%s" % model_name not in include_object_names:
                    fields.update({"create%s" % model_name: model_create(model_obj, session).Field()})
                if "update%s" % model_name not in include_object_names:
                    fields.update({"update%s" % model_name: model_update(model_obj, session).Field()})
                if "delete%s" % model_name not in include_object_names:
                    fields.update({"delete%s" % model_name: model_delete(model_obj, session).Field()})
        if _meta.fields:
            _meta.fields.update(fields)
        else:
            _meta.fields = fields
        return super(MutationObjectType, cls).__init_subclass_with_meta__(_meta=_meta, **options)
