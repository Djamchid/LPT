// Table of Contents generation
document.addEventListener('DOMContentLoaded', function() {
    generateTableOfContents();
    initializeScrollSpy();
    initializeBackToTop();
    initializeImageZoom();
});

// Generate table of contents from article sections
function generateTableOfContents() {
    const tocNav = document.getElementById('toc-nav');
    const sections = document.querySelectorAll('.section');

    sections.forEach(section => {
        const sectionId = section.getAttribute('id');
        // Skip sections without IDs or empty IDs
        if (!sectionId) return;

        const headings = section.querySelectorAll('h1, h2, h3');

        headings.forEach(heading => {
            const link = document.createElement('a');
            const headingText = heading.textContent;

            // If the heading doesn't have an ID, create one
            if (!heading.id) {
                // For the first h2 in a section, use the section ID directly
                const isFirstH2 = heading.tagName === 'H2' &&
                                 section.querySelectorAll('h2').length === 1;

                if (isFirstH2) {
                    heading.id = sectionId;
                } else {
                    // For other headings, generate a unique ID
                    heading.id = sectionId + '-' + headingText.toLowerCase()
                        .replace(/[^a-z0-9]+/g, '-')
                        .replace(/^-+|-+$/g, '');
                }
            }

            link.href = '#' + heading.id;
            link.textContent = headingText;

            // Add class based on heading level
            if (heading.tagName === 'H3') {
                link.classList.add('toc-level-3');
            } else if (heading.tagName === 'H1') {
                link.classList.add('toc-level-1');
            }

            tocNav.appendChild(link);
        });
    });
}

// Scroll spy - highlight current section in TOC
function initializeScrollSpy() {
    const tocLinks = document.querySelectorAll('#toc-nav a');
    const sections = document.querySelectorAll('.section h1, .section h2, .section h3');

    function updateActiveLink() {
        let currentSection = null;
        const scrollPosition = window.scrollY + 100;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (scrollPosition >= sectionTop) {
                currentSection = section;
            }
        });

        tocLinks.forEach(link => {
            link.classList.remove('active');
            if (currentSection && link.getAttribute('href') === '#' + currentSection.id) {
                link.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', updateActiveLink);
    updateActiveLink();
}

// Back to top button
function initializeBackToTop() {
    const backToTopButton = document.getElementById('backToTop');

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    });
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Image zoom functionality
function initializeImageZoom() {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImg');
    const captionText = document.getElementById('caption');

    // Close modal when clicking outside the image
    modal.addEventListener('click', function(e) {
        if (e.target === modal || e.target.className === 'close') {
            closeModal();
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

function zoomImage(img) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImg');
    const captionText = document.getElementById('caption');

    modal.style.display = 'block';
    modalImg.src = img.src;
    captionText.innerHTML = img.alt;

    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('imageModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Smooth scrolling for TOC links
document.addEventListener('click', function(e) {
    if (e.target.matches('#toc-nav a')) {
        e.preventDefault();
        const targetId = e.target.getAttribute('href');
        const targetElement = document.querySelector(targetId);

        if (targetElement) {
            const offsetTop = targetElement.offsetTop - 20;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    }
});

// Print functionality
function printArticle() {
    window.print();
}

// Export to PDF (requires browser print to PDF)
function exportToPDF() {
    window.print();
}

// Highlight search results (optional feature)
function highlightText(searchTerm) {
    if (!searchTerm) return;

    const article = document.querySelector('.article');
    const content = article.innerHTML;
    const regex = new RegExp(searchTerm, 'gi');

    article.innerHTML = content.replace(regex, match =>
        `<mark>${match}</mark>`
    );
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + P for print
    if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        printArticle();
    }

    // Ctrl/Cmd + Home to scroll to top
    if ((e.ctrlKey || e.metaKey) && e.key === 'Home') {
        e.preventDefault();
        scrollToTop();
    }
});

// Add animation to figures on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', function() {
    const figures = document.querySelectorAll('.figure');
    figures.forEach(figure => {
        figure.style.opacity = '0';
        figure.style.transform = 'translateY(20px)';
        figure.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(figure);
    });
});
