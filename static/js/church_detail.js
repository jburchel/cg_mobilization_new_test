// static/js/church_detail.js

document.addEventListener('DOMContentLoaded', function() {
    const collapsibles = document.querySelectorAll('.collapsible');

    function toggleSection(section) {
        section.classList.toggle('active');
    }

    function initializeSections() {
        if (window.innerWidth < 768) {
            collapsibles.forEach(section => {
                section.classList.remove('active');
            });
        } else {
            collapsibles.forEach(section => {
                section.classList.add('active');
            });
        }
    }

    collapsibles.forEach(section => {
        const header = section.querySelector('h2');
        header.addEventListener('click', () => {
            if (window.innerWidth < 768) {
                toggleSection(section);
            }
        });
    });

    initializeSections();

    window.addEventListener('resize', initializeSections);
});