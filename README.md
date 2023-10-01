# Open Weather API Collector


## Instalation

To build the application inside Docker, run the following command

```docker compose up --build```

## Calling the endpoints

* To call the POST endpoint, run the following command, substituting 1 by the desired user_defined_id.

```
curl --request POST \
  --url http://localhost:8000/collect/ \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: insomnia/8.1.0' \
  --data '{
        "user_defined_id": 1
}' -N
```

* To test the GET endpoint, run the following command, substituting 1 by the desired user_defined_id.

```
curl --request GET \
  --url http://localhost:8000/progress/1 \
  --header 'User-Agent: insomnia/8.1.0'
```