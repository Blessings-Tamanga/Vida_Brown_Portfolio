// Theme Toggle Logic
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const htmlEl = document.documentElement;

// Load saved theme preference or default to dark
const savedTheme = localStorage.getItem('theme') || 'dark';
if (savedTheme === 'light') {
    htmlEl.classList.remove('dark');
    themeIcon.textContent = 'light_mode';
}

themeToggle.addEventListener('click', () => {
    htmlEl.classList.toggle('dark');
    const isDark = htmlEl.classList.contains('dark');
    themeIcon.textContent = isDark ? 'dark_mode' : 'light_mode';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

// Header Scroll Effect
const header = document.querySelector('.site-header');
window.addEventListener('scroll', () => {
    header.style.padding = window.scrollY > 50 ? '8px 64px' : '16px 64px';
});

// Parallax effect for hero portrait
const heroImage = document.querySelector('.hero-image-wrapper');
window.addEventListener('mousemove', (e) => {
    if (!heroImage) return;
    const speed = 0.02;
    const x = (window.innerWidth - e.pageX * 4) * speed;
    const y = (window.innerHeight - e.pageY * 4) * speed;
    heroImage.style.transform = `translate(${x}px, ${y}px)`;
});