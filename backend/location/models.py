from django.db import models

class Country(models.Model):
    country_name = models.CharField(max_length=50, unique=True)
    country_code = models.CharField(max_length=4, unique=True)
    country_description = models.TextField(blank=True, null=True)
    country_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.country_name

class State(models.Model):
    state_name = models.CharField(max_length=50)
    state_code = models.CharField(max_length=4)
    state_description = models.TextField(blank=True, null=True)
    state_country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    state_is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['state_name', 'state_country'],
                name='unique_state_per_country'
            )
        ]

    def __str__(self):
        return self.state_name
    
class City(models.Model):
    city_name = models.CharField(max_length=50)
    city_code = models.CharField(max_length=4)
    city_description = models.TextField(blank=True, null=True)
    city_state = models.ForeignKey(State, on_delete=models.RESTRICT)
    city_is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['city_name', 'city_state'],
                name='unique_city_per_state'
            )
        ]

    def __str__(self):
        return self.city_name