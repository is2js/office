window.addEventListener('load', function(e) {
    document.querySelector('.footer #copyright #year').innerHTML = new Date().getFullYear() + ' ';
});


function getCurrentPath() {
    return window.location.pathname
}
