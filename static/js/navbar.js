document.addEventListener('DOMContentLoaded', function() {
    const userMenu = document.querySelector('.user-menu');
    const dropdownContent = document.querySelector('.dropdown-content');

    if (userMenu && dropdownContent) {
        userMenu.addEventListener('click', function(e) {
            e.stopPropagation();
            if (dropdownContent.style.display === 'block') {
                dropdownContent.style.display = 'none';
                console.log('Dropdown hidden');
            } else {
                dropdownContent.style.display = 'block';
                console.log('Dropdown shown');
            }
        });

        document.addEventListener('click', function(e) {
            if (!userMenu.contains(e.target)) {
                dropdownContent.style.display = 'none';
                console.log('Dropdown hidden (clicked outside)');
            }
        });
    } else {
        console.log('User menu or dropdown content not found');
    }
});