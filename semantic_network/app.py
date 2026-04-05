"""
Flask application for semantic network visualization
Main app with all routes and API endpoints
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
from pathlib import Path
import io

from network import auto_build_semantic_network, filter_network_by_category, search_network
from kaggle_loader import initialize_kaggle_loader
from data import get_default_network

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Global state
current_network = None
current_dataset = None
kaggle_loader = None


def init_kaggle():
    """Initialize Kaggle loader"""
    global kaggle_loader
    if kaggle_loader is None:
        kaggle_loader = initialize_kaggle_loader()


def load_default_network():
    """Load default demo network"""
    global current_network, current_dataset
    data = get_default_network()
    current_network = data
    current_dataset = {
        "name": data["metadata"]["name"],
        "source": "Default Dataset",
        "file": None,
    }


# Initialize on startup
with app.app_context():
    init_kaggle()
    load_default_network()


# ============================================================================
# FRONTEND ROUTES (serve HTML)
# ============================================================================

@app.route("/")
def index():
    """Main graph visualization page"""
    return render_template("index.html", 
                         dataset_name=current_dataset.get("name", "No dataset loaded"))


@app.route("/datasets")
def datasets_page():
    """Kaggle dataset browser page"""
    return render_template("dataset.html")


@app.route("/about")
def about():
    """About page"""
    return render_template("about.html")


# ============================================================================
# API ROUTES - Graph Data
# ============================================================================

@app.route("/api/graph")
def get_graph():
    """
    Get current graph as JSON for D3.js
    Supports filtering by category via ?category=X
    """
    global current_network
    
    category = request.args.get("category", None)
    
    if current_network is None:
        return jsonify(get_default_network())
    
    # If category filter requested
    if category:
        # Reconstruct network object for filtering
        from network import SemanticNetwork
        net = SemanticNetwork()
        net.nodes = current_network["nodes"]
        net.links = current_network["links"]
        net.metadata = current_network["metadata"]
        
        filtered = filter_network_by_category(net, category)
        return jsonify(filtered.to_json())
    
    return jsonify(current_network)


@app.route("/api/node/<node_id>")
def get_node(node_id):
    """Get details for a single node"""
    global current_network
    
    if current_network is None:
        return jsonify({"error": "No network loaded"}), 404
    
    # Find node
    for node in current_network["nodes"]:
        if node["id"] == node_id:
            # Get connected nodes
            connected = []
            for link in current_network["links"]:
                if link["source"] == node_id:
                    connected.append(link["target"])
                elif link["target"] == node_id:
                    connected.append(link["source"])
            
            # Get connected node details
            connected_nodes = []
            for conn_id in connected:
                for n in current_network["nodes"]:
                    if n["id"] == conn_id:
                        connected_nodes.append(n)
                        break
            
            return jsonify({
                "node": node,
                "connected": connected_nodes,
                "connectionCount": len(connected_nodes),
            })
    
    return jsonify({"error": "Node not found"}), 404


@app.route("/api/search")
def search():
    """
    Search nodes by label or description
    Query parameter: ?q=search_term
    """
    global current_network
    
    query = request.args.get("q", "")
    
    if not query or current_network is None:
        return jsonify([])
    
    from network import SemanticNetwork
    net = SemanticNetwork()
    net.nodes = current_network["nodes"]
    net.links = current_network["links"]
    
    results = search_network(net, query)
    return jsonify(results)


# ============================================================================
# API ROUTES - Kaggle Integration
# ============================================================================

@app.route("/api/kaggle/search", methods=["GET"])
def kaggle_search():
    """
    Search Kaggle for datasets
    Query parameter: ?q=search_term
    """
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    
    if not query:
        return jsonify({"error": "Query parameter 'q' required"}), 400
    
    try:
        results = kaggle_loader.search_datasets(query, max_results=limit)
        return jsonify({"success": True, "results": results, "count": len(results)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/kaggle/download", methods=["POST"])
def kaggle_download():
    """
    Download and process a Kaggle dataset
    POST body: {"dataset_slug": "owner/dataset"}
    """
    global current_network, current_dataset, kaggle_loader
    
    data = request.get_json() or {}
    dataset_slug = data.get("dataset_slug")
    
    if not dataset_slug:
        return jsonify({"error": "dataset_slug required"}), 400
    
    try:
        # Download dataset
        download_result = kaggle_loader.download_dataset(dataset_slug)
        
        if not download_result.get("success"):
            return jsonify({"success": False, "error": download_result.get("error")}), 500
        
        # Process first CSV file found
        files = download_result.get("files", [])
        if not files:
            return jsonify({"success": False, "error": "No CSV files found in dataset"}), 400
        
        csv_path = files[0]
        
        # Build network with progress
        network_data = kaggle_loader.process_dataset_to_network(
            csv_path, 
            dataset_name=dataset_slug
        )
        
        if network_data is None:
            return jsonify({"success": False, "error": "Failed to process dataset"}), 500
        
        # Store current network
        current_network = network_data
        current_dataset = {
            "name": dataset_slug,
            "source": "Kaggle",
            "file": csv_path,
        }
        
        return jsonify({
            "success": True,
            "message": "Dataset downloaded and processed",
            "dataset": dataset_slug,
            "file": csv_path,
            "nodes": len(network_data.get("nodes", [])),
            "edges": len(network_data.get("links", [])),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/kaggle/datasets", methods=["GET"])
def kaggle_list_datasets():
    """List all locally downloaded CSV files"""
    try:
        datasets = kaggle_loader.get_available_datasets()
        return jsonify({"success": True, "datasets": datasets, "count": len(datasets)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/kaggle/load", methods=["POST"])
def kaggle_load():
    """
    Load an already downloaded dataset and rebuild the graph
    POST body: {"filename": "path/to/file.csv"}
    """
    global current_network, current_dataset, kaggle_loader
    
    data = request.get_json() or {}
    filename = data.get("filename")
    
    if not filename:
        return jsonify({"error": "filename required"}), 400
    
    try:
        network_data = kaggle_loader.process_dataset_to_network(filename, dataset_name=filename)
        
        if network_data is None:
            return jsonify({"success": False, "error": "Failed to process dataset"}), 500
        
        current_network = network_data
        current_dataset = {
            "name": Path(filename).name,
            "source": "Local File",
            "file": filename,
        }
        
        return jsonify({
            "success": True,
            "message": "Dataset loaded and processed",
            "file": filename,
            "nodes": len(network_data.get("nodes", [])),
            "edges": len(network_data.get("links", [])),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/export", methods=["GET"])
def export_graph():
    """Export current graph as downloadable JSON"""
    global current_network
    
    if current_network is None:
        return jsonify({"error": "No graph to export"}), 404
    
    # Create JSON file
    json_str = json.dumps(current_network, indent=2)
    
    return send_file(
        io.BytesIO(json_str.encode()),
        mimetype="application/json",
        as_attachment=True,
        download_name=f"network-{current_dataset.get('name', 'export')}.json"
    )


# ============================================================================
# API ROUTES - Network Stats and Info
# ============================================================================

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get network statistics"""
    global current_network, current_dataset
    
    if current_network is None:
        return jsonify({"error": "No network loaded"}), 404
    
    metadata = current_network.get("metadata", {})
    
    return jsonify({
        "nodeCount": len(current_network.get("nodes", [])),
        "edgeCount": len(current_network.get("links", [])),
        "categories": list(set(n.get("category") for n in current_network.get("nodes", []))),
        "dataset": current_dataset,
        "metadata": metadata,
    })


@app.route("/api/reset", methods=["POST"])
def reset_network():
    """Reset to default network"""
    global current_network, current_dataset
    load_default_network()
    return jsonify({"success": True, "message": "Network reset to default"})


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 10000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )
