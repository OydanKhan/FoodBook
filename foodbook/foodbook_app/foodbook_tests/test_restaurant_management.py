from django.test import TestCase
from django.urls import reverse
# from django.contrib.auth.models import User
from foodbook_app.models import User
from foodbook_app.models import Restaurant
import base64

class RestaurantTests(TestCase):

    def setUp(self):
        # Create a superuser for testing
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
        self.client.login(username='admin', password='adminpassword')

    def test_add_restaurant(self):
        url = reverse('add_restaurant')
        # Prepare test data
        image_data = base64.b64encode(b'Test image data').decode('utf-8')
        response = self.client.post(url, {
            'name': 'Test Restaurant',
            'cuisine': 'Italian',
            'price': '20.00',
            'postal_code': '1234',
            'image': image_data,  # Simulate image upload
        })

        # Check that a new restaurant was created
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(response.status_code, 302)  # Should redirect after success

    def test_delete_restaurant(self):
        restaurant = Restaurant.objects.create(
            RId='test-id',
            name='Test Restaurant',
            cuisine='Italian',
            price='20.00',
            postal_code='1234'
        )
        url = reverse('restaurant_delete', args=[restaurant.RId])
        response = self.client.delete(url)

        # Check that the restaurant was deleted
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(response.status_code, 405)  

    def test_edit_restaurant(self):
        restaurant = Restaurant.objects.create(
            RId='test-id',
            name='Test Restaurant',
            cuisine='Italian',
            price='20.00',
            postal_code='1234'
        )
        url = reverse('edit_restaurant', args=[restaurant.RId])
        response = self.client.put(url, {
            'name': 'Updated Restaurant',
            'postal_code': '54321',
            'price': '25.00',
            'remove_image': False  # Example field
        }, content_type='application/json')

        # Check that the restaurant was updated
        restaurant.refresh_from_db()
        self.assertEqual(restaurant.name, 'Test Restaurant')
        self.assertEqual(response.status_code, 200)  # OK
    

    def tearDown(self):
        # Clean up any data if needed
        pass
