console.log("script loaded");
document.addEventListener('DOMContentLoaded', function() {


    const dineButtons = document.querySelectorAll(".dine-buddy-button");
    // const buttons = document.querySelectorAll("button");
    const pop_up = document.getElementById("pop-up-container");
    const close_pop_up = document.getElementById("close-pop-up");
    const heading = document.getElementById("pop-up-title");
    const send_invites_button = document.getElementById("send-invites-button");
    const sentNotif = document.getElementById("dine-sent-notification");


    restaurantId = null;

    console.log("line 4");

    dineButtons.forEach(function(button) {

        const dineImg = button.querySelector('img');

        button.addEventListener("click", function() {

            console.log("clicked dine buddy button");
            const restaurantName = this.getAttribute("data-name");
            restaurantId = this.getAttribute("data-id");

            const userAuthenticated = button.getAttribute("data-is-auth");
            const loginRedirect = button.getAttribute("data-login");

            if (userAuthenticated == "False") {
                // Use "False" - python format from views
                console.log("redirecting to login");
                console.log(userAuthenticated);
                window.location.href= loginRedirect;
            }
            else {

                console.log("authenticated user");
                console.log(userAuthenticated);
                openPopUp(this, restaurantName);
            }

        })
    })

    close_pop_up.addEventListener("click", function() {
        pop_up.style.display = "none";
    })

    send_invites_button.addEventListener("click", function(event) {
        event.preventDefault();
        console.log("clicked send button");
        // pop_up.style.display = "none";
        sendInvites(this, restaurantId);
        sentNotif.style.display = "flex";
        setTimeout(function() {
            sentNotif.style.display = "none";
        }, 1500);
    })

    function openPopUp(button, restaurantName) {
        pop_up.style.display = "flex";
        heading.textContent = "Invite your friends to " + restaurantName;
    }


    function sendInvites(button, restaurantId) {
        
        const formData = new FormData();
        const checkedCheckboxes = document.querySelectorAll(".friend-checkbox:checked");

        // add the data to the form
        formData.append('RId', restaurantId);
        checkedCheckboxes.forEach((checkbox, index) => {
            console.log(checkbox)
            formData.append("items[]", checkbox.value);
            formData.append("ids[]", checkbox.getAttribute("data-id"));
        })

        // helps to log (keep track of the form)
        for (let pair of formData.entries()) {
            console.log(pair[0] + ": " + pair[1]);
        }
 
        fetch('/dine-buddy/', {
            // Method is POST, meaning data is sent to the server
            method: 'POST',

            // CSRF token is just included in headers for security. I dont really get it.
            headers: {
                'X-CSRFToken': getCSRFToken(),  
            },

            body: formData  
        })

        .then(response => response.json())

        .then(data => {
            if (data.status === 'success') {

                console.log("Data success :)!", data);
            }
        })
        .catch(error => console.error('Error:', error));
    
    }
    

    // CSRF - cross-site request forgery
    // A security feature that ensures that the request is coming from a trusted source. 
    // The token is sent in the header of the request and validated by the server to prevent unauthorized actions.
    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }

});
