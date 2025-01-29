# API Doumentation

Our application utilises many API endpoints, supported by the JSON format. These endpoints are used to perform Create, Read, Update, and Delete (CRUD) operations, following REST principles. For example, our API design follows the stateless principle by ensuring each request is self-contained, does not rely on previous interactions, and utilises the appropriate HTTP methods for CRUD operations. 

### UserListCreate
POST: When a client sends a POST request to the same endpoint with user data, the view will use the UserSerializer to validate and create a new User instance in the database. If the data is valid, it will save the new user and return the created user data in the response. 
Example: 

Request Body: <br>
{<br>
  "name": "New Restaurant",<br>
  "username": "New Username",<br>
  "city": "Sydney", <br>
  “bio”: “New bio”,<br>
  “is_admin”: false, <br>
  “friends”: [2, 3],  # Assuming Alice and Charlie have UId’s 1 and 3 <br>
  “previously_interacted_posts”: [1,2,5],<br> 
  “profile_pic”: “path/to/profile/pic”<br>
}<br>

Response: <br>
{<br>
  "UId": 2,<br>
  "name": "New Restaurant",<br>
  "username": "New Username",<br>
  "city": "Sydney", <br>
  “bio”: “New bio”,<br>
  “is_admin”: false, <br>
  “friends”: [2, 3],  # Assuming Alice and Charlie have UId’s 1 and 3<br>
  “previously_interacted_posts”: [1,2,5], <br>
  “profile_pic”: “path/to/profile/pic”<br>
}<br>

GET:
 When a client sends a GET request to the /api/users/ endpoint, the ListCreateAPIView will return a list of all users in JSON format. This allows clients to retrieve (read) user data. <br><br>
Example: <br>

Response: <br>
[<br>
  {<br>
    "UId": 2,<br>
  "name": "New Restaurant",<br>
  "username": "New Username",<br>
  "city": "Sydney", <br>
  “bio”: “New bio”,<br>
  “is_admin”: false, <br>
  “friends”: [2, 3],  # Assuming Alice and Charlie have UId’s 1 and 3 <br>“previously_interacted_posts”: [1,2,5],<br> 
  “profile_pic”: “path/to/profile/pic”<br>
  },<br>
  ...<br>
]<br>
<br>
Error Responses: 400 Bad Request: If required fields are missing or invalid.<br>

#### RestaurantListCreate
POST: Allows for the creation of a new restaurant with data validated and serialized by RestaurantSerializer.<br>
Example: <br>
<br>
Request Body: <br>
{<br>
  "name": "New Restaurant",<br>
  "postal_code": "5678",<br>
  "price": "$$"<br>
…<br>
}<br>

Response: <br>
{<br>
  "RId": 2,<br>
  "name": "New Restaurant",<br>
  "postal_code": "5678",<br>
  "price": "$$"<br>
…<br>
}<br>
 <br>
GET: Retrieves a list of all restaurants. <br>
Example: 

Response: <br>
{  "RId": 2,<br>
  "name": "New Restaurant",<br>
  "postal_code": "5678",<br>
  "price": "$$"<br>
…<br>
}<br>

Error Responses: 400 Bad Request If required fields are missing or invalid, 404 Not Found: If the requested resource does not exist.

### FriendRequestListCreate
POST: Allows the creation of a new friend request with data validated and serialized by FriendRequestSerializer.<br>
Example: 

Request Body: <br>
  {<br>
  "from_user": "user1",<br>
  "to_user": "user2"<br>
}<br>

Response: <br>
{<br>
  "id": 2,<br>
  "from_user": "user1",<br>
  "to_user": "user2",<br>
  "status": "pending"<br>
}<br>

GET: Retrieves a list of all friend requests. <br>
Example: <br>
Response: <br>
[<br>
  {<br>
    "id": 1,<br>
    "from_user": "user1",<br>
    "to_user": "user2",<br>
    "status": "pending"<br>
  },<br>
  ...<br>
]<br>

Error Responses: 400 Bad Request If users are invalid or already friends, 500 Internal Server Error: For server-related issues.


### InteractionDetailsListCreate
POST: Allows the creation of a new interaction detail with data validated and serialized by InteractionDetailsSerializer.<br>
Example: <br>

Request Body: <br>
{<br>
  "user": "user1",<br>
  "restaurant": "Restaurant A",<br>
  "action": "liked"<br>
}<br>
Response: <br>
{<br>
  "id": 2,<br>
  "user": "user1",<br>
  "restaurant": "Restaurant A",<br>
  "action": "liked"<br>
}<br>

GET: Retrieves a list of all interaction details.<br>
Example: <br>

Response:<br>
[<br>
  {<br>
    "id": 1,<br>
    "user": "user1",<br>
    "restaurant": "Restaurant A",<br>
    "action": "liked"<br>
  },<br>
  ...<br>
]<br>

### SavedRestaurantsListCreate
POST: Allows the creation of a new saved restaurant with data validated and serialized by SavedRestaurantsSerializer. <br>
Example: <br>

Request Body: <br>
{<br>
  "user": "user1",<br>
  "restaurant": "Restaurant A"<br>
}<br>

Response Body:{<br>
  "id": 2,<br>
  "user": "user1",<br>
  "restaurant": "Restaurant A"<br>
}<br>

GET: Retrieves a list of all saved restaurants.<br>
Example: <br>

Response Body:<br>
[<br>
  {<br>
    "id": 1,<br>
    "user": "user1",<br>
    "restaurant": "Restaurant A"<br>
  },<br>
  ...<br>
]<br>

### DineBuddyListCreate
POST: Allows the creation of a new dine buddy with data validated and serialized by DineBuddySerializer.<br>
Example: <br>

Request Body:<br>
{<br>
  "user": "user1",<br>
  "dine_buddy": "user2"<br>
}<br>

Response Body:<br>
{<br>
  "id": 2,<br>
  "user": "user1",<br>
  "dine_buddy": "user2"<br>
}<br>

GET: Retrieves a list of all dine buddies.<br>
Example: <br>

Response Body: [<br>
  {<br>
    "id": 1,<br>
    "user": "user1",<br>
    "dine_buddy": "user2"<br>
  },<br>
  ...<br>
]<br>
Error Responses: 400 Bad Request If required fields are missing or invalid, 404 Not Found: If the requested resource does not exist
