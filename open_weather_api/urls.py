from django.urls import path
from .views import WeatherDataView, ProgressView

urlpatterns = [
    path('collect/', WeatherDataView.as_view(), name='collect_weather_data'),
    path('progress/<str:user_defined_id>/', ProgressView.as_view(), name='progress_percentage'),
]
