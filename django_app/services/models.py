from django.contrib.postgres.fields import DecimalRangeField, JSONField
from django.db import models


class AirportsData(models.Model):
    aircraft_code = models.CharField(primary_key=True, max_length=3, unique=True)
    airport_name = JSONField(null=False)
    city = models.JSONField(null=False)
    coordinates = DecimalRangeField()
    timezone = models.TextField(null=False)

    class Meta:
        db_table = "airports_data"


class AircraftsData(models.Model):
    aircraft_code = models.CharField(primary_key=True, max_length=3, unique=True)
    model = JSONField(null=False)
    range = models.IntegerField(null=False)

    class Meta:
        db_table = 'aircrafts_data'
