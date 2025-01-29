from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.conf import settings  # to reference the CustomUser model
from rest_framework_api_key.models import APIKey
from django.core.exceptions import ValidationError


# These are the models as discussed from the schema

def validate_image(file):
    valid_mime_types = ['image/jpeg', 'image/png']
    file_mime_type = file.file.content_type
    if file_mime_type not in valid_mime_types: # checks the image's file type
        raise ValidationError("Only .jpeg and .png files are allowed to be uploaded.")
    
    if file.size > 2 * 1024 * 1024: # checks the image's size 
        raise ValidationError("The file must be under 2MB.")

class User(AbstractUser):
    # The fields in AbstractUser include username, password, and email by default.
    UId = models.AutoField(primary_key=True)  # User ID
    # username = models.CharField(max_length=50)  # Custom field for name
    city = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)  # Admin flag
    # friends = models.ManyToManyField('self', blank=True)  # Self-referencing many-to-many field for friends
    friends = models.ManyToManyField(
        'self',
        blank=True,
        related_name='friends_list',
        symmetrical=False
    )
    postal_code = models.CharField(
        max_length=4,
        validators=[RegexValidator(r'^\d{4}$', 'Postcode must be 4 digits.')]
    )    
    # previously_interacted_posts = models.ManyToManyField('Restaurant', related_name='interacted_users', blank=True)
    previously_interacted_posts = models.ManyToManyField(
        'Restaurant',
        related_name='interacted_users',
        blank=True
    )
    profile_pic = models.ImageField(upload_to="profile_pics/", null=True, validators=[validate_image])
    
    def __str__(self):
        return self.username
    
    def get_friends(self):
        """Returns a list of user's friends"""
        return self.friends.all()
    


class Restaurant(models.Model):
    RId = models.CharField(max_length=255, primary_key=True)  # Yelp's restaurant ID as a string
    name = models.CharField(max_length=200)
    img_urls = models.TextField(blank=True, default='', null=True)  # Comma-separated URLs
    yelp_rev_url = models.CharField(max_length=500, null=True)
    price = models.CharField(max_length=6, null=True) # This is the $$$ symbols (max 5)
    phone_number = models.CharField(max_length=20, null=True) # With spaces its usually ~15
    rating = models.FloatField(max_length=6, null=True) # 6 just in case?
    address = models.TextField(max_length=250, null=True)
    menu_url = models.TextField(max_length=250, null=True) # Sometimes None
    longitude = models.FloatField( # A requirement for the other endpoints
        validators=[MinValueValidator(-180), MaxValueValidator(180)], null=True
    ) 
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)], null=True
    ) 
    postal_code = models.CharField(
        max_length=4,
        validators=[RegexValidator(r'^\d{4}$', 'Postcode must be 4 digits.')]
    )      
    apple_pay = models.BooleanField(default=False)
    andriod_pay = models.BooleanField(default=False)
    alcohol = models.CharField(max_length=100, null=True)
    hipster = models.BooleanField(default=False, null=True)
    casual = models.BooleanField(default=False, null=True)
    touristy = models.BooleanField(default=False, null=True)
    trendy = models.BooleanField(default=False, null=True)
    intimate = models.BooleanField(default=False, null=True)
    romantic = models.BooleanField(default=False, null=True)
    classy = models.BooleanField(default=False, null=True)
    upscale = models.BooleanField(default=False, null=True)
    caters = models.BooleanField(default=False, null=True)
    dogs_allowed = models.BooleanField(default=False, null=True)
    good_for_kids = models.BooleanField(default=False, null=True)
    dessert = models.BooleanField(default=False, null=True)
    lunch = models.BooleanField(default=False, null=True)
    dinner = models.BooleanField(default=False, null=True)
    brunch = models.BooleanField(default=False, null=True)
    breakfast = models.BooleanField(default=False, null=True)
    delivery = models.BooleanField(default=False, null=True)
    reservation = models.BooleanField(default=False, null=True)
    vegan_friendly = models.BooleanField(default=False, null=True)
    cuisine = models.CharField(max_length=100)

    def get_img_urls_list(self):
        # Strip single quotes and split by comma
        return [url.strip("[").strip("]").strip("'") for url in self.img_urls.split(',')] if self.img_urls else []
    
    def get_total_likes(self):
        return Interaction_Details.objects.filter(RID=self, is_like=True).count()

    def __str__(self):
        return self.name


class Friend_Request(models.Model):
    to_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='received_friend_requests', 
        on_delete=models.CASCADE
    )    
    from_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='sent_friend_requests', 
        on_delete=models.CASCADE
    )    
    status = models.CharField(max_length=10, choices=(('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')), default='pending')

    def __str__(self):
        return f"{self.from_user_id} -> {self.to_user_id} ({self.status})"

class Interaction_Details(models.Model): 
    RID = models.ForeignKey(
        'Restaurant', on_delete=models.CASCADE, related_name='interactions'
    )
    UID = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interactions'
    )
    is_like = models.BooleanField(null=True, default=None)  # Can be True (like), False (dislike), or None (no interaction)
    interaction_id = models.AutoField(primary_key=True)



    def __str__(self):
        if self.is_like is None:
            return f"{self.UID.username} has not interacted with {self.RID.name}"
        return f"{self.UID.username} {'liked' if self.is_like else 'disliked'} {self.RID.name}"
    

class Saved_Restaurants(models.Model):
    UID = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_restaurants'
    )
    RID = models.ForeignKey(
        'Restaurant', on_delete=models.CASCADE, related_name='saved_by_users'
    )
    # saved_at = models.DateTimeField(auto_now_add=True)  # Optionally, track when it was saved

    # To handle bookmarks and bookmarking!!
    is_bookmarked = models.BooleanField(null=True, default=None)

    def __str__(self):
        return f"{self.UID.username} saved {self.RID.name}"


class Dine_Buddy(models.Model):
    RID = models.ForeignKey(
        'Restaurant', on_delete=models.CASCADE, related_name='dine_buddies'
    )
    from_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dine_buddy_requests_sent'
    )
    to_user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dine_buddy_requests_received'
    )
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    date = models.DateTimeField(auto_now_add=True)  # When the request was sent
    message = models.TextField(blank=True, null=True)  # Optional message field

    def __str__(self):
        return f"Dine Buddy request from {self.from_user_id.username} to {self.to_user_id.username} for {self.RID.name}. Message : {self.message}"
    