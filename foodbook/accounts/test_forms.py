from django.test import TestCase
from accounts.forms import user_registration_form
from django.core.exceptions import ValidationError
from foodbook_app.models import User

class UserRegistrationFormTests(TestCase):

    def test_valid_registration_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'city': 'Sydney',
            'bio': 'This is a test user.',
            'postal_code': '2000'
        }
        form = user_registration_form(data=form_data)
        self.assertTrue(form.is_valid())


    def test_password_validation_fails(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': '123',  # Weak password
            'password2': '123',
            'city': 'Sydney',
            'bio': 'This is a test user.',
            'postal_code': '2000'
        }
        form = user_registration_form(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_missing_required_fields(self):
        form_data = {
            'username': '',
            'email': 'testuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        form = user_registration_form(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
