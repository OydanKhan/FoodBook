function submitFilter(element) {
    const form = element.closest('.filter');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    fetch("{% url 'feed' %}", {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())

    // The below updates without refresh
    .then(data => {
        const restaurantWrapper = document.querySelector('.restaurant-wrapper');
        restaurantWrapper.innerHTML = data.html;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
