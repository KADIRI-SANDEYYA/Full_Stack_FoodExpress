/* home.js */
// ========================================
// HERO CAROUSEL - AUTOMATIC SLIDESHOW
// ========================================

document.addEventListener('DOMContentLoaded', function () {
    const heroSection = document.querySelector('.hero-section');
    const carousel = document.querySelector('.hero-carousel');
    const dotsContainer = document.querySelector('.hero-dots');
    const prevBtn = document.querySelector('.hero-prev');
    const nextBtn = document.querySelector('.hero-next');

    if (!heroSection || !carousel || !dotsContainer || !prevBtn || !nextBtn) {
        return;
    }

    const categoryImagesElement = document.getElementById("category-images");
    const categoryImages = categoryImagesElement
        ? JSON.parse(categoryImagesElement.textContent)
        : {};

    // Slide data - you can customize these or fetch from backend
    const slides = [
        {
            image: categoryImages.biryani || 'https://images.unsplash.com/photo-1563379091339-03246963d96c?w=1200&h=600&fit=crop',
            badge: 'Best Seller',
            title: 'Authentic Hyderabadi Biryani Delivered Fresh',
            description: 'Savor the rich aroma and authentic taste of Hyderabadi biryani from the city\'s most loved restaurants.',
            buttonText: 'Order Biryani',
            buttonLink: heroSection?.dataset?.restaurantsUrl || '/restaurants/'
        },
        {
            image: categoryImages.pizza || 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=1200&h=600&fit=crop',
            badge: 'Hot Deals',
            title: 'Freshly Baked Pizza for Every Craving',
            description: 'Enjoy cheesy pizzas loaded with premium toppings from your favorite pizza brands.',
            buttonText: 'Explore Pizza',
            buttonLink: heroSection?.dataset?.restaurantsUrl || '/restaurants/'
        },
        {
            image: categoryImages.burger || 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1200&h=600&fit=crop',
            badge: 'Fast Food',
            title: 'Juicy Burgers & Crispy Fried Chicken',
            description: 'Treat yourself to burgers, crispy chicken, wraps, and fries delivered hot.',
            buttonText: 'Order Fast Food',
            buttonLink: heroSection?.dataset?.restaurantsUrl || '/restaurants/'
        },
        {
            image: categoryImages.coffee || 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1200&h=600&fit=crop',
            badge: 'Coffee Time',
            title: 'Premium Coffee, Cakes & Desserts',
            description: 'Refresh your day with coffee, milkshakes, pastries, and desserts.',
            buttonText: 'Discover Café',
            buttonLink: heroSection?.dataset?.restaurantsUrl || '/restaurants/'
        },
        {
            image: categoryImages.chinese || 'https://images.unsplash.com/photo-1512058564366-18510be2db19?w=1200&h=600&fit=crop',
            badge: 'Chef Special',
            title: 'Chinese, Tandoori & Family Meals',
            description: 'From fried rice and noodles to sizzling tandoori platters.',
            buttonText: 'Explore Menu',
            buttonLink: heroSection?.dataset?.restaurantsUrl || '/restaurants/'
        }
    ];

    let currentSlide = 0;
    let slideInterval = null;
    const INTERVAL_TIME = 5000;

    // Create slides
    function createSlides() {
        carousel.innerHTML = '';
        slides.forEach((slide, index) => {
            const slideDiv = document.createElement('div');
            slideDiv.className = `hero-slide ${index === 0 ? 'active' : ''}`;
            slideDiv.style.backgroundImage = `linear-gradient(135deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 60%, rgba(0,0,0,0.1) 100%), url('${slide.image}')`;
            slideDiv.innerHTML = `
                <div class="hero-slide-content">
                    <span class="hero-slide-badge">${slide.badge}</span>
                    <h1 class="hero-slide-title">${slide.title}</h1>
                    <p class="hero-slide-desc">${slide.description}</p>
                    <a href="${slide.buttonLink}" class="hero-slide-btn">
                        ${slide.buttonText}
                        <i class="fa-solid fa-arrow-right"></i>
                    </a>
                </div>
            `;
            carousel.appendChild(slideDiv);
        });
    }

    // Create dots
    function createDots() {
        dotsContainer.innerHTML = '';
        slides.forEach((_, index) => {
            const dot = document.createElement('button');
            dot.className = `hero-dot ${index === 0 ? 'active' : ''}`;
            dot.setAttribute('role', 'tab');
            dot.setAttribute('aria-label', `Go to slide ${index + 1}`);
            dot.dataset.index = index;
            dot.addEventListener('click', () => goToSlide(index));
            dotsContainer.appendChild(dot);
        });
    }

    // Go to specific slide
    function goToSlide(index) {
        const slideElements = carousel.querySelectorAll('.hero-slide');
        const dots = dotsContainer.querySelectorAll('.hero-dot');

        // Remove active from all
        slideElements.forEach(el => el.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));

        // Add active to current
        currentSlide = index;
        slideElements[currentSlide].classList.add('active');
        dots[currentSlide].classList.add('active');
    }

    // Next slide
    function nextSlide() {
        const next = (currentSlide + 1) % slides.length;
        goToSlide(next);
    }

    // Previous slide
    function prevSlide() {
        const prev = (currentSlide - 1 + slides.length) % slides.length;
        goToSlide(prev);
    }

    // Start autoplay
    function startAutoplay() {
        stopAutoplay();
        slideInterval = setInterval(nextSlide, INTERVAL_TIME);
    }

    // Stop autoplay
    function stopAutoplay() {
        if (slideInterval) {
            clearInterval(slideInterval);
            slideInterval = null;
        }
    }

    // Reset autoplay on user interaction
    function resetAutoplay() {
        stopAutoplay();
        startAutoplay();
    }

    // Initialize
    createSlides();
    createDots();
    startAutoplay();

    // Event listeners
    nextBtn.addEventListener('click', () => {
        nextSlide();
        resetAutoplay();
    });

    prevBtn.addEventListener('click', () => {
        prevSlide();
        resetAutoplay();
    });

    // Pause on hover
    carousel.addEventListener('mouseenter', stopAutoplay);
    carousel.addEventListener('mouseleave', startAutoplay);

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') {
            nextSlide();
            resetAutoplay();
        } else if (e.key === 'ArrowLeft') {
            prevSlide();
            resetAutoplay();
        }
    });

    // ========================================
    // WISHLIST BUTTON TOGGLE
    // ========================================
    const wishlistButtons = document.querySelectorAll('.food-wishlist, .wishlist');
    wishlistButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const icon = this.querySelector('i');
            const isSaved = this.getAttribute('aria-pressed') === 'true';

            if (isSaved) {
                icon.className = 'fa-regular fa-heart';
                this.setAttribute('aria-pressed', 'false');
            } else {
                icon.className = 'fa-solid fa-heart';
                this.setAttribute('aria-pressed', 'true');
                // Add animation class
                this.style.animation = 'none';
                setTimeout(() => {
                    this.style.animation = 'wishlist-pop 0.4s ease';
                }, 10);
            }
        });
    });

    // Add wishlist animation
    const styleSheet = document.createElement("style");
    styleSheet.textContent = `
        @keyframes wishlist-pop {
            0% { transform: scale(1); }
            50% { transform: scale(1.3); }
            100% { transform: scale(1); }
        }
    `;
    document.head.appendChild(styleSheet);
});
