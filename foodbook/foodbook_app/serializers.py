# serializers.py
from rest_framework import serializers
from .models import User, Restaurant, Friend_Request, Interaction_Details, Saved_Restaurants, Dine_Buddy

# The serializers.py file is essential for managing how your data is represented in APIs. 
# It allows you to control how data from Django models is converted to formats like JSON for frontend consumption and vice versa, while also providing validation mechanisms.
# It's often used for handling API requests and responses


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # or specify fields 

# ModelSerializer: This is a shortcut for creating serializers tied directly to Django models. 
# It automatically generates fields based on the model structure.

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend_Request
        fields = '__all__'

class InteractionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction_Details
        fields = '__all__'

class SavedRestaurantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Saved_Restaurants
        fields = '__all__'

# The class Meta is a convenient way to define additional settings for models and serializers. 
# In models, it controls things like database table names and record ordering, while in serializers, it specifies how fields are included, excluded, or customized when transforming model data to or from formats like JSON.
class DineBuddySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dine_Buddy
        fields = '__all__'
