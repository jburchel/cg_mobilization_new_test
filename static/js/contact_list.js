// static/js/contact_list.js

const ContactList = new Vue({
    el: '#contacts-app',
    delimiters: ['[[', ']]'],  // Use different delimiters to avoid conflict with Django templates
    data: {
        contacts: []
    },
    mounted() {
        // Fetch contacts from Django API
        fetch('/api/contacts/')
            .then(response => response.json())
            .then(data => {
                this.contacts = data;
            });
    }
});