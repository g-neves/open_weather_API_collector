from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from .views import WeatherDataView, ProgressView, kelvin_to_celsius
from .models import WeatherData
import json
from django.conf import settings
from django.utils import timezone


CITIES_IDS = settings.CITIES_IDS


class KelvinToCelsiusTestCase(TestCase):
    """
    Test case for the function converting Kelvin to Celsius.

    Args:
        TestCase (unittest.TestCase): Base test case from the unittest framework.
    """
    def test_kelvin_to_celsius(self):
        """Test the Kelvin to Celsius conversion."""
        # Test for absolute zero
        self.assertEqual(kelvin_to_celsius(0), -273.15)
        
        # Test for boiling point of water in Kelvin
        self.assertEqual(kelvin_to_celsius(373.15), 100)
        
        # Test for freezing point of water in Kelvin
        self.assertEqual(kelvin_to_celsius(273.15), 0)


class WeatherDataViewTestCase(TestCase):
    """
    Test case for the WeatherDataView.

    Args:
        TestCase (unittest.TestCase): Base test case from the unittest framework.
    """ 
    def setUp(self):
        """Setup for the WeatherDataView test case."""        
        self.factory = RequestFactory()

    @patch("open_weather_api.views.WeatherData.objects.filter")
    def test_call_weather_api(self, mock_filter):
        """
        Test for the call_weather_api method of WeatherDataView.

        Args:
            mock_filter (MagicMock): Mocked version of the filter method for WeatherData objects.
        """      
        # Create a mock QuerySet object
        mock_query_set = MagicMock()
        mock_query_set.first.return_value = None  # Indicates user doesn't exist in the database
        mock_filter.return_value = mock_query_set

        view = WeatherDataView()
        request = self.factory.post('/', data={'user_defined_id': 'some-id'}, content_type='application/json')
        response = view.post(request)
        self.assertEqual(response.status_code, 200)


    def test_build_payload(self):
        """Test for the build_payload method of WeatherDataView."""      
        view = WeatherDataView()
        mock_response = {
            "id": 123,
            "main": {
                "temp": 32,
                "humidity": 80
            }
        }
        expected_payload = {
            "city_id": 123,
            "temperature": -241.15,
            "humidity": 80
        }
        self.assertEqual(view.build_payload(mock_response), expected_payload)


    def test_non_post_request(self):
        """Test for handling non-POST requests in the WeatherDataView."""    
        view = WeatherDataView()
        request = self.factory.get('/')
        response = view.post(request)
        
        self.assertEqual(response.status_code, 400)
        response_content = json.loads(response.content)
        self.assertEqual(response_content, {"Error": "Method not allowed."})

    def test_missing_user_defined_id(self):
        """Test for handling requests with missing user-defined IDs in the WeatherDataView."""       
        view = WeatherDataView()
        request = self.factory.post('/', data={}, content_type='application/json')
        response = view.post(request)
        
        self.assertEqual(response.status_code, 400)
        response_content = json.loads(response.content)
        self.assertEqual(response_content, {"Error": "User ID not provided"})

    @patch.object(WeatherDataView, 'call_weather_api', side_effect=Exception("API Call failed"))
    def test_api_call_failure(self, mock_call_weather_api):
        """
        Test for handling API call failures in the WeatherDataView.

        Args:
            mock_call_weather_api (MagicMock): Mocked version of the call_weather_api method of WeatherDataView.
        """       
        view = WeatherDataView()
        request = self.factory.post('/', data={'user_defined_id': 'some-id'}, content_type='application/json')
        with self.assertRaises(Exception) as context:
            view.post(request)
        self.assertEqual(str(context.exception), "API Call failed")

    def test_valid_post_request(self):
        """Test for handling valid POST requests in the WeatherDataView."""      
        view = WeatherDataView()
        request = self.factory.post('/', data={'user_defined_id': 'some-id'}, content_type='application/json')
        response = view.post(request)
        self.assertEqual(response.status_code, 200)

    def test_invalid_json_body(self):
        """Test for handling requests with invalid JSON body in the WeatherDataView."""
        view = WeatherDataView()
        # The data here is not valid JSON
        request = self.factory.post('/', data="{ 'user_defined_id': 'some-id'", content_type='application/json')
        response = view.post(request)
        self.assertEqual(response.status_code, 400)
        response_content = json.loads(response.content)
        self.assertEqual(response_content, {"status": "error", "message": "Invalid JSON"})

    @patch('open_weather_api.views.WeatherData.objects.filter')
    def test_existing_user_id(self, mock_filter):
        """
        Test for handling requests with an already existing user ID in the WeatherDataView.

        Args:
            mock_filter (MagicMock): Mocked version of the filter method for WeatherData objects.
        """      
        # Mocking a return value that simulates user exists in the database
        mock_query_set = MagicMock()
        mock_query_set.first.return_value = MagicMock()
        mock_filter.return_value = mock_query_set

        view = WeatherDataView()
        request = self.factory.post('/', data={'user_defined_id': 'existing-id'}, content_type='application/json')
        response = view.post(request)
        
        self.assertEqual(response.status_code, 400)
        response_content = json.loads(response.content)
        self.assertEqual(response_content, {"Error": "User ID already exists"})

    @patch.object(WeatherDataView, 'call_weather_api', return_value=iter(["Part1", "Part2"]))
    def test_streaming_response_content(self, mock_call_weather_api):
        """
        Test for the streaming content of WeatherDataView response.

        Args:
            mock_call_weather_api (MagicMock): Mocked version of the call_weather_api method of WeatherDataView.
        """       
        view = WeatherDataView()
        request = self.factory.post('/', data={'user_defined_id': 'some-id'}, content_type='application/json')
        response = view.post(request)
        
        self.assertEqual(response.status_code, 200)
        response_content = b"".join([content for content in response.streaming_content])
        self.assertEqual(response_content, b"Part1Part2")

    def test_build_payload_missing_keys(self):
        """Test for the build_payload method when provided with incomplete data."""
      
        view = WeatherDataView()
        mock_response = {
            "id": 123,
            "main": {
                "humidity": 80
            }
        }
        with self.assertRaises(KeyError):
            view.build_payload(mock_response)

    def test_order_of_error_checks(self):
        """Test the order in which the WeatherDataView checks for errors."""
       
        view = WeatherDataView()
        # Sending a request with invalid JSON and missing 'user_defined_id'
        request = self.factory.post('/', data="{ 'user_defined_id': 'some-id'", content_type='application/json')
        response = view.post(request)
        self.assertEqual(response.status_code, 400)
        response_content = json.loads(response.content)
        self.assertEqual(response_content, {"status": "error", "message": "Invalid JSON"})

    @patch('open_weather_api.views.WeatherData.objects.filter', side_effect=Exception('DB Error'))
    def test_database_error(self, mock_filter):
        """
        Test for handling database errors in the WeatherDataView.

        Args:
            mock_filter (MagicMock): Mocked version of the filter method for WeatherData objects.
        """  
        view = WeatherDataView()
        request = self.factory.post('/', data={'user_defined_id': 'some-id'}, content_type='application/json')
        
        with self.assertRaises(Exception) as context:
            view.post(request)
        self.assertEqual(str(context.exception), "DB Error")
    

    @patch('open_weather_api.views.grequests.map')
    @patch('open_weather_api.views.WeatherData.objects.create')
    @patch('open_weather_api.views.WeatherData.objects.filter')
    def test_call_weather_api_with_exact_ten_urls(self, mock_filter, mock_create, mock_grequests_map):
        """
        Test the call_weather_api method when provided with exactly ten URLs.

        Args:
            mock_filter (MagicMock): Mocked version of the filter method for WeatherData objects.
            mock_create (MagicMock): Mocked version of the create method for WeatherData objects.
            mock_grequests_map (MagicMock): Mocked version of the map function in grequests.
        """      
        # Mock the grequests response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "main": {"temp": 300, "humidity": 80}, "some": "data"}
        mock_grequests_map.return_value = [mock_response] * 10

        # Mock the database response for `filter`
        mock_query_set = MagicMock()
        mock_weather_data = WeatherData()
        mock_weather_data.request_datetime = timezone.now() 
        mock_weather_data.city_info = {"cities_info": []}
        mock_query_set.first.return_value = mock_weather_data
        mock_filter.return_value = mock_query_set

        mock_create.return_value = mock_weather_data

        view = WeatherDataView()
        cities_urls = ["http://example.com"] * 10
        generator_response = view.call_weather_api('some-id', timezone.now(), cities_urls)  # Use timezone-aware datetime

        # Convert generator to list
        response_list = list(generator_response)

        # Check the starting and ending of the response
        self.assertIn('"user_defined_id": "some-id"', response_list[0])
        self.assertEqual(response_list[-1], "]}")

        # Ensure there were 10 city responses included
        city_data = ",".join(response_list[1:-1])
        self.assertEqual(city_data.count('{"city_id": 1, "temperature": 26.85, "humidity": 80}'), 10)



class ProgressViewTestCase(TestCase):
    """Test cases for the ProgressView."""   

    def setUp(self):
        """Set up the testing environment for ProgressView."""       
        self.factory = RequestFactory()
        self.view = ProgressView()

    @patch('open_weather_api.views.WeatherData.objects.filter')
    def test_user_id_not_found(self, mock_filter):
        """Test the response when a user ID is not found in the ProgressView."""
       
        mock_filter.return_value.first.return_value = None

        request = self.factory.get('/progress/some-id')
        response = self.view.get(request, 'some-id')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content), {
            "user_defined_id": "some-id",
            "Status": "User ID not found."
        })


    @patch('open_weather_api.views.WeatherData.objects.filter')
    def test_user_id_progress(self, mock_filter):
        """Test calculating and returning progress percentage for a valid user ID."""
       
        mock_user_data = WeatherData()
        mock_user_data.city_info = {"cities_info": [1, 2, 3]} 
        mock_filter.return_value.first.return_value = mock_user_data

        request = self.factory.get('/progress/some-id')
        response = self.view.get(request, 'some-id')

        expected_progress = round(len(mock_user_data.city_info["cities_info"]) / len(CITIES_IDS) * 100, 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            "user_defined_id": "some-id",
            "Status": f"{expected_progress}%",
        })

    @patch('open_weather_api.views.WeatherData.objects.filter')
    def test_user_id_progress_100_percent(self, mock_filter):
        """Test the response when progress for a user ID is 100%."""
       
        mock_user_data = WeatherData()
        mock_user_data.city_info = {"cities_info": list(CITIES_IDS)}
        mock_filter.return_value.first.return_value = mock_user_data

        request = self.factory.get('/progress/some-id')
        response = self.view.get(request, 'some-id')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            "user_defined_id": "some-id",
            "Status": "100.0%",
        })

    @patch('open_weather_api.views.WeatherData.objects.filter')
    def test_user_id_progress_0_percent(self, mock_filter):
        """Test the response when progress for a user ID is 0%."""
       
        mock_user_data = WeatherData()
        mock_user_data.city_info = {"cities_info": []}
        mock_filter.return_value.first.return_value = mock_user_data

        request = self.factory.get('/progress/some-id')
        response = self.view.get(request, 'some-id')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            "user_defined_id": "some-id",
            "Status": "0.0%",
        })