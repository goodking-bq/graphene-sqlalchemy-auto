
import graphene
from fastapi import FastAPI
from starlette.graphql import GraphQLApp

from graphene_sqlalchemy_auto import MutationObjectType, QueryObjectType
import models
from database import SessionLocal, engine, Base
import uvicorn
Base.metadata.create_all(bind=engine)

app = FastAPI()


class Query(QueryObjectType):
    class Meta:
        declarative_base = Base


class Mutation(MutationObjectType):
    class Meta:
        declarative_base = Base
        session = SessionLocal.session_factory()


schema = graphene.Schema(query=Query, mutation=Mutation)


app.add_route("/", GraphQLApp(schema=schema))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)
