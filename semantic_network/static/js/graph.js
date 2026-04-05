/**
 * D3.js Graph Visualization
 * Semantic Network Force-Directed Graph
 */

let graphData = null;
let simulation = null;
let svg = null;
let g = null;
let width = 0;
let height = 0;
let selectedNode = null;
let filteredNodeIds = new Set();
let isFiltered = false;

const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
const categoryColors = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Hide loading screen after a delay
    setTimeout(() => {
        document.getElementById('loading-screen').style.display = 'none';
    }, 1500);

    // Load initial graph
    await loadGraph();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load theme preference
    if (localStorage.getItem('theme') === 'light') {
        document.body.classList.add('light-mode');
        document.getElementById('theme-toggle').textContent = '☀️ Light';
    }
});

async function loadGraph(category = null) {
    try {
        const url = category ? `/api/graph?category=${encodeURIComponent(category)}` : '/api/graph';
        const response = await fetch(url);
        graphData = await response.json();
        
        renderGraph();
        updateStats();
        updateCategoryFilters();
        
    } catch (error) {
        console.error('Error loading graph:', error);
        showToast('Failed to load graph: ' + error.message, 'error');
    }
}

function renderGraph() {
    // Clear previous graph
    d3.select('#graph').selectAll('*').remove();
    
    width = document.getElementById('graph').clientWidth;
    height = document.getElementById('graph').clientHeight;
    
    // Build category color map
    graphData.nodes.forEach(node => {
        if (!categoryColors[node.category]) {
            const color = node.color || colorScale(node.category);
            categoryColors[node.category] = color;
        }
    });
    
    // Create SVG
    svg = d3.select('#graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Add background
    svg.append('rect')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', window.matchMedia('(prefers-color-scheme: light)').matches ? '#f5f5f5' : '#0f0f1a')
        .on('click', handleCanvasClick);
    
    // Create group for zoom/pan
    g = svg.append('g');
    
    // Add zoom behavior
    const zoom = d3.zoom()
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    // Force simulation
    simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.links)
            .id(d => d.id)
            .distance(80)
            .strength(0.5))
        .force('charge', d3.forceManyBody()
            .strength(-400)
            .distanceMax(300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(35))
        .on('tick', ticked);
    
    // Draw links
    const links = g.selectAll('line')
        .data(graphData.links)
        .enter()
        .append('line')
        .attr('class', 'link')
        .attr('stroke-width', d => Math.sqrt(d.weight || 1));
    
    // Draw nodes
    const nodes = g.selectAll('circle')
        .data(graphData.nodes)
        .enter()
        .append('g')
        .attr('class', 'node')
        .on('click', handleNodeClick)
        .on('mouseover', handleNodeHover)
        .on('mouseout', handleNodeUnhover);
    
    nodes.append('circle')
        .attr('r', d => 20 + (d.frequency || 0) * 2)
        .attr('fill', d => categoryColors[d.category] || '#00ff88')
        .attr('stroke', '#fff')
        .attr('stroke-width', 2);
    
    nodes.append('text')
        .attr('dy', '.3em')
        .attr('text-anchor', 'middle')
        .text(d => d.label.length > 15 ? d.label.substring(0, 12) + '...' : d.label);
    
    // Add drag behavior
    nodes.call(d3.drag()
        .on('start', dragStarted)
        .on('drag', dragged)
        .on('end', dragEnded));
    
    function ticked() {
        links
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        nodes
            .attr('transform', d => `translate(${d.x},${d.y})`);
    }
}

function handleNodeClick(event, d) {
    event.stopPropagation();
    selectedNode = d;
    updateNodePanel(d);
    highlightNode(d);
}

function handleCanvasClick(event) {
    selectedNode = null;
    updateNodePanel(null);
    unhighlightAll();
}

function handleNodeHover(event, d) {
    const tooltip = document.getElementById('tooltip');
    tooltip.style.display = 'block';
    tooltip.style.left = (event.pageX + 10) + 'px';
    tooltip.style.top = (event.pageY - 10) + 'px';
    tooltip.innerHTML = `
        <strong>${d.label}</strong><br>
        <small>${d.category}</small><br>
        <small>${d.description || 'No description'}</small>
    `;
}

function handleNodeUnhover(event) {
    document.getElementById('tooltip').style.display = 'none';
}

function dragStarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragEnded(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

function updateNodePanel(node) {
    const panel = document.getElementById('node-panel');
    
    if (!node) {
        panel.innerHTML = '<p class="no-selection">Click a node to view details</p>';
        return;
    }
    
    // Find connected nodes
    const connectedIds = new Set();
    graphData.links.forEach(link => {
        if (link.source.id === node.id) connectedIds.add(link.target.id);
        if (link.target.id === node.id) connectedIds.add(link.source.id);
    });
    
    const connectedNodes = graphData.nodes.filter(n => connectedIds.has(n.id));
    
    panel.innerHTML = `
        <div class="node-details">
            <div class="node-detail-item">
                <div class="detail-label">Label</div>
                <div class="detail-value">${node.label}</div>
            </div>
            <div class="node-detail-item">
                <div class="detail-label">Category</div>
                <div class="detail-value">${node.category}</div>
            </div>
            <div class="node-detail-item">
                <div class="detail-label">Description</div>
                <div class="detail-value">${node.description || 'No description'}</div>
            </div>
            <div class="node-detail-item">
                <div class="detail-label">Connections</div>
                <div class="detail-value">${connectedIds.size}</div>
            </div>
            ${connectedNodes.length > 0 ? `
                <div class="node-detail-item">
                    <div class="detail-label">Connected To</div>
                    <div class="detail-value" style="font-size: 0.9em;">
                        ${connectedNodes.slice(0, 5).map(n => n.label).join(', ')}
                        ${connectedNodes.length > 5 ? `... and ${connectedNodes.length - 5} more` : ''}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

function highlightNode(node) {
    const nodeIds = new Set([node.id]);
    const connectedIds = new Set();
    
    graphData.links.forEach(link => {
        if (link.source.id === node.id) {
            nodeIds.add(link.target.id);
            connectedIds.add(link.target.id);
        }
        if (link.target.id === node.id) {
            nodeIds.add(link.source.id);
            connectedIds.add(link.source.id);
        }
    });
    
    d3.selectAll('.node').classed('faded', d => !nodeIds.has(d.id));
    d3.selectAll('.node').classed('selected', d => d.id === node.id);
    d3.selectAll('.link').classed('highlighted', d => 
        (d.source.id === node.id || d.target.id === node.id)
    );
    d3.selectAll('.link').classed('faded', d => 
        !(d.source.id === node.id || d.target.id === node.id)
    );
}

function unhighlightAll() {
    d3.selectAll('.node').classed('faded', false).classed('selected', false);
    d3.selectAll('.link').classed('highlighted', false).classed('faded', false);
}

function updateStats() {
    document.getElementById('stat-nodes').textContent = graphData.nodes.length;
    document.getElementById('stat-edges').textContent = graphData.links.length;
    
    const categories = [...new Set(graphData.nodes.map(n => n.category))];
    document.getElementById('stat-categories').textContent = categories.length;
    
    const metadata = graphData.metadata || {};
    document.getElementById('stat-dataset').textContent = metadata.source || 'Kaggle';
    document.getElementById('dataset-badge').textContent = `📊 ${metadata.source || 'Kaggle'}`;
    document.getElementById('footer-dataset').textContent = metadata.name || 'Dataset';
}

function updateCategoryFilters() {
    const categories = [...new Set(graphData.nodes.map(n => n.category))];
    const container = document.getElementById('category-filter-container');
    
    container.innerHTML = '';
    
    categories.forEach(category => {
        const btn = document.createElement('button');
        btn.className = 'category-filter-btn';
        btn.textContent = `${category}`;
        btn.onclick = async () => {
            await loadGraph(category);
        };
        container.appendChild(btn);
    });
}

function setupEventListeners() {
    // Search
    const searchInput = document.getElementById('search-input');
    const searchClear = document.getElementById('search-clear');
    let searchTimeout;
    
    searchInput.addEventListener('keyup', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length === 0) {
            unhighlightAll();
            isFiltered = false;
            updateNodeCountBadge();
        } else {
            searchTimeout = setTimeout(() => performSearch(query), 300);
        }
    });
    
    searchClear.addEventListener('click', () => {
        searchInput.value = '';
        unhighlightAll();
        isFiltered = false;
        updateNodeCountBadge();
    });
    
    // Controls
    document.getElementById('zoom-in').addEventListener('click', () => {
        svg.transition().duration(750).call(
            d3.zoom().transform,
            d3.zoomIdentity.translate(width / 2, height / 2).scale(2)
        );
    });
    
    document.getElementById('zoom-out').addEventListener('click', () => {
        svg.transition().duration(750).call(
            d3.zoom().transform,
            d3.zoomIdentity.translate(width / 2, height / 2).scale(1)
        );
    });
    
    document.getElementById('reset-view').addEventListener('click', () => {
        svg.transition().duration(750).call(
            d3.zoom().transform,
            d3.zoomIdentity.translate(width / 2, height / 2)
        );
    });
    
    document.getElementById('reset-filter').addEventListener('click', () => {
        searchInput.value = '';
        unhighlightAll();
        isFiltered = false;
        updateNodeCountBadge();
    });
    
    // Dataset button
    document.getElementById('dataset-btn').addEventListener('click', () => {
        window.location.href = '/datasets';
    });
    
    document.getElementById('mobile-dataset-btn').addEventListener('click', () => {
        window.location.href = '/datasets';
    });
    
    // Export button
    document.getElementById('export-btn').addEventListener('click', () => {
        window.location.href = '/api/export';
        showToast('Graph exported successfully!', 'success');
    });
    
    document.getElementById('mobile-export-btn').addEventListener('click', () => {
        window.location.href = '/api/export';
        showToast('Graph exported successfully!', 'success');
    });
    
    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
    document.getElementById('mobile-theme-toggle').addEventListener('click', toggleTheme);
    
    // Mobile menu
    document.getElementById('menu-toggle').addEventListener('click', toggleMenuContent);
}

async function performSearch(query) {
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        if (results.length === 0) {
            showToast(`No results found for "${query}"`, 'info');
            unhighlightAll();
            isFiltered = false;
        } else {
            filteredNodeIds = new Set(results.map(n => n.id));
            isFiltered = true;
            
            // Highlight matching nodes
            d3.selectAll('.node').classed('faded', d => !filteredNodeIds.has(d.id));
            d3.selectAll('.node').classed('selected', false);
            
            updateNodeCountBadge();
            showToast(`Found ${results.length} matching node(s)`, 'success');
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast('Search failed: ' + error.message, 'error');
    }
}

function updateNodeCountBadge() {
    const total = graphData.nodes.length;
    const showing = isFiltered ? filteredNodeIds.size : total;
    document.getElementById('node-count-badge').textContent = `Showing ${showing} of ${total} nodes`;
}

function toggleTheme() {
    document.body.classList.toggle('light-mode');
    const isDark = !document.body.classList.contains('light-mode');
    document.getElementById('theme-toggle').textContent = isDark ? '🌙 Dark' : '☀️ Light';
    if (document.getElementById('mobile-theme-toggle')) {
        document.getElementById('mobile-theme-toggle').textContent = isDark ? '🌙 Dark' : '☀️ Light';
    }
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // Redraw graph with new colors
    renderGraph();
}

function toggleMenuContent() {
    const menu = document.getElementById('menu-content');
    menu.classList.toggle('active');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Handle window resize
window.addEventListener('resize', () => {
    if (graphData) {
        renderGraph();
    }
});
