from django.db import models


class WeatherData(models.Model):
    user_defined_id = models.CharField(max_length=100, unique=True, primary_key=True)
    request_datetime = models.DateTimeField()
    city_info = models.JSONField()

    def __str__(self):
        return self.user_defined_id
