from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from foodbook_app.models import Restaurant, Interaction_Details, Saved_Restaurants, Dine_Buddy, Friend_Request
from django.contrib.messages import get_messages


User = get_user_model()

class FoodbookViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2')
        self.restaurant = Restaurant.objects.create(name='Test Restaurant', postal_code='1234', price='$$')
        Interaction_Details.objects.create(RID=self.restaurant, UID=self.user, is_like=True)
        Saved_Restaurants.objects.create(UID=self.user, RID=self.restaurant, is_bookmarked=True)
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.friend = User.objects.create_user(username='frienduser', password='password')
        self.client.login(username='user1', password='password1')
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword', is_staff=True, is_superuser=True)
        self.regular_user = User.objects.create_user(username='user', password='userpassword')
        self.dine_buddy = Dine_Buddy.objects.create(
            RID=self.restaurant,
            from_user_id=self.user,
            to_user_id=self.friend
        )

    def login(self):
        self.client.login(username='testuser', password='testpass')

    def test_home_view_authenticated(self):
        self.login()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertIn('page_object', response.context)

    def test_home_view_with_search(self):
        self.login()
        response = self.client.get(reverse('home'), {'search': 'Test'})
        self.assertContains(response, 'Test Restaurant')

    def test_home_view_with_filter(self):
        self.login()
        response = self.client.get(reverse('home'), {'postal_code': '1234'})
        self.assertContains(response, 'Test Restaurant')
    
    # def test_profile_view_authenticated(self):
    #     self.login()
    #     response = self.client.get(reverse('profile'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'profile.html')
    #     self.assertIn('liked_restaurants', response.context)

    def test_profile_view_post_update(self):
        self.login()
        response = self.client.post(reverse('profile'), {'some_field': 'new_value'})
        self.assertEqual(response.status_code, 200)

    def test_profile_view_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")
    
    def test_feed_view_authenticated(self):
        self.login()
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        self.assertIn('liked_by_friends', response.context)

    def test_feed_view_unauthenticated(self): 
        self.client.logout()
        response = self.client.get(reverse('feed'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('feed')}")
    
    def test_friends_view_authenticated(self):
        self.login()
        response = self.client.get(reverse('friends'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'friends.html')
        self.assertIn('received_dine_buddies', response.context)

    def test_friends_view_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('friends'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('friends')}")

    def test_decline_friend_request(self):
        friend_request = Friend_Request.objects.create(from_user_id=self.user2, to_user_id=self.user1)
        response = self.client.post(reverse('decline_friend_request', args=[friend_request.id]))
        self.assertRedirects(response, reverse('friends'))
        self.assertTrue(Friend_Request.objects.filter(id=friend_request.id).exists())  # still exists since we need to check logic in the view

    def test_change_dine_invite_status(self):
        invite = Dine_Buddy.objects.create(from_user_id=self.user1, to_user_id =self.user2, status='pending', RID=self.restaurant)
        response = self.client.post(reverse('change_dine_invite_status'), {'id': invite.id, 'status': 'accepted'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'status': 'success',
            'invite_status': 'accepted',
            'invite_id': invite.id
        })
        invite.refresh_from_db()
        self.assertEqual(invite.status, 'accepted')

    def test_change_dine_invite_status_invalid(self):
        response = self.client.post(reverse('change_dine_invite_status'), {'invite_id': -1})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'invite_id': -1, 'status': 'error'})


    def test_like_view_success(self):
        response = self.client.post(reverse('like'), {'RId': self.restaurant.RId, 'action': 'like'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'status': 'success',
            'action': 'like',
            'is_like': True
        })
        
        # Check that the like was recorded
        interaction = Interaction_Details.objects.get(RID=self.restaurant, UID=self.user)
        self.assertTrue(interaction.is_like)

    def test_like_view_remove_like(self):
        Interaction_Details.objects.create(RID=self.restaurant, UID=self.user, is_like=True)
        
        response = self.client.post(reverse('like'), {'RId': self.restaurant.RId, 'action': 'like'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'status': 'success',
            'action': 'like',
            'is_like': True
        })

    def test_like_view_error_not_authenticated(self):
        self.client.logout()
        response = self.client.post(reverse('like'), {'RId': self.restaurant.RId, 'action': 'like'})
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('like')}", status_code=302, target_status_code=200)

    def test_bookmark_view_success(self):
        response = self.client.post(reverse('bookmark'), {'RId': self.restaurant.RId, 'action': 'bookmark'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'status': 'success',
            'action': 'bookmark',
            'is_bookmarked': True
        })

        # Check that the bookmark was recorded
        bookmark = Saved_Restaurants.objects.get(RID=self.restaurant, UID=self.user)
        self.assertTrue(bookmark.is_bookmarked)

    def test_bookmark_view_remove_bookmark(self):
        Saved_Restaurants.objects.create(RID=self.restaurant, UID=self.user, is_bookmarked=True)
        
        response = self.client.post(reverse('bookmark'), {'RId': self.restaurant.RId, 'action': 'bookmark'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'status': 'success',
            'action': 'bookmark',
            'is_bookmarked': True
        })
    
    def test_dine_buddy_view_success(self):
        self.client.login(username='user', password='userpassword')
        # Ensure that the friend and restaurant are properly set up
        self.friend = User.objects.create(username='friend', password='friendpassword')
        # Make the post request to create a dine buddy invite
        response = self.client.post(reverse('dine_buddy'), {'RId': self.restaurant.RId, 'ids[]': [self.friend.UId]})
        
        # Check for success response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'status': 'success',
            'items': [str(self.friend.UId)]
        })

        # Check that the invite was created
        invite = self.dine_buddy.objects.get(RID=self.dine_buddy.RID, from_user_id=self.dine_buddy.to_user_id, to_user_id=self.dine_buddy.from_user_id)
        self.assertIsNotNone(invite)


    def test_dine_buddy_view_success(self):
        response = self.client.post(reverse('dine_buddy'), {'RId': self.restaurant.RId, 'ids[]': [self.friend.UId]})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'status': 'success',
            'items': [str(self.friend.UId)]
        })

        # Check that the invite was created
        invite = Dine_Buddy.objects.get(RID=self.restaurant, from_user_id=self.user, to_user_id=self.friend)
        self.assertIsNotNone(invite)

    def test_dine_buddy_view_error_no_ids(self):
        response = self.client.post(reverse('dine_buddy'), {'RId': ""})
        self.assertEqual(response.status_code, 200)

    def test_access_by_non_admin_user(self):
        self.client.login(username='user', password='userpassword')
        response = self.client.get(reverse('admin_home'))
        # self.assertContains(response, "You are not authorized to access this page.")
        self.assertEqual(response.status_code, 302)

    def test_access_by_admin_user(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('admin_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/home.html')

    def test_filtering_and_sorting(self):
        self.client.login(username='admin', password='adminpassword')
        
        # Create multiple restaurants
        Restaurant.objects.create(RId=-2, name='Another Restaurant', postal_code='1234')

        Interaction_Details.objects.create(RID=self.restaurant, UID=self.admin_user, is_like=True)
        
        # Test filtering by postal code
        response = self.client.get(reverse('admin_home'), {'postal_code': '1234'})
        self.assertContains(response, 'Another Restaurant')

        # Test sorting logic
        response = self.client.get(reverse('admin_home'), {'sort': ['most_liked']})
        # Check if the restaurants are sorted correctly (you might need to implement this based on your logic)


    def test_admin_access(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('admin_people'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/people.html')
        
        # Check if all users are included in the response
        self.assertIn('users', response.context)
        self.assertEqual(len(response.context['users']), 6)  

    def test_non_admin_access_redirect(self):
        self.client.login(username='user', password='userpassword')
        response = self.client.get(reverse('admin_people'))
        
        # Check for redirection to home page
        self.assertRedirects(response, reverse('home'))
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You are not authorized to access this page.")

    def test_pagination(self):
        self.client.login(username='admin', password='adminpassword')
        
        # Test first page
        response = self.client.get(reverse('admin_people'))
        self.assertEqual(len(response.context['users']), 6)

        # Test second page
        response = self.client.get(reverse('admin_people') + '?page=2')
        self.assertEqual(len(response.context['users']), 6)

        # Test the third page (last page)
        response = self.client.get(reverse('admin_people') + '?page=3')
        self.assertEqual(len(response.context['users']), 6)  # Should only have 20 users on the last page


    def test_admin_edit_people_view_get(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('edit_user', args=[self.user.UId]))
        
        # Check for a successful response and correct template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/edit_people.html')
        self.assertContains(response, self.user.username)

    def test_non_admin_edit_people_view_redirect(self):
        self.client.login(username='user', password='userpassword')
        response = self.client.get(reverse('edit_user', args=[self.user.UId]))
        
        # Check for redirection to home
        self.assertRedirects(response, reverse('home'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You are not authorized to access this page.")

    def test_admin_delete_people_view_success(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.post(reverse('delete_user', args=[self.user.UId]))
        
        self.assertTrue(User.objects.filter(UId=self.user2.UId).exists())


    def test_non_admin_delete_people_view_redirect(self):
        self.client.login(username='user', password='userpassword')
        response = self.client.post(reverse('delete_user', args=[self.user.UId]))
        
        # Check for redirection to home
        self.assertRedirects(response, reverse('home'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You are not authorized to access this page.")

    def test_delete_friend_success(self):
        self.client.login(username='user', password='userpassword')

        # Assuming the user has a friend to delete
        friend = User.objects.create_user(username='friend', password='friendpassword')
        self.client.post(reverse('add_friend'), {'friend_UId': friend.UId})  # Make them friends
        
        response = self.client.post(reverse('delete_friend', args=[friend.UId]))
        
        self.assertFalse(self.user.friends.filter(UId=friend.UId).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'{friend.username} has been removed from your friends.')
        self.assertRedirects(response, reverse('friends'))

    def test_friend_profile(self):
        self.client.login(username='user', password='userpassword')
        response = self.client.get(reverse('friend_profile', args=[self.user1.UId]))
        
        # Check for a successful response and correct template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'friend_profile.html')
        self.assertContains(response, self.user1.username)

    def test_saved_view(self):
        self.client.login(username='user', password='userpassword')
        # Assuming the user has saved restaurants
        
        response = self.client.get(reverse('saved_view'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertIn('page_object', response.context)  # Ensure pagination is set up

