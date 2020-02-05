import graphene
import graphql_jwt

import hotels.schema
import users.schema
import auth.schema

class Query(
    hotels.schema.Query,
    users.schema.Query,
    graphene.ObjectType
):
    pass

class Mutation(
    hotels.schema.Mutation,
    users.schema.Mutation,
    auth.schema.Mutation,
    graphene.ObjectType
):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
