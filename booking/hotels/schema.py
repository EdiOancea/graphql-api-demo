import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q
from .models import Hotel, Comment
from users.schema import UserType

class HotelType(DjangoObjectType):
    class Meta:
        model = Hotel

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment

class Query(graphene.ObjectType):
    hotels = graphene.List(
        HotelType,
        id=graphene.Int(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    comments = graphene.List(CommentType)

    def resolve_hotels(
        self,
        info,
        id=None,
        first=None,
        skip=None,
        **kwargs
    ):
        qs = Hotel.objects.all()

        if id:
            return qs.filter(id=id)

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]\

        return qs

    def resolve_comments(self, info, **kwargs):
        return Comment.objects.all()

class CreateHotel(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        name = graphene.String()

    def mutate(self, info, name):
        user = info.context.user or None

        hotel = Hotel(name=name, posted_by=user)
        hotel.save()

        return CreateHotel(
            id=hotel.id,
            name=hotel.name,
            posted_by=hotel.posted_by
        )

class CreateComment(graphene.Mutation):
    id = graphene.Int()
    content = graphene.String()
    hotel = graphene.Field(HotelType)
    posted_by = graphene.Field(UserType)

    class Arguments:
        content = graphene.String()
        hotel_id = graphene.Int()

    def mutate(self, info, content, hotel_id):
        user = info.context.user
        hotel = None

        if user.is_anonymous:
            raise Exception('You must be logged to vote!')

        try:
            hotel = Hotel.objects.get(pk=hotel_id)
        except:
            raise Exception("Invalid hotel")

        comment = Comment(
            content=content,
            hotel=hotel,
            posted_by=user
        )
        comment.save()

        return CreateComment(
            id=comment.id,
            content=comment.content,
            hotel=comment.hotel,
            posted_by=comment.posted_by
        )

class Mutation(graphene.ObjectType):
    create_hotel = CreateHotel.Field()
    create_comment = CreateComment.Field()
