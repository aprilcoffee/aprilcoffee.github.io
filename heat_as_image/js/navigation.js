function loadNavigation() {
    const navigation = `
        <a href="/heat_as_image/index.html"><h2>Heat as (Generative) Image Making</h2></a>
        <ul>
            <li><a href="/heat_as_image/index.html">Abstract</a></li>
            <li><a href="/heat_as_image/prologue.html">Prologue</a></li>
            <li class="has-submenu">
                <div class="section-header">
                    <a href="/heat_as_image/introduction/index.html">Introduction</a>
                </div>
                <ul class="submenu">
                    <li><a href="/heat_as_image/introduction/cybernetic.html">A (Possibly) Cybernetic Approach</a></li>
                    <li><a href="/heat_as_image/introduction/unexpected-imagery.html">The Unexpected Imagery</a></li>
                    <li><a href="/heat_as_image/introduction/computer-limits.html">Because my computer can't run</a></li>
                    <li><a href="/heat_as_image/introduction/future-self.html">Note for the future self</a></li>
                </ul>
            </li>
            <li class="has-submenu">
                <div class="section-header">
                    <a href="/heat_as_image/loss-function/index.html">The Loss Function in Our Practices</a>
                </div>
                <ul class="submenu">
                    <li><a href="/heat_as_image/loss-function/what-you-see.html">What you see is not inside the machine</a></li>
                    <li><a href="/heat_as_image/loss-function/purple-coincidence.html">The purple coincidence</a></li>
                    <li><a href="/heat_as_image/loss-function/eliza-effect.html">Eliza Effect</a></li>
                    <li><a href="/heat_as_image/loss-function/specificity.html">Specificity in Imaging</a></li>
                    <li><a href="/heat_as_image/loss-function/statistical-index.html">Statistical Index and Embeddings</a></li>
                </ul>
            </li>
            <li class="has-submenu">
                <div class="section-header">
                    <a href="/heat_as_image/optimized-noise/index.html">Optimized Noise Maker</a>
                </div>
                <ul class="submenu">
                    <li><a href="/heat_as_image/optimized-noise/measuring-coffee.html">Measuring Coffee</a></li>
                    <li><a href="/heat_as_image/optimized-noise/computer-vision.html">When Computer Squeeze its eyes</a></li>
                    <li><a href="/heat_as_image/optimized-noise/self-critic.html">Self-critic machine</a></li>
                    <li><a href="/heat_as_image/optimized-noise/biochemical.html">A biochemical problem</a></li>
                    <li><a href="/heat_as_image/optimized-noise/attention.html">Attending to Attention</a></li>
                    <li><a href="/heat_as_image/optimized-noise/denoising.html">Denoising the noise</a></li>
                </ul>
            </li>
            <li class="has-submenu">
                <div class="section-header">
                    <a href="/heat_as_image/materiality/index.html">Materiality of Artificial Intelligence</a>
                </div>
                <ul class="submenu">
                    <li><a href="/heat_as_image/materiality/commodity.html">Art as commodity and commodity as art</a></li>
                    <li><a href="/heat_as_image/materiality/gpu.html">Graphics Processing Units</a></li>
                    <li><a href="/heat_as_image/materiality/sand.html">Sand, Quartz and Silicon</a></li>
                    <li><a href="/heat_as_image/materiality/touches.html">All touches leave marks</a></li>
                    <li><a href="/heat_as_image/materiality/cleanrooms.html">Cleanrooms and Chokepoints</a></li>
                    <li><a href="/heat_as_image/materiality/fabrications.html">Fabrications</a></li>
                    <li><a href="/heat_as_image/materiality/taiwan.html">The Taiwan Dilemma</a></li>
                </ul>
            </li>
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
                const parentSubmenu = link.closest('.has-submenu');
                if (parentSubmenu) {
                    parentSubmenu.classList.add('open');
                }
                break;
            }
        }

        // Add click handlers for section headers
        const sectionHeaders = nav.querySelectorAll('.section-header');
        sectionHeaders.forEach(header => {
            header.addEventListener('click', (e) => {
                if (e.target.tagName === 'A') return;
                const menu = header.closest('.has-submenu');
                menu.classList.toggle('open');
            });
        });
    }
}

// Load navigation when DOM is ready
document.addEventListener('DOMContentLoaded', loadNavigation);