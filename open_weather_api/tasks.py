from celery import shared_task
from open_weather_project.celery import app as celery_app

@shared_task(queue="get_city_info_queue")
def my_task():
    celery_app.send_task('get_city_info')
    pass
