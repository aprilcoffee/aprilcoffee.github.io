function loadNavigation() {
    const navigation = `
        <h2>Heat as (Generative) Image Making</h2>
        <ul>
            <li><a href="/heat_as_image/index.html">Abstract</a></li>
            <li><a href="/heat_as_image/prologue.html">Prologue</a></li>
            <li><a href="/heat_as_image/introduction/index.html">Introduction</a></li>
            <li><a href="/heat_as_image/loss-function/index.html">The Loss Function in Our Practices</a></li>
            <li><a href="/heat_as_image/optimized-noise/index.html">Optimized Noise Maker</a></li>
            <li><a href="/heat_as_image/materiality/index.html">Materiality of Artificial Intelligence</a></li>
            <li><a href="/heat_as_image/outlook.html">Outlook and Reflection</a></li>
            <li><a href="/heat_as_image/bibliography.html">Bibliography</a></li>
        </ul>
    `;
    
    const nav = document.querySelector('.table-of-contents');
    if (nav) {
        nav.innerHTML = navigation;
        
        // Set active class based on current page
        const currentPath = window.location.pathname;
        const links = nav.getElementsByTagName('a');
        for (let link of links) {
            if (currentPath.endsWith(link.getAttribute('href'))) {
                link.classList.add('active');
                break;
            }
        }
    }
}

// Load navigation when DOM is ready
document.addEventListener('DOMContentLoaded', loadNavigation); 