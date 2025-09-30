from django.db import models

# Create your models here.
class Pais(models.Model):
    country_name = models.CharField(max_length=50, unique=True)
    country_code = models.CharField(max_length=4, unique=True)
    country_description = models.TextField(blank=True, null=True)
    country_state = models.BooleanField(default=True)

    def __str__(self):
        return self.country_name