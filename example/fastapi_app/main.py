
import graphene
from fastapi import FastAPI
from starlette.graphql import GraphQLApp

from graphene_sqlalchemy_auto import MutationObjectType, QueryObjectType
from . import models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Query(QueryObjectType):
    class Meta:
        declarative_base = models.Base


class Mutation(MutationObjectType):
    class Meta:
        declarative_base = models.Base
        session = SessionLocal()


schema = graphene.Schema(query=Query, mutation=Mutation)


app.add_route("/", GraphQLApp(schema=schema))
