import os
from dotenv import load_dotenv
import requests
from django.core.management.base import BaseCommand
from foodbook_app.models import User, Restaurant, Friend_Request, Interaction_Details, Saved_Restaurants, Dine_Buddy
import json

load_dotenv()  # Load environment variables from .env file

class Command(BaseCommand):
    help = 'Fetch data from the external API and populate the database'

    def handle(self, *args, **kwargs):
        api_key = os.getenv('API_KEY')  
        if not api_key:
            raise ValueError("API key not found. Please set the API_KEY environment variable.")
        
        # Fetch basic restaurant data
        restaurant_data = self.fetch_restaurant(api_key)

        if restaurant_data:
            for restaurant in restaurant_data.get('businesses', []):
                self.process_restaurant(restaurant, api_key)
            self.stdout.write(self.style.SUCCESS('Successfully populated the database'))
        else:
            self.stdout.write(self.style.ERROR('No restaurant data found'))


    def fetch_restaurant(self, api_key):
        url = "https://api.yelp.com/v3/businesses/search"
        
        params = {
            "location": "Sydney 2121",
            "radius": 40000,  
            "sort_by": "best_match",
            "limit": 50
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "accept": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch restaurants: {str(e)}'))
            return None
    
    def process_restaurant(self, restaurant, api_key):
        RId = restaurant['id']
        try:
            restaurant_instance, created = Restaurant.objects.update_or_create(
                RId=RId,  
                defaults={
                    'name': restaurant['name'],
                    'address': ', '.join(restaurant['location'].get('display_address', [])),
                    'postal_code': restaurant['location'].get('zip_code', ''),
                    'cuisine': restaurant['categories'][0]['title'] if restaurant.get('categories') else '',
                    'yelp_rev_url': restaurant.get('url', ''),
                    'price': restaurant.get('price', ''),
                    'phone_number': restaurant.get('phone', ''),
                    'rating': restaurant.get('rating', 0),
                    'menu_url': restaurant.get('attributes', {}).get('menu_url', ''),
                    'longitude': restaurant['coordinates'].get('longitude', None) if restaurant.get('coordinates') else None,
                    'latitude': restaurant['coordinates'].get('latitude', None) if restaurant.get('coordinates') else None,
                }
            )

            # Fetch detailed information for each restaurant
            detailed_url = f"https://api.yelp.com/v3/businesses/{RId}"
            response_details = requests.get(detailed_url, headers={"Authorization": f"Bearer {api_key}"})
            response_details.raise_for_status()

            # Get the extra details for every restaurant
            self.update_restaurant_details(restaurant_instance, response_details.json())
        
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch details for restaurant ID {RId}: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred while processing restaurant ID {RId}: {str(e)}'))
    
    def update_restaurant_details(self, restaurant_instance, data):
        # Prepare the defaults dictionary with the updated values
        defaults = {
            'apple_pay': data.get('attributes', {}).get('business_accepts_apple_pay', False),
            'android_pay': data.get('attributes', {}).get('business_accepts_android_pay', False),
            'alcohol': data.get('attributes', {}).get('alcohol', None),
            'hipster': data.get('attributes', {}).get('ambience', {}).get('hipster', False),
            'casual': data.get('attributes', {}).get('ambience', {}).get('casual', False),
            'touristy': data.get('attributes', {}).get('ambience', {}).get('touristy', False),
            'trendy': data.get('attributes', {}).get('ambience', {}).get('trendy', False),
            'intimate': data.get('attributes', {}).get('ambience', {}).get('intimate', False),
            'romantic': data.get('attributes', {}).get('ambience', {}).get('romantic', False),
            'classy': data.get('attributes', {}).get('ambience', {}).get('classy', False),
            'upscale': data.get('attributes', {}).get('ambience', {}).get('upscale', False),
            'caters': data.get('attributes', {}).get('caters', False),
            'dogs_allowed': data.get('attributes', {}).get('dogs_allowed', False),
            'good_for_kids': data.get('attributes', {}).get('good_for_kids', False), # maybe remove this lol 
            'dessert': data.get('attributes', {}).get('good_for_meal', {}).get('dessert', False),
            'lunch': data.get('attributes', {}).get('good_for_meal', {}).get('lunch', False),
            'dinner': data.get('attributes', {}).get('good_for_meal', {}).get('dinner', False),
            'brunch': data.get('attributes', {}).get('good_for_meal', {}).get('brunch', False) if 'good_for_meal' in data.get('attributes', {}) else False,
            'breakfast': data.get('attributes', {}).get('good_for_meal', {}).get('breakfast', False),
            'delivery': data.get('attributes', {}).get('restaurants_delivery', False),
            'reservation': data.get('attributes', {}).get('restaurants_reservations', False),
            'vegan_friendly': data.get('attributes', {}).get('liked_by_vegans', False),
            'img_urls': data.get('photos', []), 
        }

        try:
            # Update or create the restaurant instance
            Restaurant.objects.update_or_create(
                RId=restaurant_instance.RId,  # Assuming RId is the unique identifier
                defaults=defaults
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to update restaurant details for {restaurant_instance.RId}: {str(e)}'))


