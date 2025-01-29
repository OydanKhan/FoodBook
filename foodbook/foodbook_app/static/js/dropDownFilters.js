function toggleDropDown(dropdownId, event) {
    event.preventDefault(); // Prevent form submission
    const dropdownContent = document.getElementById(dropdownId);
    dropdownContent.classList.toggle('show');
    console.log('Dropdown button clicked');
}

document.addEventListener('DOMContentLoaded', function() {
    // Select all dropdowns and their respective content
    const dropdowns = document.querySelectorAll('.dropdown-menu');

    dropdowns.forEach(dropdown => {
        const sortOptions = dropdown.querySelectorAll('.sort-option');
        const selectedOptionsDisplay = dropdown.querySelector('.dropdown-button .selected-options');

        // Update selected options display when a checkbox is clicked
        sortOptions.forEach(option => {
            option.addEventListener('change', function() {
                updateSelectedOptions(sortOptions, selectedOptionsDisplay);
            });
        });

        // If the user clicks anywhere outside the dropdown, close it
        window.addEventListener('click', function(event) {
            if (!event.target.closest('.dropdown-menu')) {
                dropdown.querySelector('.dropdown-content').classList.remove('show');
            }
        });
    });

    function updateSelectedOptions(sortOptions, selectedOptionsDisplay) {
        const selectedOptions = Array.from(sortOptions)
            .filter(option => option.checked)
            .map(option => option.parentNode.textContent.trim());

        selectedOptionsDisplay.textContent = selectedOptions.length > 0 
            ? selectedOptions.join(', ') 
            : ''; // Clear if no options selected
    }
});


document.querySelectorAll('input').forEach(input => {
    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent form submission
            console.log('Enter key pressed in input:', input.name);
        }
    });
});

