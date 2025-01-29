from django.contrib import admin
from .models import User, Restaurant, Friend_Request, Interaction_Details, Saved_Restaurants, Dine_Buddy
# Register your models here.

# To show on the admin control center.

admin.site.register(User)
admin.site.register(Restaurant)
admin.site.register(Friend_Request)
admin.site.register(Interaction_Details)
admin.site.register(Saved_Restaurants)
admin.site.register(Dine_Buddy)


# @admin.register(Restaurant)
# class RestaurantAdmin(admin.ModelAdmin):
#     list_display = ['name', 'cuisine', 'location'] 
#     search_fields = ['name', 'cuisine']  
#     list_filter = ['cuisine']