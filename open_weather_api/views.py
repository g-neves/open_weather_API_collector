# from gevent import monkey
# monkey.patch_all()

import datetime as dt
import json
import time

import grequests
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import condition
from more_itertools import chunked
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WeatherData

API_KEY = settings.OPEN_WEATHER_API_KEY
URL = "https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}"
CITIES_IDS = settings.CITIES_IDS


def to_celsius(temp):
    return round((-32 + temp) / 1.8, 2)


class WeatherDataView(APIView):
    def build_payload(self, response):
        return {
            "city_id": response["id"],
            "temperature": to_celsius(response["main"]["temp"]),
            "humidity": response["main"]["humidity"],
        }

    def call_weather_api(self, user_defined_id, request_datetime, cities_urls):
        yield f'{{"user_defined_id": {json.dumps(user_defined_id)}, "request_datetime": {json.dumps(str(request_datetime))}, "city_info": ['
        is_first = True
        for chunk in chunked(cities_urls, 10):
            if not is_first:
                yield ","
            is_first = False
            start_time = time.time()
            responses = grequests.map(grequests.get(u) for u in chunk)
            end_time = time.time()
            elapsed_time = end_time - start_time
            diff_to_11_seconds = 11 - elapsed_time
            responses = (response.json() for response in responses if response)
            responses = [self.build_payload(response) for response in responses]
            user_defined_object = WeatherData.objects.filter(
                user_defined_id=user_defined_id
            )
            yield ",".join(json.dumps(response) for response in responses)
            time.sleep(max(0, diff_to_11_seconds))
        yield "]}"

    def post(self, request):
        if request.method == "POST":
            req = json.loads(request.body)
            user_defined_id = req.get("user_defined_id")
            if not user_defined_id:
                return JsonResponse({"status": "error"})
            request_datetime = dt.datetime.now()
            city_data = []
            cities_urls = (
                URL.format(city_id=city_id, API_KEY=API_KEY) for city_id in CITIES_IDS
            )
            response = StreamingHttpResponse(
                self.call_weather_api(user_defined_id, request_datetime, cities_urls),
                status=200,
                content_type="text/event-stream",
            )
            response["Cache-Control"] = "no-cache"

            return response
        else:
            return JsonResponse({"status": "error"})


class ProgressView(APIView):
    def get(self, request, user_defined_id):
        # Handle the GET request to calculate and return progress percentage
        user_defined_id_info = WeatherData.objects.filter(
            user_defined_id=user_defined_id
        )
        user_defined_id_progress = len(
            user_defined_id_info.city_info["cities_info"]
        ) / len(CITIES_IDS)
        return JsonResponse({"Status": f"{round(user_defined_id_progress,2)}%"})
