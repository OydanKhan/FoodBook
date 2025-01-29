from django import forms
from django.contrib.auth.forms import UserCreationForm
from foodbook_app.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

class UserEditForm(forms.ModelForm):
    profile_pic = forms.ImageField(required=False, widget=forms.ClearableFileInput)
    class Meta:
        model = User
        fields = ['username', 'city', 'bio', 'postal_code', 'profile_pic']
        
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None


class EditProfileForm(forms.Form):
    username = forms.CharField(max_length=301)
    email = forms.EmailField()
    city = forms.CharField(max_length=20)
    bio = forms.CharField(max_length=2000)


    def save(self, user):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        city = self.cleaned_data["city"]
        bio = self.cleaned_data["bio"]

        
        current_user_id = user.UId
        print(current_user_id)
        
        user_instance = get_object_or_404(User, UId=current_user_id)
        user_instance.email = email
        user_instance.username = username
        user_instance.city = city 
        user_instance.bio = bio

        user_instance.save()

        print(f"user: {user_instance}")
        return user_instance

