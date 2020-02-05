import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id

from .models import Hotel, Comment
from users.schema import UserType


class HotelType(DjangoObjectType):
    class Meta:
        model = Hotel
        filter_fields = ['name', 'posted_by']
        interfaces = (graphene.relay.Node, )


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        filter_fields = ['posted_by', 'hotel']
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    hotel = graphene.relay.Node.Field(HotelType)
    hotels = DjangoFilterConnectionField(HotelType)

    comment = graphene.relay.Node.Field(CommentType)
    comments = DjangoFilterConnectionField(CommentType)


class HotelInput(graphene.InputObjectType):
    name = graphene.String(required=True)


class CreateHotel(graphene.Mutation):
    hotel = graphene.Field(HotelType)

    class Arguments:
        input = graphene.Argument(HotelInput, required=True)

    def mutate(self, info, input):
        user = info.context.user or None

        if user.is_anonymous:
            raise Exception('You must be logged to add a hotel!')

        hotel = Hotel(name=input.get('name'), posted_by=user)
        hotel.save()

        return CreateHotel(hotel=hotel)


class DeleteHotel(graphene.relay.ClientIDMutation):
    ok = graphene.Boolean()

    class Input:
        id = graphene.ID(required=True)

    def mutate_and_get_payload(self, info, id):
        user = info.context.user or None

        if user.is_anonymous:
            raise Exception('You must be logged to delete a hotel!')

        Hotel.objects.get(pk=from_global_id(id)[1]).delete()

        return DeleteHotel(ok=True)


class CreateComment(graphene.Mutation):
    comment = graphene.Field(CommentType)

    class Arguments:
        content = graphene.String()
        hotel_id = graphene.Int()

    def mutate(self, info, content, hotel_id):
        user = info.context.user
        hotel = None

        if user.is_anonymous:
            raise Exception('You must be logged in to leave a comment!')

        try:
            hotel = Hotel.objects.get(pk=hotel_id)
        except:
            raise Exception("Invalid hotel")

        comment = Comment(content=content, hotel=hotel, posted_by=user)
        comment.save()

        return CreateComment(comment=comment)


class Mutation(graphene.ObjectType):
    create_hotel = CreateHotel.Field()
    delete_hotel = DeleteHotel.Field()
    create_comment = CreateComment.Field()
