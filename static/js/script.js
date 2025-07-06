// static/js/scripts.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('Document ready!');
    
    // Example event listener
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            alert('Button clicked!');
        });
    });
});