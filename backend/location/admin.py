from django.contrib import admin

from .models import City, Country, State

# Register your models here.
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
