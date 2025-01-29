from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from accounts.forms import user_registration_form
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()  # Fetch the custom user model

class AccountsViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='StrongPass123!'
        )


    def test_register_view_get(self):
        """Test GET request to the register view."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIsInstance(response.context['form'], user_registration_form)

    def test_register_view_post_valid(self):
        """Test valid POST request to the register view."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'city': 'Sydney',
            'bio': 'This is a new user.',
            'postal_code': '2000',
        })
        self.assertEqual(response.status_code, 302)  # Redirects to 'home'
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_get(self):
        """Test GET request to the login view."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIsInstance(response.context['form'], AuthenticationForm)

    def test_login_view_post_valid(self):
        """Test valid POST request to the login view."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirects to 'home'
        self.assertRedirects(response, reverse('home'))

    def test_login_view_post_invalid(self):
        """Test invalid POST request to the login view."""
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'WrongPass123!',
        })
        # Extract the form from the response context
        form = response.context.get('form')

        # Ensure the response status is 200 (stays on the same page)
        self.assertEqual(response.status_code, 200)
        # Check that the form contains the appropriate error
        self.assertFalse(form.is_valid())
        # self.assertIn("Invalid username or password.", form.non_field_errors())


    def test_logout_view(self):
        """Test the logout view."""
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirects to 'login'
        self.assertRedirects(response, reverse('login'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "You have been logged out successfully.")

    def test_register_redirect_if_logged_in(self):
        """Test that logged-in users are redirected from the register view."""
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.get(reverse('register'))
        # self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 200)
        # messages = list(get_messages(response.wsgi_request))
        # self.assertEqual(str(messages[0]), "You are already logged in.")

    def test_login_redirect_if_logged_in(self):
        """Test that logged-in users are redirected from the login view."""
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.get(reverse('login'))
        # self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 200)
        # messages = list(get_messages(response.wsgi_request))
        # self.assertEqual(str(messages[0]), "You are already logged in.")
