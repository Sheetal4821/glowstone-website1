/**
 * Glowstone - Main JavaScript
 * Clean, responsive, performant
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // If page loaded with hash (e.g. #collection), show target section and scroll to it
    // (animate-on-scroll starts with opacity:0, so content is invisible until .visible is added)
    function showHashTarget() {
        var hash = window.location.hash;
        if (hash) {
            var target = document.querySelector(hash);
            if (target) {
                var animEls = target.querySelectorAll('.animate-on-scroll');
                if (animEls.length) {
                    animEls.forEach(function(el) { el.classList.add('visible'); });
                } else if (target.classList.contains('animate-on-scroll')) {
                    target.classList.add('visible');
                }
                // Explicitly scroll to target (fixes navigation from other pages)
                requestAnimationFrame(function() {
                    requestAnimationFrame(function() {
                        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    });
                });
            }
        }
    }
    showHashTarget();
    window.addEventListener('hashchange', showHashTarget);
    // Re-scroll on full load (handles layout shift from images when coming from another page)
    if (window.location.hash) {
        window.addEventListener('load', function() {
            var target = document.querySelector(window.location.hash);
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    }

    // Scroll-triggered animations (Intersection Observer)
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    if (animateElements.length > 0) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, {
            root: null,
            rootMargin: '0px 0px -80px 0px',
            threshold: 0.1
        });
        animateElements.forEach(function(el) { observer.observe(el); });
    }

    // Navbar scroll effect - transparent over first section (hero), solid after (same on all pages)
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        // Detect first section: scroll-driven heroes (#gs-hero, #sus-hero, #care-hero, .inst-step) or page heroes (.about-hero, etc.)
        var heroScrollSection = document.querySelector('#gs-hero, #sus-hero, #care-hero, .inst-step');
        var pageHero = document.querySelector('.about-hero, .contact-hero, .faq-hero, .tech-hero, .sh');

        function updateNavbarScroll() {
            var scrollY = window.scrollY || window.pageYOffset;
            var threshold;
            if (heroScrollSection) {
                threshold = heroScrollSection.offsetHeight || window.innerHeight * 5;
            } else if (pageHero) {
                threshold = Math.min(pageHero.offsetHeight || 300, window.innerHeight * 0.8);
            } else {
                threshold = 50;
            }
            navbar.classList.toggle('scrolled', scrollY > threshold);
        }
        var scrollTimeout;
        window.addEventListener('scroll', function() {
            if (scrollTimeout) return;
            scrollTimeout = setTimeout(function() {
                updateNavbarScroll();
                scrollTimeout = null;
            }, 16);
        }, { passive: true });
        window.addEventListener('resize', updateNavbarScroll);
        window.addEventListener('orientationchange', function() {
            setTimeout(updateNavbarScroll, 100);
        });
        updateNavbarScroll();
    }

    // Footer expand/collapse (Caesarstone-style: click + to expand)
    var footerToggle = document.getElementById('footerToggle');
    var footerExpandable = document.querySelector('.footer-expandable');
    if (footerToggle && footerExpandable) {
        footerToggle.addEventListener('click', function() {
            var expanded = footerExpandable.classList.toggle('expanded');
            footerToggle.setAttribute('aria-expanded', expanded);
            if (expanded) {
                var footer = document.getElementById('main-footer');
                if (footer) {
                    footer.scrollIntoView({ behavior: 'auto', block: 'end' });
                }
            }
        });
    }

    // Step 2: Website controls video with scroll (TinyPod-style)
    // Scrolling down → video plays forward | Scrolling up → video reverses
    // Step 3: GSAP ScrollTrigger for smooth sync, pin, and professional feel
    var heroSection = document.querySelector('.hero.hero-scroll-driven');
    var heroWrap = document.querySelector('.hero-video-wrap');
    var heroVideo = document.getElementById('hero-video');

    if (heroSection && heroWrap && heroVideo && typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined' && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        gsap.registerPlugin(ScrollTrigger);

        var scrollVideoInited = false;
        function initScrollVideo() {
            if (scrollVideoInited) return;
            heroVideo.pause();
            var duration = heroVideo.duration;
            if (!duration || !isFinite(duration)) return;
            scrollVideoInited = true;

            ScrollTrigger.create({
                trigger: heroSection,
                start: 'top top',
                end: '+=500%',
                scrub: 1.5,
                pin: true,
                anticipatePin: 1,
                onUpdate: function(self) {
                    var scrollPercent = self.progress;
                    heroVideo.currentTime = scrollPercent * duration;
                    var hint = heroSection.querySelector('.hero-scroll-hint');
                    if (hint) hint.style.opacity = scrollPercent > 0.05 ? Math.max(0, 1 - scrollPercent * 3) : '0.85';
                }
            });
        }

        heroVideo.addEventListener('loadedmetadata', initScrollVideo);
        heroVideo.addEventListener('loadeddata', initScrollVideo);
        heroVideo.addEventListener('canplay', initScrollVideo);
        if (heroVideo.readyState >= 1) initScrollVideo();
    } else if (heroSection && heroVideo && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        // Fallback: vanilla scroll-to-video when GSAP unavailable (Step 2 concept)
        var scrollRange = 3000;
        var ticking = false;
        heroVideo.pause();
        function updateVideoFromScroll() {
            var scrollY = window.scrollY || window.pageYOffset;
            var scrollPercent = Math.min(1, Math.max(0, scrollY / scrollRange));
            if (heroVideo.duration && isFinite(heroVideo.duration)) {
                heroVideo.currentTime = scrollPercent * heroVideo.duration;
            }
            ticking = false;
        }
        heroVideo.addEventListener('loadedmetadata', updateVideoFromScroll);
        window.addEventListener('scroll', function() {
            if (!ticking) {
                requestAnimationFrame(updateVideoFromScroll);
                ticking = true;
            }
        }, { passive: true });
    } else if (heroWrap && !heroSection) {
        var tickingP = false;
        function updateParallax() {
            var scrollY = window.scrollY || window.pageYOffset;
            heroWrap.style.transform = 'translate3d(0, ' + (scrollY * 0.4) + 'px, 0)';
            tickingP = false;
        }
        window.addEventListener('scroll', function() {
            if (!tickingP) { requestAnimationFrame(updateParallax); tickingP = true; }
        }, { passive: true });
        updateParallax();
    }

    // Contact form
    const contactForm = document.getElementById('contactForm');
    const messageInput = document.getElementById('message');
    const charCount = document.querySelector('.char-count');

    if (messageInput && charCount) {
        var maxLen = messageInput.getAttribute('maxlength') || 200;
        messageInput.addEventListener('input', function() {
            charCount.textContent = this.value.length + ' / ' + maxLen + ' characters';
        });
    }

    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
            this.reset();
            if (charCount) {
                var max = messageInput ? (messageInput.getAttribute('maxlength') || 200) : 200;
                charCount.textContent = '0 / ' + max + ' characters';
            }
        });
    }

    // Close mobile menu when clicking a nav link (smooth UX on mobile)
    document.querySelectorAll('.nav-link').forEach(function(link) {
        link.addEventListener('click', function() {
            var collapse = document.querySelector('.navbar-collapse');
            if (collapse && collapse.classList.contains('show')) {
                var toggle = document.querySelector('.navbar-toggler');
                if (toggle) toggle.click();
            }
        });
    });

    // Hero video - smooth playback (skip for scroll-driven hero, which uses scrub)
    var heroVideoEl = document.querySelector('.hero-video-element');
    var isScrollDriven = !!document.querySelector('.hero.hero-scroll-driven');
    if (heroVideoEl && !isScrollDriven && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        heroVideoEl.play().catch(function() {});
        heroVideoEl.addEventListener('loadeddata', function() {
            heroVideoEl.play().catch(function() {});
        });
    }

    // Render Lightbox - click any product render to open full-size with slider
    (function initRenderLightbox() {
        var items = document.querySelectorAll('.product-render-item');
        if (items.length === 0) return;

        var lightbox = document.createElement('div');
        lightbox.className = 'render-lightbox';
        lightbox.setAttribute('role', 'dialog');
        lightbox.setAttribute('aria-label', 'Image gallery');
        lightbox.innerHTML = '<button type="button" class="render-lightbox-close" aria-label="Close">&times;</button>' +
            '<button type="button" class="render-lightbox-prev" aria-label="Previous image">&lsaquo;</button>' +
            '<button type="button" class="render-lightbox-next" aria-label="Next image">&rsaquo;</button>' +
            '<div class="render-lightbox-content"></div>' +
            '<span class="render-lightbox-counter"></span>';
        document.body.appendChild(lightbox);

        var closeBtn = lightbox.querySelector('.render-lightbox-close');
        var prevBtn = lightbox.querySelector('.render-lightbox-prev');
        var nextBtn = lightbox.querySelector('.render-lightbox-next');
        var content = lightbox.querySelector('.render-lightbox-content');
        var counter = lightbox.querySelector('.render-lightbox-counter');

        var images = [];
        var currentIndex = 0;

        function openLightbox(index) {
            currentIndex = index;
            updateLightbox();
            lightbox.classList.add('active');
            document.body.style.overflow = 'hidden';
        }

        function closeLightbox() {
            lightbox.classList.remove('active');
            document.body.style.overflow = '';
        }

        function updateLightbox() {
            var img = images[currentIndex];
            if (!img) return;
            content.innerHTML = '<img src="' + img.src + '" alt="' + (img.alt || 'Render') + '">';
            counter.textContent = (currentIndex + 1) + ' / ' + images.length;
            prevBtn.disabled = currentIndex === 0;
            nextBtn.disabled = currentIndex === images.length - 1;
        }

        function goPrev() {
            if (currentIndex > 0) {
                currentIndex--;
                updateLightbox();
            }
        }

        function goNext() {
            if (currentIndex < images.length - 1) {
                currentIndex++;
                updateLightbox();
            }
        }

        closeBtn.addEventListener('click', closeLightbox);
        prevBtn.addEventListener('click', goPrev);
        nextBtn.addEventListener('click', goNext);

        lightbox.addEventListener('click', function(e) {
            if (e.target === lightbox) closeLightbox();
        });

        document.addEventListener('keydown', function(e) {
            if (!lightbox.classList.contains('active')) return;
            if (e.key === 'Escape') closeLightbox();
            if (e.key === 'ArrowLeft') goPrev();
            if (e.key === 'ArrowRight') goNext();
        });

        items.forEach(function(item, itemIndex) {
            var img = item.querySelector('img');
            if (!img) return;
            item.addEventListener('click', function() {
                var container = item.closest('.product-renders');
                images = Array.from(container.querySelectorAll('.product-render-item img')).map(function(i) { return i; });
                var idx = Array.from(container.querySelectorAll('.product-render-item')).indexOf(item);
                openLightbox(idx >= 0 ? idx : 0);
            });
        });
    })();

});
