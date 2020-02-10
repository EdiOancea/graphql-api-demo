from django.db import models
from django.conf import settings

from users.models import User

class Hotel(models.Model):
    name = models.TextField(blank=True)
    location = models.TextField(blank=True)
    description = models.TextField(blank=True)
    room_count = models.IntegerField(default=1)
    reservations = models.ManyToManyField(
        User,
        through='Reservation'
    )
    posted_by = models.ForeignKey(
        User,
        related_name="hotels",
        on_delete=models.CASCADE
    )

class Reservation(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

class Comment(models.Model):
    content = models.TextField(blank=True)
    hotel = models.ForeignKey(
        Hotel,
        related_name="comments",
        on_delete=models.CASCADE
    )
    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
