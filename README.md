# Open Weather API Collector

## Overview

The Open Weather API Collector is a streamlined API designed to collect weather data from multiple cities and store the results. Leveraging the power of OpenWeatherMap's extensive data, this API provides a systematic way to aggregate city-specific weather conditions using an asynchronous architecture.

## Features

* **Bulk Data Collection**: Collect weather data for multiple cities in one go.
* **Real-Time Progress Monitoring**: Use the progress endpoint to monitor the collection status.
* **Interactive API Documentation**: Utilize Swagger and ReDoc for comprehensive and user-friendly API documentation.
* **Docker Support**: Easily set up and run the application using Docker.

## Instalation

### Prerequisites

* Docker and Docker Compose installed on your machine 

### Steps

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Rename the `.env_example` file to `.env` and insert your Open Weather API Key where indicated.
4. Build and run the application using Docker:
```docker compose up --build```

## API Documentation

### Swagger and ReDoc

For a visual and interactive documentation of the API, you can use Swagger and ReDoc. These tools provide insights into the endpoints, request-response structures, and more.

* **Swagger**: Access at **localhost:8000/swagger**
* **ReDoc**: Access at **localhost:8000/redoc**

## Endpoints Usage

### Collect Weather Data (POST)

Initiate the data collection process by specifying a **`user_defined_id`**. This ID can be any number or string you'd like to associate with the data collection request.

```
curl --request POST \
  --url http://localhost:8000/collect/ \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: insomnia/8.1.0' \
  --data '{
        "user_defined_id": 1
}' -N
```

Replace **`1`** with your desired **`user_defined_id`**.

### Monitor Collection Progress (GET)

Monitor the progress of a previously initiated data collection process using its **`user_defined_id`**.

```
curl -L --request GET \
  --url http://localhost:8000/progress/1 \
  --header 'User-Agent: insomnia/8.1.0'
```

Replace **`1`** with the corresponding **`user_defined_id`** you'd like to track.

## Testing 

Testing ensures the reliability and functionality of the application. The Open Weather API Collector uses Django's built-in testing tools for this purpose.

### Setting Up the Test Environment:

1. Navigate to the root directory of the Django project.
2. Activate your virtual environment (if you're using one).
3. Install the required testing packages:
```
pip install -r requirements.txt
```

### Running the Tests:

To execute all tests:
```
python manage.py test open_weather_api --settings=open_weather_project.test_settings [--verbosity=2]
```

For investigating the testing coverage, run the following command
```
coverage run --source=open_weather_api manage.py test open_weather_api --settings=open_weather_project.test_settings [--verbosity=2]
```
and then
```
coverage report
```

## Design Considerations and Commentaries

1. **Asynchronous Requests with **`grequests`**:** 
The project utilizes grequests to handle asynchronous calls to the predefined Open Weather API endpoints. This choice facilitates efficient data collection from multiple sources concurrently. However, the free tier of Open Weather API restricts requests to a maximum of 60 calls per minute. To adhere to this limitation and prevent potential over-requesting, I've introduced a deliberate delay using **`time.sleep()`** in the POST view. This ensures that the application never exceeds the API's request limits, even when dealing with multiple asynchronous calls. 

2. **Database Choice - SQLite:**
The current implementation of the project uses SQLite as the database solution. This choice was based on the project's specifications, which did not indicate a large user volume or heavy traffic that would necessitate a more scalable database solution. However, should the need arise in the future, transitioning to PostgreSQL is straightforward. The `docker-compose.yml` file is already set up to accommodate PostgreSQL. To switch, one would simply need to include the necessary libraries for PostgreSQL connectivity. The versatility in database selection provides scalability options for future demands.

3. **Utilizing `more-itertools`:** 
   The `more-itertools` library is a valuable addition to the Python standard itertools, offering a richer set of utilities. Within this project, its `chunked` function was specifically employed to efficiently partition the list of URLs into manageable chunks. This approach is especially beneficial when dealing with rate limits or when wanting to make batch requests to an API, ensuring optimal performance and resource management.

4. **Integration of `gunicorn`:** 
   The choice to use `gunicorn` as the application server was twofold:
   
   a) **Compatibility with `grequests`**: The `grequests` library operates on top of `gevent`, a coroutine-based Python networking library. Due to certain nuances in how `gevent` patches Python's standard libraries for asynchronous operations, running the Django application using the traditional `python manage.py runserver` command can lead to unexpected behaviors. `gunicorn` with the `gevent` worker type alleviates these issues, providing a stable environment for asynchronous operations.
   
   b) **Concurrency**: With `gunicorn`, the application can concurrently handle multiple incoming requests. This is particularly useful in scenarios where a long-running POST request is being processed, and there's a need to serve other GET requests simultaneously. This level of concurrency ensures responsive user experiences and efficient request handling.

5. **Integration of `whitenoise`:** 
   Due to the use of `gunicorn` and the bypass of Django's traditional development server (`runserver`), serving static files (like the assets for Swagger and Redoc documentation) requires an external tool. `whitenoise` was chosen for this purpose. It seamlessly integrates with Django and serves static files directly from `gunicorn`. This avoids the need for a separate static file server or CDN during development, and ensures that tools like Swagger and Redoc operate smoothly.

6. **Configuring the Open Weather API Key:**
For the application to interact with the Open Weather API, users must provide their own API Key. This key should be set in the `.env` file. An illustrative example of how to set up the `.env` file is provided in the `.env_example` file.


## Feedback and Contributions

I value your feedback and contributions! If you have any suggestions, issues, or enhancements for the Open Weather API Collector, please open an issue or submit a pull request.