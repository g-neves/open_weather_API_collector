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
3. Build and run the application using Docker:
```docker compose up --build```

## API Documentation

### Swagger and ReDoc

For a visual and interactive documentation of the API, you can use Swagger and ReDoc. These tools provide insights into the endpoints, request-response structures, and more.

* **Swagger**: Access at 
* **ReDoc**: Access at 

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
curl --request GET \
  --url http://localhost:8000/progress/1 \
  --header 'User-Agent: insomnia/8.1.0'
```

Replace **`1`** with the corresponding **`user_defined_id`** you'd like to track.