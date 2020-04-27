generate default graphene schema from sqlalchemy model base on [graphene-sqlalchemy](https://github.com/graphql-python/graphene-sqlalchemy.git)

# Installation

just run
```shell script
pip install graphene_sqlalchemy_auto
```

# How To Use
example :
```python
from graphene_sqlalchemy_auto import QueryObjectType,MutationObjectType
from sqlalchemy.ext.declarative import declarative_base
import graphene

Base = declarative_base() 

class Query(QueryObjectType):
    class Meta:
        declarative_base = Base


class Mutation(MutationObjectType):
    class Meta:
        declarative_base = Base
        
        # include_object = [UserCreateMutation, UserUpdateMutation]


schema = graphene.Schema(query=Query, mutation=Mutation)

```
now you can use schema everywhere.some like flask,fastapi
also more example you can find in [example](https://github.com/goodking-bq/graphene-sqlalchemy-auto/tree/master/example)