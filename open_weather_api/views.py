import datetime as dt
import json
import time

import grequests
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from more_itertools import chunked
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .models import WeatherData
from .swagger_schemas import post_request, post_response, get_response

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
            ).first()
            if not user_defined_object:
                user_defined_object = WeatherData.objects.create(
                    user_defined_id=user_defined_id,
                    request_datetime=request_datetime,
                    city_info={"cities_info": []}
                )
            user_defined_object.city_info["cities_info"].extend(responses)
            user_defined_object.save() 
            yield ",".join(json.dumps(response) for response in responses)
            time.sleep(max(0, diff_to_11_seconds))
        yield "]}"

    @swagger_auto_schema(request_body=post_request(), responses={200: post_response()})
    def post(self, request):
        if request.method == "POST":
            req = json.loads(request.body)
            user_defined_id = req.get("user_defined_id")
            if not user_defined_id:
                return JsonResponse({"Error": "User ID not provided"}, status=400)
            check_user_exists = WeatherData.objects.filter(user_defined_id=user_defined_id).first()
            if check_user_exists:
                return JsonResponse({"Error": "User ID already exists"}, status=400)
            request_datetime = dt.datetime.now()
            city_data = []
            cities_urls = (
                URL.format(city_id=city_id, API_KEY=API_KEY) for city_id in CITIES_IDS
            )
            # Using StreamingHttpResponse to avoid timeout
            response = StreamingHttpResponse(
                self.call_weather_api(user_defined_id, request_datetime, cities_urls),
                status=200,
                content_type="text/event-stream",
            )
            response["Cache-Control"] = "no-cache"

            return response
        else:
            return JsonResponse({"Error": "Method not allowed."}, status=400)


class ProgressView(APIView):
    @swagger_auto_schema(operation_description="Endpoint to check the progress of the POST operation", responses={200: get_response()})
    def get(self, request, user_defined_id):
        user_defined_id_info = WeatherData.objects.filter(
            user_defined_id=user_defined_id
        ).first()
        if not user_defined_id_info:
            return JsonResponse({
                "user_defined_id": user_defined_id,    
                "Status": "User ID not found.",
            },
            status=status.HTTP_404_NOT_FOUND
            )
        user_defined_id_progress = len(
            user_defined_id_info.city_info["cities_info"]
        ) / len(CITIES_IDS)
        return JsonResponse({
            "user_defined_id": user_defined_id,
            "Status": f"{round(user_defined_id_progress*100,2)}%"
        })
