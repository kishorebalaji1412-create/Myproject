"""
Fallback data module - provides default semantic networks if Kaggle fails
"""

def get_default_network():
    """Returns a default semantic network for demo purposes"""
    return {
        "nodes": [
            {"id": "python", "label": "Python", "category": "Language", "color": "#00ff88"},
            {"id": "machine_learning", "label": "Machine Learning", "category": "Field", "color": "#00d4ff"},
            {"id": "data_science", "label": "Data Science", "category": "Field", "color": "#00d4ff"},
            {"id": "neural_networks", "label": "Neural Networks", "category": "Technique", "color": "#ff00ff"},
            {"id": "deep_learning", "label": "Deep Learning", "category": "Technique", "color": "#ff00ff"},
            {"id": "nlp", "label": "NLP", "category": "Field", "color": "#00d4ff"},
            {"id": "computer_vision", "label": "Computer Vision", "category": "Field", "color": "#00d4ff"},
            {"id": "tensorflow", "label": "TensorFlow", "category": "Framework", "color": "#ffaa00"},
            {"id": "pytorch", "label": "PyTorch", "category": "Framework", "color": "#ffaa00"},
            {"id": "sklearn", "label": "scikit-learn", "category": "Framework", "color": "#ffaa00"},
            {"id": "pandas", "label": "Pandas", "category": "Tool", "color": "#00ff88"},
            {"id": "numpy", "label": "NumPy", "category": "Tool", "color": "#00ff88"},
            {"id": "classification", "label": "Classification", "category": "Task", "color": "#ff6b6b"},
            {"id": "regression", "label": "Regression", "category": "Task", "color": "#ff6b6b"},
            {"id": "clustering", "label": "Clustering", "category": "Task", "color": "#ff6b6b"},
        ],
        "links": [
            {"source": "python", "target": "machine_learning", "type": "uses"},
            {"source": "machine_learning", "target": "neural_networks", "type": "includes"},
            {"source": "neural_networks", "target": "deep_learning", "type": "specializes"},
            {"source": "deep_learning", "target": "computer_vision", "type": "applies_to"},
            {"source": "deep_learning", "target": "nlp", "type": "applies_to"},
            {"source": "machine_learning", "target": "classification", "type": "includes"},
            {"source": "machine_learning", "target": "regression", "type": "includes"},
            {"source": "machine_learning", "target": "clustering", "type": "includes"},
            {"source": "tensorflow", "target": "deep_learning", "type": "enables"},
            {"source": "pytorch", "target": "neural_networks", "type": "enables"},
            {"source": "sklearn", "target": "machine_learning", "type": "implements"},
            {"source": "pandas", "target": "data_science", "type": "tools"},
            {"source": "numpy", "target": "data_science", "type": "tools"},
            {"source": "python", "target": "data_science", "type": "language"},
        ],
        "metadata": {
            "name": "AI/ML Semantic Network",
            "description": "Default demo network showing AI/ML concepts and relationships",
            "nodeCount": 15,
            "edgeCount": 14,
            "source": "Default Dataset",
        }
    }

def get_simple_network():
    """Returns a simple network for quick testing"""
    return {
        "nodes": [
            {"id": "A", "label": "Node A", "category": "Type1", "color": "#00ff88"},
            {"id": "B", "label": "Node B", "category": "Type2", "color": "#00d4ff"},
            {"id": "C", "label": "Node C", "category": "Type1", "color": "#00ff88"},
        ],
        "links": [
            {"source": "A", "target": "B", "type": "connects"},
            {"source": "B", "target": "C", "type": "connects"},
        ],
        "metadata": {
            "name": "Simple Test Network",
            "description": "Minimal test network",
            "nodeCount": 3,
            "edgeCount": 2,
            "source": "Test Data",
        }
    }
