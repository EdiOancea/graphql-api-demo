import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import User

class UserType(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = [email']
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    user = graphene.relay.Node.Field(UserType)
    users = DjangoFilterConnectionField(UserType)

    def resolve_me(self, info):
        user = info.context.user

        if user.is_anonymous:
            raise Exception("Not logged in")

        return user


class UserInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        input = graphene.Argument(UserInput, required=True)

    def mutate(self, info, input):
        user = User.objects.create_user(
            email=input.get('email'),
            password=input.get('password'),
            **input
        )

        return CreateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
