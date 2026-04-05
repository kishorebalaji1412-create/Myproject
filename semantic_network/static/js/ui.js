/**
 * UI Handler - Non-graph UI interactions
 * Sidebar management, mobile menu, and general utilities
 */

document.addEventListener('DOMContentLoaded', () => {
    setupMobileUI();
    setupSidebarToggle();
});

function setupMobileUI() {
    // Detect mobile
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            // Add mobile sidebar toggle
            const graphContainer = document.querySelector('.graph-container');
            if (graphContainer) {
                graphContainer.addEventListener('click', (e) => {
                    if (e.target.id === 'graph' || e.target === graphContainer) {
                        sidebar.classList.remove('active');
                    }
                });
            }
        }
    }
}

function setupSidebarToggle() {
    // Mobile hamburger-like sidebar toggle
    window.addEventListener('resize', () => {
        const sidebar = document.querySelector('.sidebar');
        if (window.innerWidth > 768) {
            sidebar?.classList.remove('active');
        }
    });
}

// Add touch support for mobile D3 graph
function setupTouchGestures() {
    const graph = document.getElementById('graph');
    
    if (!graph) return;
    
    let touchStartDistance = 0;
    
    graph.addEventListener('touchstart', (e) => {
        if (e.touches.length === 2) {
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            touchStartDistance = Math.sqrt(dx * dx + dy * dy);
        }
    });
    
    graph.addEventListener('touchmove', (e) => {
        if (e.touches.length === 2) {
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const scale = distance / touchStartDistance;
            
            if (Math.abs(scale - 1) > 0.1) {
                // Pinch zoom detected
                e.preventDefault();
            }
        }
    });
}

// Utility function to close menu when item is clicked
document.addEventListener('click', (e) => {
    const menu = document.getElementById('menu-content');
    const toggle = document.getElementById('menu-toggle');
    
    if (menu && menu.classList.contains('active')) {
        if (!toggle.contains(e.target) && !menu.contains(e.target)) {
            menu.classList.remove('active');
        }
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K or Cmd + F for search
    if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === '/')) {
        e.preventDefault();
        document.getElementById('search-input')?.focus();
    }
    
    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.getElementById('search-input');
        if (searchInput && searchInput.value) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('keyup'));
        }
    }
});

// Setup touch gesture support
if ('ontouchstart' in window) {
    document.addEventListener('DOMContentLoaded', setupTouchGestures);
}
