// static/js/church_detail.js

document.addEventListener('DOMContentLoaded', function() {
    const infoSections = document.querySelectorAll('.info-section h2');
    
    infoSections.forEach(section => {
        section.addEventListener('click', function() {
            this.parentElement.classList.toggle('expanded');
        });
    });
});