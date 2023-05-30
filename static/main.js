// Navbar
document.querySelectorAll(".nav-link").forEach((link) => {
    if (link.href === window.location.href) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
    }
});
// End of Navbar

// Back to Top Button
const scrollBtn = document.getElementById("btn-top")
const onScroll = () => {
    const scroll = document.documentElement.scrollTop
    if (scroll > 220) {
        scrollBtn.classList.add("show");
    } else {
        scrollBtn.classList.remove("show")
    }
};
window.addEventListener('scroll', onScroll);
// Scroll to top when button clicked
const scrollWindow = function () {
    if (window.scrollY != 0) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};
scrollBtn.addEventListener("click", scrollWindow);
// End of Back to Top Button
