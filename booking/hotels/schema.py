import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id

from .models import Hotel, Comment, Reservation
from users.schema import UserType


class HotelType(DjangoObjectType):
    class Meta:
        model = Hotel
        filter_fields = ['name']
        interfaces = (graphene.relay.Node, )


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        filter_fields = ['hotel']
        interfaces = (graphene.relay.Node, )


class ReservationType(DjangoObjectType):
    class Meta:
        model = Reservation
        filter_fields = ['hotel', 'user']
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    hotel = graphene.relay.Node.Field(HotelType)
    hotels = DjangoFilterConnectionField(HotelType)

    comment = graphene.relay.Node.Field(CommentType)
    comments = DjangoFilterConnectionField(CommentType)

    reservation = graphene.relay.Node.Field(ReservationType)
    reservations = DjangoFilterConnectionField(ReservationType)


class ReservationInput(graphene.InputObjectType):
    hotel_id = graphene.ID(required=True)
    start_date = graphene.types.datetime.Date(required=True)
    end_date = graphene.types.datetime.Date(required=True)

class CreateReservation(graphene.Mutation):
    reservation = graphene.Field(ReservationType)

    class Arguments:
        input = graphene.Argument(ReservationInput, required=True)

    def mutate(self, info, input):
        db_hotel_id = from_global_id(input.get('hotel_id'))[1]
        user = info.context.user or None
        hotel = Hotel.objects.get(pk=db_hotel_id)

        if not user or user.is_anonymous:
            raise Exception('You must be logged to delete a hotel!')

        if not hotel:
            raise Exception('Hotel does not exist!')

        reservation = Reservation(
            user=user,
            hotel=hotel,
            start_date=input.get('start_date'),
            end_date=input.get('end_date')
        )

        return CreateReservation(reservation=reservation)


class HotelInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    location = graphene.String(required=True)
    description = graphene.String(required=True)
    room_count = graphene.Int(required=True)


class CreateHotel(graphene.Mutation):
    hotel = graphene.Field(HotelType)

    class Arguments:
        input = graphene.Argument(HotelInput, required=True)

    def mutate(self, info, input):
        user = info.context.user or None

        if user.is_anonymous:
            raise Exception('You must be logged to add a hotel!')

        hotel = Hotel(
            name=input.get('name'),
            location=input.get('location'),
            description=input.get('description'),
            room_count=input.get('room_count'),
            posted_by=user
        )
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
    create_reservation = CreateReservation.Field()
