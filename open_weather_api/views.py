from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from .models import WeatherData
from .serializers import WeatherDataSerializer
import json
from django.conf import settings
import requests
import datetime as dt



API_KEY = settings.OPEN_WEATHER_API_KEY
URL = "https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}"
CITIES_IDS = settings.CITIES_IDS

def to_celsius(temp):
    pass


class WeatherDataView(APIView):
    def post(self, request):
        request_datetime = dt.datetime.now()
        city_data = []
        # Handle the POST request here, making calls to Open Weather API and storing data
        for city_id in CITIES_IDS:
            response = requests.post(URL.format(city_id=city_id, API_KEY=API_KEY))
            response = response.json()
            city_data.append({
                'city_id': city_id,
                'temperature': to_celsius(response.json()['main']['temp']),
                'humidity': response.json()['main']['temp']
            })
            user_defined_id = request.POST['id']

        city_data_serializer = {
            'user_defined_id' : user_defined_id,
            'request_datetime' : request_datetime,
            'city_info' : {'cities_info': city_data}     
        }
        serializer = WeatherDataSerializer(data=city_data_serializer)

        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.error)

        return JsonResponse({"Status": "Created"}, status=200)

class ProgressView(APIView):
    def get(self, request, user_defined_id):
        # Handle the GET request to calculate and return progress percentage
        user_defined_id_info = WeatherData.objects.filter(user_defined_id=user_defined_id)        
        user_defined_id_progress = len(user_defined_id_info.city_info['cities_info'])/len(CITIES_IDS)
        return JsonResponse({'Status': f"{round(user_defined_id_progress,2)}%"})

