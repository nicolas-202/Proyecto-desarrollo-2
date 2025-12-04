from django.db import models


# Create your models here.
class PrizeType(models.Model):
    prize_type_name = models.CharField(max_length=50, unique=True)
    prize_type_code = models.CharField(max_length=4, unique=True)
    prize_type_description = models.TextField(blank=True, null=True)
    prize_type_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.prize_type_name


class StateRaffle(models.Model):
    state_raffle_name = models.CharField(max_length=50, unique=True)
    state_raffle_code = models.CharField(max_length=4, unique=True)
    state_raffle_description = models.TextField(blank=True, null=True)
    state_raffle_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.state_raffle_name
