from django.db import models
from django.conf import settings

class Hotel(models.Model):
    name = models.TextField(blank=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE
    )

class Comment(models.Model):
    content = models.TextField(blank=True)
    hotel = models.ForeignKey(
        'hotels.hotel',
        related_name="comments",
        on_delete=models.CASCADE
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE
    )
