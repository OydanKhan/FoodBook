console.log("Here! 1");
// const CSRFToken = document.getElementById("csrf_token").value;

document.addEventListener('DOMContentLoaded', function() {

    console.log("Here! 3")

    const acceptDineButtons = document.querySelectorAll(".accept-dine-button");
    const declineDineButtons = document.querySelectorAll(".decline-dine-button");

    acceptDineButtons.forEach(function(button) {
        button.addEventListener("click", function(event) {
            console.log("accept dine clicked");
            event.preventDefault();
            changeInviteStatus(this, "accepted");
        });
    });

    declineDineButtons.forEach(function(button) {
        button.addEventListener("click", function(event) {
            console.log("decline dine clicked");
            event.preventDefault();
            changeInviteStatus(this, "declined");
        });
    });

    function changeInviteStatus(button, newStatus) {
        const formData = new FormData();
        // const checkedCheckboxes = document.querySelectorAll(".friend-checkbox:checked");

        const dineBuddyId = button.getAttribute("data-id");
        // const dineBuddy = button.getAttribute("data-invite");

        // const RID = button.getAttribute("data-rid");
        // const to_user = button.getAttribute("data-to");
        // const from_user = button.getAttribute("data-from");
        // console.log("logging here hi", RID, "  ", to_user, "  ", from_user);
        // var status;

        const buttonType = button.getAttribute("class");
        // if (buttonType == "decline-button") {
        //     status = "declined";
        // }
        // else if (buttonType == "accept-button") {
        //     status = "accepted";
        // }
        // else {
        //     status = "pending";
        // }
        // add the data to the form
        formData.append('id', dineBuddyId);
        // formData.append('RID', RID);
        // formData.append('to_user_id', to_user);
        // formData.append('from_user_id', from_user);

        formData.append('status', newStatus);
        

        console.log("here? 41");

        // helps to log (keep track of the form)
        for (let pair of formData.entries()) {
            console.log(pair[0] + ": " + pair[1]);
        }
 
        fetch('/change-dine-invite-status/', {
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
                updateInviteCard(data.invite_status, data.invite_id);
            }
        })
        .catch(error => console.error('Error:', error));
    
    };

    function updateInviteCard(new_status, invite_id) {
        if (new_status == "pending" || new_status == "Pending") {
            // should never happen
        }
        else {
            // Hide the accept / decline buttons
            const to_hide = document.querySelectorAll('[data-id="' + invite_id + '"]');
            console.log("to hide: ", to_hide);
            to_hide.forEach(function(button) {
                button.style.display = "none";
            })
            // Show status
            // status_banner.style.display="flex";
            if (new_status == "accepted" || new_status == "Accepted") {
                const accepted_banner = document.getElementById("accepted-banner" + invite_id);
                accepted_banner.style.display = "flex";
            }
            else if (new_status == "declined" || new_status == "Declined") {
                const declined_banner = document.getElementById("declined-banner" + invite_id);
                declined_banner.style.display = "flex";
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