
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.restaurant-summary').forEach(card => {
        card.addEventListener('click', function () {
            const cardElement = this.parentElement;
            cardElement.classList.toggle('expanded'); 
            const cardDetails = cardElement.querySelector('.restaurant-details');
            
            if (cardElement.classList.contains('expanded')) {
                cardDetails.style.display = 'block'; 
            } else {
                cardDetails.style.display = 'none';
            }
        });
    });
});