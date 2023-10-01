from drf_yasg import openapi

def post_request():
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_defined_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID defined by the user.'),
        },
        required=['user_defined_id']
    )

def post_response():
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_defined_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID defined by the user.'),
            'request_datetime': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Datetime of the request.'),
            'city_info': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'city_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the city.'),
                        'temperature': openapi.Schema(type=openapi.TYPE_NUMBER, description='Temperature of the city.'),
                        'humidity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Humidity of the city.')
                    },
                    required=['city_id', 'temperature', 'humidity']
                ),
                description='List of cities with weather data.'
            )
        },
        required=['user_defined_id', 'request_datetime', 'city_info']
    )
