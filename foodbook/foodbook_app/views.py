from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from jsonschema import ValidationError
from rest_framework import generics
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
from .models import User, Restaurant, Friend_Request, Interaction_Details, Saved_Restaurants, Dine_Buddy
from .serializers import UserSerializer, RestaurantSerializer, FriendRequestSerializer, InteractionDetailsSerializer, SavedRestaurantsSerializer, DineBuddySerializer
from django.contrib import messages
from .forms import EditProfileForm, UserEditForm
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.http import Http404
from django.db.models import Count
from django.db.models import Count, OuterRef, Subquery
import base64
import uuid
from .forms import UserEditForm
from django.utils.functional import SimpleLazyObject
import json
from django.views.decorators.csrf import csrf_exempt
import bleach

# this view handles the homepage of Foodbook
def home_view(request):
    current_user = request.user
    restaurants = Restaurant.objects.all()

    # Sorting Logic: show trending 
    likes_count_subquery = Interaction_Details.objects.filter(
        RID=OuterRef('pk'),  # Reference to the Restaurant's PK
        is_like=True
    ).values('RID').annotate(like_count=Count('RID')).values('like_count')

    restaurants = restaurants.annotate(likes_count=Subquery(likes_count_subquery)).order_by('-likes_count')
    paginator = Paginator(restaurants, 21)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    interaction_status = {}
    saved_status = {}
    friends = None

    # Get filter parameters
    postal_code = bleach.clean(request.GET.get('postal_code') or "")
    search = bleach.clean(request.GET.get('search') or "")
    liked_by = bleach.clean(request.GET.get('liked_by') or "")
    sort_options = request.GET.getlist('sort')

    if current_user.is_authenticated:
        # Get interaction details
        for restaurant in restaurants:
            interaction = Interaction_Details.objects.filter(RID=restaurant, UID=current_user).first()
            interaction_status[restaurant.RId] = interaction.is_like if interaction else None
        
        friends = current_user.friends.all()
        bookmarked_restaurants = Saved_Restaurants.objects.filter(UID=current_user, is_bookmarked=True).select_related('RID')
        for bookmark in bookmarked_restaurants:
            saved_status[bookmark.RID.RId] = True
    else:
        for restaurant in restaurants:
            interaction_status[restaurant.RId] = None

    
    # Filtering
    filtered_restaurants_queryset = restaurants
    price_filters = request.GET.getlist('price')  # Get the list of selected price values
    if price_filters:
        filtered_restaurants_queryset = filtered_restaurants_queryset.filter(price__in=price_filters)

    if postal_code:
        filtered_restaurants_queryset = filtered_restaurants_queryset.filter(postal_code=postal_code)

    if search:
        filtered_restaurants_queryset = filtered_restaurants_queryset.filter(
            Q(name__icontains=search) | Q(cuisine__icontains=search)
        )
    
    if liked_by:
        user = User.objects.filter(username=liked_by).first()
        if user:
            liked_by_user = Interaction_Details.objects.filter(UID=user, is_like=True).values_list('RID', flat=True)
            filtered_restaurants_queryset = filtered_restaurants_queryset.filter(RId__in=liked_by_user)

    # Sorting Logic
    sort_filters = request.GET.getlist('sort')  # Get the list of selected sort values
    if sort_filters:
        if 'friends' in sort_filters:
            # Apply your custom logic for sorting by friends
            filtered_restaurants_queryset = sorted(
                filtered_restaurants_queryset,
                key=lambda r: len(Interaction_Details.objects.filter(RID=r, is_like=True, UID__in=current_user.friends.all())),
                reverse=True
                )
        if 'most_liked' in sort_filters:
            likes_count_subquery = Interaction_Details.objects.filter(
                RID=OuterRef('pk'),  # This should be the correct reference to the Restaurant's PK
                is_like=True
            ).values('RID').annotate(like_count=Count('RID')).values('like_count')

            filtered_restaurants_queryset = filtered_restaurants_queryset.annotate(
                likes_count=Subquery(likes_count_subquery)
            ).order_by('-likes_count')


    # Pagination
    paginator = Paginator(filtered_restaurants_queryset, 21)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)


    return render(request, 'home.html', {
        'page_object': page_object,
        'interaction_status': interaction_status,
        'friends': friends,
        'saved_status': saved_status,
        'login_redirect': reverse("login"),
        'user': request.user,
    })


@login_required
def profile_view(request):
    current_user = request.user
    context = {}
    if request.method == 'POST':
        form = EditProfileForm(data=request.POST)
        # print(form.errors)
        if form.is_valid():
            username = bleach.clean(form.cleaned_data.get('username') or "")
            email = bleach.clean(form.cleaned_data.get('email') or "")
            city = bleach.clean(form.cleaned_data.get('city') or "")
            bio = bleach.clean(form.cleaned_data.get('bio') or "")

            user_instance = get_object_or_404(User, UId=current_user.UId)
            user_instance.username = username
            user_instance.email = email
            user_instance.city = city
            user_instance.bio = bio
            user_instance.save()

            messages.success(request, 'Profile changes have been successfully saved!')

            return redirect("profile")
            
    else:
        form = EditProfileForm(instance=current_user)

    if request.method == "GET":
        try:
            foodbook_user = get_object_or_404(User, username=request.user) #get Customer w/ current username
        except:
                print("Not user")

        liked_restaurants = Interaction_Details.objects.filter(UID=current_user, is_like=True).select_related('RID')
        disliked_restaurants = Interaction_Details.objects.filter(UID=current_user, is_like=False).select_related('RID')
        saved_restaurants = Saved_Restaurants.objects.filter(UID=current_user, is_bookmarked=True).select_related('RID')
        print('liked restaurants: ', liked_restaurants)
        print('disliked restaurants: ', disliked_restaurants)
        print('saved restaurants: ', saved_restaurants)
        context = {
            'user': current_user,
            'liked_restaurants': [interaction.RID for interaction in liked_restaurants],
            'disliked_restaurants': [interaction.RID for interaction in disliked_restaurants],
            'saved_restaurants': [saved.RID for saved in saved_restaurants],
            'login_redirect': reverse("login"),
        }

        return render(request, 'profile.html' , context)
    else:
        user = request.user

    
    return render(request, 'profile.html', context)

# this view manages the feed page (finds restaurants liked by current user's friends)
@login_required
def feed_view(request):
    current_user = request.user

    # Start with all restaurants
    restaurants = Restaurant.objects.all()
    liked_by_friends = {}  
    interaction_status = {}

    filtered_restaurants = []

    for restaurant in restaurants:
        # checks if any of the current user's friends have liked the restaurant
        friends_who_liked = Interaction_Details.objects.filter(
            RID=restaurant, is_like=True, UID__in=current_user.friends.all()
        ).select_related('UID')  

        interaction = Interaction_Details.objects.filter(RID=restaurant, UID=current_user).first()
        interaction_status[restaurant.RId] = interaction.is_like if interaction else None

        # if any friends have liked the restaurant, the restaurant is added to the filtered list for feed
        if friends_who_liked.exists():
            filtered_restaurants.append(restaurant)  
            # stores the list of friends who have liked the specific restaurant
            liked_by_friends[restaurant.RId] = list(friends_who_liked)

    filtered_restaurants_queryset = Restaurant.objects.filter(RId__in=[r.RId for r in filtered_restaurants])

    

    # Pagination of restaurants, 21 per page
    filtered_restaurants_queryset = filtered_restaurants_queryset.order_by('name') 
    paginator = Paginator(filtered_restaurants_queryset, 21)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    friends = current_user.friends.all() #Fetch the user's friends - needed for dine buddy
    print(f"friends of user: {friends}")
    

    return render(request, 'feed.html', {
        'page_object': page_object,
        'liked_by_friends': liked_by_friends,
        'interaction_status': interaction_status,
        'friends': friends,
        'login_redirect': reverse("login"),
        'user': request.user,
    })

@login_required
def friends_view(request):
    restaurants = Restaurant.objects.all()
    paginator = Paginator(restaurants, 21)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    current_user = request.user
    received_dine_buddies = Dine_Buddy.objects.filter(to_user_id=current_user)
    sent_dine_buddies = Dine_Buddy.objects.filter(from_user_id=current_user)

    friend_requests = Friend_Request.objects.filter(to_user_id=current_user)
    friends = current_user.friends.all()  # Fetch the user's friends

    return render(request, 'friends.html', {'page_object': page_object,
                                            'received_dine_buddies': received_dine_buddies,
                                            'sent_dine_buddies': sent_dine_buddies,
                                            'friend_requests': friend_requests,
                                            'friends': friends,
                                            })

@login_required
def add_friend(request):
    query = bleach.clean(request.GET.get('q') or "")  # Get the search query from the request
    results = None
    
    if query:  # Only perform search if there's a query
        results = User.objects.filter(username__icontains=query).exclude(UId=request.user.UId)  # Exclude the current user

    if request.method == "POST":
        friend_id = request.POST.get('friend_id')
        if friend_id:
            friend = User.objects.get(id=friend_UId)
            request.user.friends.add(friend)  # Add the friend
            return redirect('add_friend')  # Redirect to the same page after adding a friend

    return render(request, 'add_friend.html', {'results': results})


@login_required
def send_friend_request(request):
    if request.method == 'POST':
        to_user_id = request.POST.get('to_user_id')
        to_user = get_object_or_404(User, UId=to_user_id)
        
        # Check if the friend request already exists
        if Friend_Request.objects.filter(from_user_id=request.user, to_user_id=to_user).exists():
            return JsonResponse({'error': 'Friend request already sent.'}, status=400)

        # Create a new friend request
        Friend_Request.objects.create(from_user_id=request.user, to_user_id=to_user)

        return JsonResponse({'message': 'Friend request sent successfully!'})
    
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required
def accept_friend_request(request, request_id):
    # Fetch the friend request by its ID
    friend_request = get_object_or_404(Friend_Request, id=request_id)

    # Make sure the logged-in user is the intended recipient
    if friend_request.to_user_id == request.user:
        # Update the status to 'accepted'
        friend_request.status = 'accepted'
        friend_request.save()

        # Add the sender and receiver to each other's friends list
        sender = friend_request.from_user_id
        receiver = friend_request.to_user_id
        sender.friends.add(receiver)
        receiver.friends.add(sender)
        friend_request.delete() # Remove the friend request once the two have become friends

    return redirect('friends')  

@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(Friend_Request, id=request_id)
    
    # Make sure the logged-in user is the intended recipient
    if friend_request.to_user_id == request.user:
        # Update the status to 'declined'
        friend_request.status = 'declined'
        friend_request.save()
        

    return redirect('friends')

@login_required
def change_dine_invite_status(request):
    if request.method == "POST":
        user = request.user
        
        # extract data from AJAX request
        # invite_id = int(request.POST.get('id'))
        invite_id = request.POST.get('id')
        
        if invite_id is None:
            return JsonResponse({'status': 'error', 'invite_id': -1}, status=400)

        try:
            invite_id = int(invite_id)
        except ValueError:
            return JsonResponse({'status': 'error', 'invite_id': -1}, status=400)

        status = request.POST.get('status')
        invite = get_object_or_404(Dine_Buddy, id=invite_id)

        # update status :))
        invite.status = status 
        invite.save()
        print(invite)

        return JsonResponse({
            'status': 'success',
            'invite_status' : invite.status,
            'invite_id': invite_id
        })

    return JsonResponse({'status': 'error'}, status=400)


@login_required
def like_view(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 
                                 'message': 'You must be logged in to perform this action.', 'redirect': '/login/'}, status=401)

        # user who performed the action
        user = request.user
        
        # extracts data from AJAX request
        RId = request.POST.get('RId')
        action = request.POST.get('action')

        restaurant = get_object_or_404(Restaurant, RId=RId) 
        # checks if user already interacted with the restaurant before
        interaction, created = Interaction_Details.objects.get_or_create(
            RID=restaurant,
            UID=user
        )

        if action == 'like':
            if interaction.is_like is True:  # user already liked, so remove the like
                interaction.is_like = None
            else:  # like the restaurant
                interaction.is_like = True
        elif action == 'dislike':
            if interaction.is_like is False:  # user already disliked, so remove the dislike
                interaction.is_like = None
            else:  # dislike the restaurant
                interaction.is_like = False
        interaction.save()

        return JsonResponse({
            'status': 'success',
            'action': action,
            'is_like': interaction.is_like
        })

    return JsonResponse({'status': 'error'}, status=400)

@login_required
def bookmark_view(request):
    if request.method == "POST":
        # user who performed the action
        user = request.user
        
        # extracts data from AJAX request
        RId = request.POST.get('RId')
        action = request.POST.get('action')

        restaurant = get_object_or_404(Restaurant, RId=RId) 

        # checks if user already interacted with the restaurant before
        interaction, created = Saved_Restaurants.objects.get_or_create(
            RID=restaurant,
            UID=user
        )

        if action == 'bookmark': # if the user clicks on bookmark
            if interaction.is_bookmarked:  # user has already bookmarked the restaurant, so remove the bookmark
                interaction.is_bookmarked = False
            else:  # bookmark the restaurant
                interaction.is_bookmarked = True

        interaction.save()

        return JsonResponse({
            'status': 'success',
            'action': action,
            'is_bookmarked': interaction.is_bookmarked
        })

    return JsonResponse({'status': 'error'}, status=400)
    
    
@login_required
def dine_buddy_view(request):
    if request.method == "POST":
        user = request.user
        
        # extract data from AJAX request
        RId = request.POST.get('RId')
        selected_friend_ids = request.POST.getlist("ids[]")

        print(selected_friend_ids)

        restaurant = get_object_or_404(Restaurant, RId=RId) 

        for friend_id_str in selected_friend_ids:
            friend = get_object_or_404(User, UId=int(friend_id_str)) 
            invite, created = Dine_Buddy.objects.get_or_create(
                RID=restaurant,
                from_user_id=user,
                to_user_id=friend
                )
            invite.save()
            print(invite)

        return JsonResponse({
            'status': 'success',
            'items': selected_friend_ids
        })

    return JsonResponse({'status': 'error'}, status=400)



def is_admin_user(user):
    return user.is_staff or user.is_superuser

@login_required
def admin_home_view(request):
    # Check if the user is not admin
    if not is_admin_user(request.user):
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')
    
    current_user = request.user
    restaurants = Restaurant.objects.all()
    
    # Sorting Logic: show trending 
    likes_count_subquery = Interaction_Details.objects.filter(
        RID=OuterRef('pk'),  # Reference to the Restaurant's PK
        is_like=True
    ).values('RID').annotate(like_count=Count('RID')).values('like_count')

    restaurants = restaurants.annotate(likes_count=Subquery(likes_count_subquery)).order_by('-likes_count')
    paginator = Paginator(restaurants, 21)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    interaction_status = {}
    friends = None

    # Get filter parameters
    postal_code = bleach.clean(request.GET.get('postal_code') or "")
    search = bleach.clean(request.GET.get('search') or "")
    liked_by = bleach.clean(request.GET.get('liked_by') or "")
    sort_options = request.GET.getlist('sort')

    try:
        if current_user.is_authenticated:
        # Get interaction details
            for restaurant in restaurants:
                interaction = Interaction_Details.objects.filter(RID=restaurant, UID=current_user).first()
                interaction_status[restaurant.RId] = interaction.is_like if interaction else None
            
            friends = current_user.friends.all()
            bookmarked_restaurants = Saved_Restaurants.objects.filter(UID=current_user, is_bookmarked=True).select_related('RID')
            for bookmark in bookmarked_restaurants:
                saved_status[bookmark.RID.RId] = True
        else:
            for restaurant in restaurants:
                interaction_status[restaurant.RId] = None
    except Exception as e:
        # Redirect to login view if user is not authenticated or any other error occurs
        return redirect('/accounts/login/')

    
    # Filtering
    filtered_restaurants_queryset = (Restaurant.objects.all())
    if not filtered_restaurants_queryset.exists():
            messages.error(request, "No restaurants found matching your criteria.")  # Set the error message
            return redirect("admin_home")
    
    price_filters = request.GET.getlist('price')  # Get the list of selected price values
    if price_filters:
        filtered_restaurants_queryset = filtered_restaurants_queryset.filter(price__in=price_filters)

    if postal_code:
        filtered_restaurants_queryset = filtered_restaurants_queryset.filter(postal_code=postal_code)

    if search:
        filtered_restaurants_queryset = filtered_restaurants_queryset.filter(
            Q(name__icontains=search) | Q(cuisine__icontains=search)
        )
    
    if liked_by:
        user = User.objects.filter(username=liked_by).first()
        if user:
            liked_by_user = Interaction_Details.objects.filter(UID=user, is_like=True).values_list('RID', flat=True)
            filtered_restaurants_queryset = filtered_restaurants_queryset.filter(RId__in=liked_by_user)

    # Sorting Logic
    sort_filters = request.GET.getlist('sort')  # Get the list of selected sort values
    if sort_filters:
        if 'friends' in sort_filters:
            # Apply your custom logic for sorting by friends
            filtered_restaurants_queryset = sorted(
                filtered_restaurants_queryset,
                key=lambda r: len(Interaction_Details.objects.filter(RID=r, is_like=True, UID__in=current_user.friends.all())),
                reverse=True
                )
        if 'most_liked' in sort_filters:
            likes_count_subquery = Interaction_Details.objects.filter(
                RID=OuterRef('pk'),  # This should be the correct reference to the Restaurant's PK
                is_like=True
            ).values('RID').annotate(like_count=Count('RID')).values('like_count')

            filtered_restaurants_queryset = filtered_restaurants_queryset.annotate(
                likes_count=Subquery(likes_count_subquery)
            ).order_by('-likes_count')
    
    # Pagination
    paginator = Paginator(filtered_restaurants_queryset, 21)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)

    friends = current_user.friends.all() #Fetch the user's friends - needed for dine buddy
    print(f"friends of user: {friends}")


    return render(request, 'admin/home.html', {
        'page_object': page_object,
        'interaction_status': interaction_status,
        'friends': friends,
        'login_redirect': reverse("login"),
        'user': request.user,
    })

    
@login_required
def admin_people_view(request):
    # if a non-admin user tries to access this view, they are redirected to the home page
    if not is_admin_user(request.user):
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')
    
    # gets all users
    users = User.objects.all()
    
    paginator = Paginator(users, 40)  # 40 users per page
    page_number = request.GET.get('page')  
    users_paginated = paginator.get_page(page_number)
    
    return render(request, 'admin/people.html', {
        'users': users_paginated,
        'current_user': request.user,  
    })

@login_required
def admin_edit_people_view(request, id):
    # if a non-admin user tries to access this view, they are redirected to the home page
    if not is_admin_user(request.user):
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')
    
    user = get_object_or_404(User, UId=id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            username = bleach.clean(form.cleaned_data.get('username') or "")
            city = bleach.clean(form.cleaned_data.get('city') or "")
            bio = bleach.clean(form.cleaned_data.get('bio') or "")
            postal_code = bleach.clean(form.cleaned_data.get('postal_code') or "")

            user.username = username
            user.city = city
            user.bio = bio
            user.postal_code = postal_code
            
            user.save()
            messages.success(request, f'{user.username} has been updated successfully.')
            return redirect('admin_people')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    # form will be filled with user's current details
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'admin/edit_people.html', {
        'form': form,
        'user': user,
    })

@login_required
def admin_delete_people_view(request, id):
    # if a non-admin user tries to access this view, they are redirected to the home page
    if not is_admin_user(request.user):
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')
    
    try:
        user = User.objects.get(UId=id)  
        if user == request.user:
            messages.error(request, 'You cannot delete your own account.')
            return redirect('admin_people')
        
        user.delete()
        messages.success(request, f'User {user.username} has been successfully deleted.')
        
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
    
    return redirect('admin_people')

@login_required
def delete_friend(request, friend_id):  # Ensure friend_id is passed as a positional argument
    try:
        friend = User.objects.get(UId=friend_id)  # Use UId to get the friend
        request.user.friends.remove(friend)  # Assuming the ManyToManyField is set up correctly
        messages.success(request, f'{friend.username} has been removed from your friends.')
    except User.DoesNotExist:
        messages.error(request, 'Friend does not exist.')
    return redirect('friends')  # Redirect to the friends page after deletion 

# this view finds all restaurants that have been liked or disliked by the current user's friend
@login_required
def friend_profile(request, friend_id):
    friend = get_object_or_404(User, pk=friend_id)
    
    liked_restaurants = Interaction_Details.objects.filter(UID=friend, is_like=True).select_related('RID')
    disliked_restaurants = Interaction_Details.objects.filter(UID=friend, is_like=False).select_related('RID')

    context = {
        'friend': friend,
        'liked_restaurants': [interaction.RID for interaction in liked_restaurants],
        'disliked_restaurants': [interaction.RID for interaction in disliked_restaurants],
        'login_redirect': reverse("login"),
        'user': request.user,
    }
    return render(request, 'friend_profile.html', context)

@login_required
def saved_view(request):
    # Ensure the current user is properly evaluated
    current_user = request.user
    friends = None

    if isinstance(current_user, SimpleLazyObject):
        current_user = current_user._wrapped

    if current_user.is_authenticated:
        friends = current_user.friends.all()

        # Fetch only bookmarked restaurants for the current user, ordering by name
        bookmarked_restaurants = Saved_Restaurants.objects.filter(UID=current_user, is_bookmarked=True).select_related('RID').order_by('RID__name')

        # Extract the actual Restaurant objects from the saved bookmarks
        restaurants = [bookmark.RID for bookmark in bookmarked_restaurants]

        # Set up pagination (showing 21 restaurants per page)
        paginator = Paginator(restaurants, 21)
        page_number = request.GET.get('page')
        page_object = paginator.get_page(page_number)

        # Prepare interaction status and saved status dictionaries
        interaction_status = {}
        saved_status = {}

        # Check interaction details for each bookmarked restaurant
        for restaurant in restaurants:
            interaction = Interaction_Details.objects.filter(RID=restaurant, UID=current_user).first()
            interaction_status[restaurant.RId] = interaction.is_like if interaction else None

            # Mark the restaurant as bookmarked
            saved_status[restaurant.RId] = True

    # Render the page with only the saved (bookmarked) restaurants
    return render(request, 'home.html', {
        'page_object': page_object,
        'interaction_status': interaction_status,
        'saved_status': saved_status,
        # 'interaction_status': saved_status,
        'login_redirect': reverse("login"),
        'user': request.user,
        'friends': friends,
    })

    # If the user is not authenticated, redirect to login (though this should be handled by @login_required)
    return redirect('login')

@login_required
def session_status(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})


@login_required
def add_restaurant(request):
    if not is_admin_user(request.user):
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')
    
    if request.method == 'POST':
        # Extract data from the request
        name = bleach.clean(request.POST.get('name') or "")
        cuisine = bleach.clean(request.POST.get('cuisine') or "")
        price = bleach.clean(request.POST.get('price') or "")
        postal_code = bleach.clean(request.POST.get('postal_code') or "")
        image = request.FILES.get('image')  # Use request.FILES for file uploads
        image_data = None
        new_RId = "0000"

        while True:
            new_RId = str(uuid.uuid4())
            if not Restaurant.objects.filter(RId=new_RId).exists():
                break

        # Convert image to Base64 string
        if image:
            image_data = base64.b64encode(image.read()).decode('utf-8')
        else:
            image_data = None
        
        if not name:
            return render(request, 'admin/add_card.html', {'error': 'Restaurant Name is required.'})

        
        # Create a new Restaurant instance
        restaurant = Restaurant(
            RId = new_RId,
            name=name,
            cuisine=cuisine,
            price=price,
            postal_code=postal_code,
            img_urls=image_data,
            yelp_rev_url="fill",
            phone_number="fill",
            rating=0,
            address="address",
            menu_url="fill",
            longitude=0,
            latitude=0,
            alcohol="fill"
        )

        # Save the restaurant if valid
        try:
            restaurant.full_clean()  # Validates the model instance
            restaurant.save()
            return redirect('admin_home')  # Redirect back to the home page
        except ValidationError as e:
            # Handle validation errors (you could store these in messages or render them)
            return render(request, 'add_card.html', {'error': e.messages})
    
    return render(request, 'admin/add_card.html', {})

# @csrf_exempt # To bypass csrf protections and allow deleteion
@login_required
def delete_restaurant(request, RId):
    if not is_admin_user(request.user):
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')
    try:
        restaurant = get_object_or_404(Restaurant, RId=RId)
        if request.method == 'POST':
            restaurant.delete()
            return JsonResponse({'message': 'Restaurant deleted successfully'}, status=204)
        
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    except Http404:
        return render(request, '404.html')  # Render a 404 page if not found
    
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

@login_required
def edit_restaurant(request, RId):
    if not is_admin_user(request.user):
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')
    
    restaurant = get_object_or_404(Restaurant, RId=RId)

    if request.method == 'PUT':
        try:
            # Parse the JSON body
            data = json.loads(request.body)

            # Update restaurant details based on form input
            name = bleach.clean(data.get('name', ''))
            postal_code = bleach.clean(data.get('postal_code', ''))
            price = bleach.clean(data.get('price', ''))

            # Check if the remove_image checkbox was selected
            if data.get('remove_image'):
                restaurant.img_urls = None

            restaurant.save()

            # Return a successful JSON response
            return JsonResponse({'message': 'Restaurant updated successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # Handle GET request: render the edit form
    return render(request, 'admin/edit_card.html', {'restaurant': restaurant})


class RestaurantCreateView(CreateView):
    model = Restaurant
    fields = ['name', 'cuisine', 'location']  # Include other fields as needed
    template_name = 'restaurant_form.html'
    success_url = reverse_lazy('home')

# Edit View for updating an existing restaurant
class RestaurantUpdateView(UpdateView):
    model = Restaurant
    fields = ['name', 'cuisine', 'location']
    template_name = 'restaurant_form.html'
    success_url = reverse_lazy('home')

# Delete View for deleting a restaurant
class RestaurantDeleteView(DeleteView):
    model = Restaurant
    template_name = 'restaurant_confirm_delete.html'  # Confirmation page
    success_url = reverse_lazy('home')

    
# Django Rest Framework Views
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RestaurantListCreate(generics.ListCreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class FriendRequestListCreate(generics.ListCreateAPIView):
    queryset = Friend_Request.objects.all()
    serializer_class = FriendRequestSerializer

class InteractionDetailsListCreate(generics.ListCreateAPIView):
    queryset = Interaction_Details.objects.all()
    serializer_class = InteractionDetailsSerializer

class SavedRestaurantsListCreate(generics.ListCreateAPIView):
    queryset = Saved_Restaurants.objects.all()
    serializer_class = SavedRestaurantsSerializer

class DineBuddyListCreate(generics.ListCreateAPIView):
    queryset = Dine_Buddy.objects.all()
    serializer_class = DineBuddySerializer
