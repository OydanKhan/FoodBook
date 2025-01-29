const editButton = document.getElementById('editButton');
const saveButton = document.getElementById('saveButton');
const cancelButton = document.getElementById('cancelButton');
const inputs = document.querySelectorAll('#profileForm input, #profileForm textarea');
const editButtons = document.getElementById('editButtons');

// Store the original values to revert if the user cancels
let originalValues = {};

editButton.addEventListener('click', () => {
    // Enable all inputs
    inputs.forEach(input => {
        input.disabled = false;
        originalValues[input.id] = input.value; // Save original values
    });
    // Show save/cancel buttons and hide edit button
    editButtons.style.display = 'flex';
    editButton.style.display = 'none';
});

cancelButton.addEventListener('click', () => {
    // Revert inputs to original values and disable them
    inputs.forEach(input => {
        input.disabled = true;
        input.value = originalValues[input.id]; // Restore original values
    });
    editButtons.style.display = 'none';
    editButton.style.display = 'inline-block';
});

// When the form is submitted, keep inputs disabled and proceed with form submission
document.getElementById('profileForm').addEventListener('submit', (event) => {
    // Allow form submission to handle saving data
    inputs.forEach(input => input.disabled = false);
});
