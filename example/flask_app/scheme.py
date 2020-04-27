import graphene

from graphene_sqlalchemy_auto import QueryObjectType, MutationObjectType
from .extensions import db


class Query(QueryObjectType):
    class Meta:
        declarative_base = db.Model


class Mutation(MutationObjectType):
    class Meta:
        declarative_base = db.Model
        session = db.session
    # include_object = [UserCreateMutation, UserUpdateMutation]


schema = graphene.Schema(query=Query, mutation=Mutation)
