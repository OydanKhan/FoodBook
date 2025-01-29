from django.urls import path, include
from . import views
from .views import UserListCreate, RestaurantListCreate, FriendRequestListCreate, InteractionDetailsListCreate, SavedRestaurantsListCreate, DineBuddyListCreate
from .views import profile_view, feed_view, friends_view, like_view, bookmark_view, dine_buddy_view, change_dine_invite_status, home_view, edit_restaurant, delete_restaurant, session_status

urlpatterns = [
    # External API views
    path('api/users/', UserListCreate.as_view(), name='user-list-create'),
    path('api/restaurants/', RestaurantListCreate.as_view(), name='restaurant-list-create'),
    path('api/friend-requests/', FriendRequestListCreate.as_view(), name='friend-request-list-create'),
    path('api/interactions/', InteractionDetailsListCreate.as_view(), name='interaction-list-create'),
    path('api/saved-restaurants/', SavedRestaurantsListCreate.as_view(), name='saved-restaurant-list-create'),
    path('api/dine-buddies/', DineBuddyListCreate.as_view(), name='dine-buddy-list-create'),

    # Regular views
    path('', home_view, name='home'),
    path('profile/', profile_view, name='profile'),
    path('feed/', feed_view, name='feed'),
    path('friends/', friends_view, name='friends'),
    path('add_friend/', views.add_friend, name='add_friend'),
    path('like/', like_view, name='like'),
    path('bookmark/', bookmark_view, name='bookmark'),
    path('dine-buddy/', dine_buddy_view, name='dine_buddy'),
    path('send-friend-request/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline-friend-request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('change-dine-invite-status/', views.change_dine_invite_status, name='change_dine_invite_status'),
    path('delete_friend/<int:friend_id>/', views.delete_friend, name='delete_friend'),
    path('friend/<int:friend_id>/', views.friend_profile, name='friend_profile'),
    path('saved/', views.saved_view, name="saved_view"),
    
    # admin URLs
    path('admin-dashboard/', views.admin_home_view, name='admin_home'),
    path('admin-dashboard/people/', views.admin_people_view, name='admin_people'),
    path('admin-dashboard/edit_user/<int:id>/', views.admin_edit_people_view, name='edit_user'),
    path('admin-dashboard/delete_user/<int:id>/', views.admin_delete_people_view, name='delete_user'),
    path('admin-dashboard/edit_restaurant/<str:RId>/', edit_restaurant, name='edit_restaurant'),
    path('admin-dashboard/delete_restaurant/<str:RId>/', views.delete_restaurant, name='restaurant_delete'),
    path('admin-dashboard/add_restaurant/', views.add_restaurant, name='add_restaurant'),
    
    path('session-status/', session_status, name='session_status'),
    path('accounts/', include('allauth.urls')),  # django-allauth routes
    
]
