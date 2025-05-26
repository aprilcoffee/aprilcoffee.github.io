document.addEventListener('DOMContentLoaded', function() {
    // Initialize footnotes
    const footnotes = document.querySelectorAll('.footnote');
    const modal = document.getElementById('footnote-modal');
    const modalContent = document.getElementById('footnote-content');
    const closeBtn = document.querySelector('.close');

    // Handle footnote clicks
    footnotes.forEach(footnote => {
        footnote.addEventListener('click', function(e) {
            e.preventDefault();
            const footnoteId = this.getAttribute('data-footnote');
            const footnoteText = document.querySelector(`#footnote-${footnoteId}`).innerHTML;
            modalContent.innerHTML = footnoteText;
            modal.style.display = 'block';
        });
    });

    // Close modal when clicking the close button
    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Handle smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const headerOffset = 20;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Highlight current section in navigation
    const sections = document.querySelectorAll('article section');
    const navLinks = document.querySelectorAll('.table-of-contents a');

    function highlightCurrentSection() {
        let currentSection = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= sectionTop - 100) {
                currentSection = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').includes(currentSection)) {
                link.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', highlightCurrentSection);
    highlightCurrentSection(); // Initial call

    // Handle responsive navigation
    const handleResize = () => {
        const isMobile = window.innerWidth <= 768;
        const nav = document.querySelector('.table-of-contents');
        
        if (isMobile) {
            nav.style.height = 'auto';
        } else {
            nav.style.height = '100vh';
        }
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // Initial call
}); 