![publish](https://github.com/goodking-bq/graphene-sqlalchemy-auto/workflows/Upload%20Python%20Package/badge.svg)


generate default graphene schema from sqlalchemy model base on [graphene-sqlalchemy](https://github.com/graphql-python/graphene-sqlalchemy.git)

# Installation

just run
```shell script
pip install graphene_sqlalchemy_auto
```
# Features

- auto add `offset` `limit` `totalCount` to pagination
- auto add `dbId` for model's database id
- mutation auto return ok for success,message for more information and output for model data


# How To Use
example :
```python
from graphene_sqlalchemy_auto import QueryObjectType,MutationObjectType
from sqlalchemy.ext.declarative import declarative_base
import graphene
from sqlalchemy.orm import sessionmaker

Base = declarative_base() 
Session = sessionmaker()

class Query(QueryObjectType):
    class Meta:
        declarative_base = Base
        exclude_models = ["User"] # exclude models

class Mutation(MutationObjectType):
    class Meta:
        declarative_base = Base
        session=Session() # mutate used
        
        include_object = []# you can use yourself mutation UserCreateMutation, UserUpdateMutation


schema = graphene.Schema(query=Query, mutation=Mutation)

```

about many-to-many mutation

>now you can use schema everywhere.some like flask,fastapi

>also more example you can find in [example](https://github.com/goodking-bq/graphene-sqlalchemy-auto/tree/master/example)