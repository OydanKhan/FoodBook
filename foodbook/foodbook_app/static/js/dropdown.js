document.addEventListener('DOMContentLoaded', function() {
  const dropdownButton = document.getElementById('userDropdown');
  const dropdownContent = document.getElementById('dropdownContent');

  // shows the dropdown menu when profile icon is clicked
  dropdownButton.addEventListener('click', function(event) {
      dropdownContent.classList.toggle('show');
  });

  // if user presses anywhere except the dropdown menu, closes it
  window.addEventListener('click', function(event) {
      if (!event.target.closest('.dropdown-menu')) {
          dropdownContent.classList.remove('show');
      }
  });
  document.addEventListener('DOMContentLoaded', function() {
    // Select the form
    const searchForm = document.querySelector('.search-container');

    // Listen for keydown events on inputs within the form
    searchForm.addEventListener('keydown', function(event) {
        // Check if the pressed key is "Enter"
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default form submission
            console.log('Enter key pressed, submitting form...');
            searchForm.submit(); // Trigger form submission
        }
    });
});


});

