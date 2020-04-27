from flask import Flask

from . import models
from .extensions import *
from .scheme import schema

print(models)
from flask_graphql import GraphQLView

app = Flask(__name__)

app.config.update(
    {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///../example.db",
        "SQLALCHEMY_TRACK_MODIFICATIONS": True,
        "DEBUG": True,
    }
)
db.init_app(app)

# 视图
app.add_url_rule(
    "/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
)
