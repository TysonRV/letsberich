from django.db import models
from django.contrib.auth.models import User


class Position(models.Model):
    currency_code = models.CharField(
        max_length=3,
        help_text="3 letter ID"
    )
    deal_reference = models.CharField(
        max_length=30,
        help_text="Reference: TestPOS11",
        blank=True,
    )
    direction = models.CharField(
        max_length=4,
        choices=(("BUY", "BUY"), ("SELL", "SELL")),
        default="BUY",
        help_text="BUY or SELL"
    )
    epic = models.CharField(
        max_length=30,
        help_text="Instrument epic identifier, i.e CS.D.BITCOIN.TODAY.IP"
    )
    expiry = models.CharField(
        max_length=10,
        help_text="Date in format dd-MM-yy or DFB"
    )
    force_open = models.BooleanField(default=True,)
    guaranteed_stop = models.BooleanField(default=False,)
    order_type = models.CharField(
        max_length=6,
        choices=(("LIMIT", "LIMIT"), ("MARKET", "MARKET"), ("QUOTE", "QUOTE")),
        default="MARKET"
    )
    size = models.FloatField(help_text="Deal size")
    stop_level = models.IntegerField(null=True, blank=True)

    created_by = models.ForeignKey(
        User, related_name='positions', on_delete=models.CASCADE
    )


class Autotrade(models.Model):
    status = models.CharField(
        max_length=7,
        help_text="This activates the Auto Trade tool",
        choices=(("ON", "TURN ON"), ("OFF", "TURN OFF"), ("STATUS", "STATUS")),
    )
