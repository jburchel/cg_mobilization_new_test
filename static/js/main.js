document.addEventListener('DOMContentLoaded', function() {
    const navbarToggle = document.getElementById('navbar-toggle');
    const navbarMenu = document.getElementById('navbar-menu');

    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
            navbarToggle.classList.toggle('active');
        });

    // Close the mobile menu when a link is clicked
    navbarMenu.addEventListener('click', function(e) {
        if (e.target.classList.contains('navbar-item')) {
            navbarMenu.classList.remove('active');
        }
    });

    // Toggle user menu dropdown
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
        userMenu.addEventListener('click', function(e) {
            this.querySelector('.dropdown-content').style.display = 
                this.querySelector('.dropdown-content').style.display === 'block' ? 'none' : 'block';
            e.stopPropagation();
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            userMenu.querySelector('.dropdown-content').style.display = 'none';
        });
    }
});