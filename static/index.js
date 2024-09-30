// Add an event listener to the window object to run the JavaScript code after the DOM is fully loaded
window.addEventListener('DOMContentLoaded', function() {
    // Get all the page-link-button elements
    const buttons = document.querySelectorAll('.page-link-button');

    // Loop through each button
    buttons.forEach(function(button) {
        // Add a click event listener to each button
        button.addEventListener('click', function(event) {
            // Prevent the default behavior of the link (i.e., navigating to a new page)
            event.preventDefault();
            
            // Get the URL from the href attribute of the clicked button
            const url = button.getAttribute('href');
            
            // Log the URL to the console (you can replace this with your desired action)
            console.log('Navigating to:', url);
            
            // You can also use window.location.href to navigate to the URL:
            // window.location.href = url;
        });
    });
});
