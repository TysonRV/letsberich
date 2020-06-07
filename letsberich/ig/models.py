from django.db import models
from django.contrib.auth.models import User


class Position(models.Model):
    currencyCode = models.TextField(max_length=20)
    dealReference = models.TextField(max_length=20)
    epic = models.TextField(max_length=20)
    expiry = models.DateField(max_length=20)
    size = models.FloatField(max_length=20)
    stopLevel = models.FloatField(max_length=20)
    direction = models.TextField(max_length=20)
    guaranteedStop = models.FloatField(max_length=20)
    orderType = models.TextField(max_length=20)
    forceOpen = models.BooleanField(max_length=20)
    created_by = models.ForeignKey(User, related_name='positions', on_delete=models.CASCADE)


