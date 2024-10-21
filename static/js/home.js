document.addEventListener('DOMContentLoaded', function() {
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('click', function(e) {
            e.preventDefault();
            const feature = this.getAttribute('data-feature');
            const screenshotUrl = `/static/images/${feature}-screenshot.png`;
            
            const popup = document.createElement('div');
            popup.classList.add('screenshot-popup');
            popup.innerHTML = `
                <div class="screenshot-content">
                    <button class="close-popup">&times;</button>
                    <img src="${screenshotUrl}" alt="${feature} screenshot">
                </div>
            `;
            
            document.body.appendChild(popup);
            
            popup.querySelector('.close-popup').addEventListener('click', function() {
                document.body.removeChild(popup);
            });
        });
    });
});
