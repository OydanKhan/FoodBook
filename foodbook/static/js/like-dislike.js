// Fires when HTML document has been completely loaded and parsed, without waiting for other stylesheets, images and subframes
// The code inside it runs when the page content is fully loaded.
document.addEventListener('DOMContentLoaded', function() {

    // Selecting all like and dislike buttons on the page
    const likeButtons = document.querySelectorAll('.like-button');
    const dislikeButtons = document.querySelectorAll('.dislike-button');

    // Adding an event listener to all buttons
    likeButtons.forEach(button => {
        const status = button.getAttribute('data-status');
        const likeImg = button.querySelector('img');

        if (status === 'liked') {
            button.classList.add('liked');
            likeImg.src = "/static/images/liked.png";
        } else {
            likeImg.src = "/static/images/thumbs-up.png";
        }
        button.addEventListener('click', function() {
            // Getting the restaurant id from the 'data-id' field in the html.
            const restaurantId = this.getAttribute('data-id');
            // 'this' refers to the button!! Passes restaurant id and the action 'like'
            sendLikeDislikeRequest(restaurantId, 'like', this);
        });
    });

    dislikeButtons.forEach(button => {
        const status = button.getAttribute('data-status');
        const dislikeImg = button.querySelector('img');

        if (status === 'disliked') {
            button.classList.add('disliked');
            dislikeImg.src = "/static/images/disliked.png";
        } else {
            dislikeImg.src = "/static/images/thumbs-down.png";
        }

        button.addEventListener('click', function() {
            const restaurantId = this.getAttribute('data-id');
            sendLikeDislikeRequest(restaurantId, 'dislike', this);
        });
    });


    //  
    function sendLikeDislikeRequest(restaurantId, action, button) {
        // FormData is used to easily create key-value pairs to be sent with the request 
        // like (RId and action)
        const formData = new FormData();
        formData.append('RId', restaurantId);
        formData.append('action', action);

        // Sends request to server to the '/like/' endpoint.
        fetch('/like/', {
            // Method is POST, meaning data is sent to the server
            method: 'POST',

            // CSRF token is just included in headers for security. I dont really get it.
            headers: {
                'X-CSRFToken': getCSRFToken(),  
            },

            // The request body is the form data (what is above)
            body: formData  
        })
        // When server responds its converted to json
        .then(response => {
            if (response.redirected) {
                // Redirect the user to the login page
                window.location.href = response.url;
                return;
            }
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                console.log('Non-JSON response:', response);
                return Promise.reject('Received non-JSON response');
            }
        })

        // If ther server response indicates success, the updatebuttonstate function is called.
        .then(data => {
            if (data && data.status === 'success') {
                updateButtonState(button, action, data.is_like);
            } else if (data.status === 'error') {
    
                if (data.redirect) {
                        window.location.href = data.redirect;
                }
            } else {
                console.error('Unexpected response:', data);
            }
        })
        .catch(error => console.error('Error:', error));
    }


    // Finally updating the state of the buttons.
    function updateButtonState(button, action, isLike) {
        const likeButton = button.closest('.grouped-features').querySelector('.like-button');
        const dislikeButton = button.closest('.grouped-features').querySelector('.dislike-button');
        const likeImg = likeButton.querySelector('img');
        const dislikeImg = dislikeButton.querySelector('img');

        // This is FOR EACH button we're removing all liked/disliked previous classes
        // before changing anything on top of that.
        button.classList.remove('liked', 'disliked');
        // I don't understand what classes are for buttons exactly though.

        if (action === 'like') {
            if (isLike === true) {
                likeImg.src = "/static/images/liked.png";
                dislikeImg.src = "/static/images/thumbs-down.png";
                button.classList.add('liked');
            } else {
                likeImg.src = "/static/images/thumbs-up.png";
                button.classList.remove('liked', 'disliked');
            }
        } else if (action === 'dislike') {
            if (isLike === false) {
                dislikeImg.src = "/static/images/disliked.png";
                likeImg.src = "/static/images/thumbs-up.png";
                button.classList.add('disliked');
            } else {
                dislikeImg.src = "/static/images/thumbs-down.png";
                button.classList.remove('liked', 'disliked');
            }
        }
    }

    // CSRF - cross-site request forgery
    // A security feature that ensures that the request is coming from a trusted source. 
    // The token is sent in the header of the request and validated by the server to prevent unauthorized actions.
    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }
});
