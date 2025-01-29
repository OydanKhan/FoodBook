document.addEventListener('DOMContentLoaded', function() {
    // Selecting all bookmark buttons on the page
    const bookmarkButtons = document.querySelectorAll('.bookmark-button');

    // Adding an event listener to all bookmark buttons
    bookmarkButtons.forEach(button => {
        button.addEventListener('click', function() {
            const restaurantId = this.closest('.grouped-features').querySelector('.bookmark-button').getAttribute('data-id');
            toggleBookmark(restaurantId, 'bookmark', this);
        });
    });

    // Function to toggle the bookmark state
    function toggleBookmark(restaurantId, action, button) {
        const formData = new FormData();
        formData.append('RId', restaurantId);
        formData.append('action', action);

        // Send a POST request to bookmark/unbookmark the restaurant
        fetch('/bookmark/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(), // Get the CSRF token for security
            },
            body: formData
        })
        
        // When server responds its converted to json
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update the bookmark icon based on the new state
                updateBookmarkIcon(button, data.is_bookmarked);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Function to update the bookmark icon based on the state
    function updateBookmarkIcon(button, isBookmarked) {
        const bookmarkImg = button.querySelector('img');

        if (isBookmarked) {
            bookmarkImg.src = "/static/images/bookmarked.png"; // Change to bookmarked image
        } else {
            bookmarkImg.src = "/static/images/bookmark.png"; // Change to default image
        }
    }

    // Function to get CSRF token
    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }
});