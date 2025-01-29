from django import forms
from django.contrib.auth.forms import UserCreationForm
from foodbook_app.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re


class user_registration_form(UserCreationForm):
    usable_password = None
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'city', 'bio', 'postal_code']
        
    def __init__(self, *args, **kwargs):
        super(user_registration_form, self).__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # Check if the two password fields match
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "The two password fields must match!")
        return cleaned_data

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        try:
            # Validate password using Django's built-in validators
            validate_password(password)
        except ValidationError as e:
            # Add validation error messages to the form
            self.add_error('password1', e)
        return password

class SearchFilterForm(forms.Form):
    query = forms.CharField(required=False, label='Search by Name or Cuisine')
    postal_code = forms.CharField(required=False, label='Postal Code')
    liked_by = forms.CharField(required=False, label='Postal Code')
    price = forms.ChoiceField(
        choices=[
            ('', 'Any'),
            ('1', '$'),
            ('2', '$$'),
            ('3', '$$$'),
            ('4', '$$$$'),
        ],
        required=False,
        label='Price Range'
    )
    sort = forms.MultipleChoiceField(
        choices=[
            ('friends', 'Liked by Friends'),
            ('most_liked', 'Most Liked'),
            ('highest_rated', 'Highest Rated'),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Sort By'
    )
    
    def clean_query(self):
        query = self.cleaned_data.get('query')
        # the search query must only contain alphanumeric characters or spaces
        if query and not re.match(r'^[\w\s]+$', query):
            self.add_error('query', "Invalid input. Only alphanumeric characters and spaces are allowed.")
        return query

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        # the post code must be 4 digits exactly
        if postal_code and not re.match(r'^\d{4}$', postal_code):
            self.add_error('postal_code', "Post code must be 4 digits.")
        return postal_code

    def clean_liked_by(self):
        liked_by = self.cleaned_data.get('liked_by')
        # the liked_by field must only contain alphanumeric characters or spaces
        if liked_by and not re.match(r'^[\w\s]+$', liked_by):
            self.add_error('liked_by', "Invalid input. Only alphanumeric characters and spaces are allowed.")
        return liked_by

