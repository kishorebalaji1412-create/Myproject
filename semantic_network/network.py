"""
Network module - Builds semantic networks from DataFrames using NetworkX
"""

import networkx as nx
import pandas as pd
from collections import Counter
import json

class SemanticNetwork:
    """Represents a semantic network with nodes and links"""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.nodes = []
        self.links = []
        self.categories = {}
        self.metadata = {}
        
    def to_json(self):
        """Convert to D3.js compatible JSON format"""
        return {
            "nodes": self.nodes,
            "links": self.links,
            "metadata": self.metadata
        }
    
    def add_node(self, node_id, label, category, description="", properties=None):
        """Add a node to the network"""
        if properties is None:
            properties = {}
            
        color = self._get_color_for_category(category)
        
        node = {
            "id": str(node_id),
            "label": str(label),
            "category": str(category),
            "color": color,
            "description": str(description),
            "properties": properties
        }
        
        self.nodes.append(node)
        self.graph.add_node(str(node_id), **node)
        
    def add_link(self, source, target, link_type="related", weight=1.0):
        """Add an edge/link between nodes"""
        source = str(source)
        target = str(target)
        
        # Avoid duplicate links
        if not self.graph.has_edge(source, target):
            link = {
                "source": source,
                "target": target,
                "type": link_type,
                "weight": weight
            }
            self.links.append(link)
            self.graph.add_edge(source, target, type=link_type, weight=weight)
        
    def _get_color_for_category(self, category):
        """Assign consistent colors to categories"""
        color_palette = [
            "#00ff88",  # Green
            "#00d4ff",  # Cyan
            "#ff00ff",  # Magenta
            "#ffaa00",  # Orange
            "#ff6b6b",  # Red
            "#a78bfa",  # Purple
            "#fbbf24",  # Amber
            "#34d399",  # Emerald
        ]
        
        if category not in self.categories:
            idx = len(self.categories) % len(color_palette)
            self.categories[category] = color_palette[idx]
            
        return self.categories[category]
    
    def set_metadata(self, name, description, source=""):
        """Set metadata about the network"""
        self.metadata = {
            "name": name,
            "description": description,
            "source": source,
            "nodeCount": len(self.nodes),
            "edgeCount": len(self.links),
            "categories": list(self.categories.keys())
        }


def build_network_from_dataframe(df, config):
    """
    Build a semantic network from a Pandas DataFrame
    
    Args:
        df: Pandas DataFrame (from Kaggle CSV)
        config: Dict with keys:
            - node_column: column(s) to create nodes from
            - label_column: column to use as node labels
            - category_column: column for node categories
            - relationship_column: column(s) for relationships
            - max_nodes: limit number of nodes (default 100)
            - min_frequency: minimum frequency for edges (default 1)
    
    Returns:
        SemanticNetwork object ready for D3.js
    """
    network = SemanticNetwork()
    
    max_nodes = config.get("max_nodes", 100)
    min_frequency = config.get("min_frequency", 1)
    
    # Get column names from config
    node_col = config.get("node_column", df.columns[0] if len(df.columns) > 0 else None)
    label_col = config.get("label_column", node_col)
    category_col = config.get("category_column", None)
    relationship_col = config.get("relationship_column", None)
    
    if node_col is None or node_col not in df.columns:
        raise ValueError(f"node_column '{node_col}' not found in DataFrame")
    
    # Create nodes from unique values
    unique_values = df[node_col].dropna().unique()[:max_nodes]
    
    for i, value in enumerate(unique_values):
        node_id = f"{node_col}_{i}"
        label = str(value)
        category = df[category_col].iloc[i] if category_col and category_col in df.columns else node_col
        
        network.add_node(node_id, label, category, description=label)
    
    # Build edges from co-occurrences
    if relationship_col and relationship_col in df.columns:
        # Count co-occurrences
        for col in [col for col in df.columns if col != relationship_col]:
            if col not in df.columns:
                continue
                
            value_pairs = df.groupby(node_col)[col].apply(list).to_dict()
            
            for main_val, related_vals in value_pairs.items():
                # Find nodes matching this value
                main_node = next((n for n in network.nodes if n["label"] == str(main_val)), None)
                if not main_node:
                    continue
                
                # Count relationships
                counter = Counter(related_vals)
                for related_val, count in counter.most_common(10):
                    if count >= min_frequency:
                        related_node = next((n for n in network.nodes if n["label"] == str(related_val)), None)
                        if related_node and main_node["id"] != related_node["id"]:
                            network.add_link(main_node["id"], related_node["id"], 
                                           link_type="co_occurs", weight=float(count))
    
    # Detect top terms and build additional edges
    text_columns = df.select_dtypes(include=['object']).columns
    for text_col in text_columns[:3]:  # Use first 3 text columns
        if text_col == node_col:
            continue
        
        # Count occurrences
        value_counts = df[text_col].value_counts().head(20)
        
        # Add edges between frequently co-occurring terms
        for i, (val1, count1) in enumerate(value_counts.items()):
            node1 = next((n for n in network.nodes if n["label"] == str(val1)), None)
            if not node1:
                continue
            
            for val2, count2 in list(value_counts.items())[i+1:]:
                node2 = next((n for n in network.nodes if n["label"] == str(val2)), None)
                if node2:
                    co_occur_count = len(df[(df[text_col] == val1) | (df[text_col] == val2)])
                    if co_occur_count >= min_frequency:
                        network.add_link(node1["id"], node2["id"], 
                                       link_type="related", weight=float(co_occur_count))
    
    return network


def auto_build_semantic_network(df, name="Kaggle Dataset", max_nodes=100):
    """
    Automatically analyze a Kaggle CSV and build a semantic network
    
    Args:
        df: Pandas DataFrame from Kaggle CSV
        name: Name for the network
        max_nodes: Maximum number of nodes to create
    
    Returns:
        SemanticNetwork object ready for D3.js
    """
    network = SemanticNetwork()
    network.set_metadata(name, f"Semantic network from {name}", source="Kaggle")
    
    # Analyze DataFrame structure
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # Select best columns for nodes (low cardinality text columns or top numeric features)
    node_candidates = []
    
    for col in text_cols:
        n_unique = df[col].nunique()
        if 2 <= n_unique <= max_nodes:  # Good cardinality
            node_candidates.append((col, n_unique, "text"))
    
    # Sort by cardinality
    node_candidates.sort(key=lambda x: x[1])
    
    # Use the best candidates
    selected_cols = [col for col, _, _ in node_candidates[:5]]  # Top 5 columns
    
    if not selected_cols and text_cols:
        selected_cols = [text_cols[0]]
    
    # Create nodes from selected columns
    node_id_counter = 0
    node_map = {}  # Maps (column, value) -> node_id
    
    for col in selected_cols:
        if col not in df.columns:
            continue
            
        # Get top unique values
        top_values = df[col].value_counts().head(min(max_nodes // len(selected_cols), 30))
        
        for value, freq in top_values.items():
            if pd.isna(value):
                continue
            
            node_id = f"node_{node_id_counter}"
            node_id_counter += 1
            node_map[(col, value)] = node_id
            
            network.add_node(
                node_id,
                label=str(value)[:50],
                category=col,
                description=f"{col}: {value} (appears {freq} times)",
                properties={"frequency": int(freq)}
            )
            
            if node_id_counter >= max_nodes:
                break
        
        if node_id_counter >= max_nodes:
            break
    
    # Build edges from row co-occurrences
    for col_idx, col1 in enumerate(selected_cols):
        if col1 not in df.columns:
            continue
            
        for col2 in selected_cols[col_idx + 1:]:
            if col2 not in df.columns:
                continue
            
            # Find co-occurrences
            co_occur = df.groupby([col1, col2]).size().reset_index(name='count')
            
            for _, row in co_occur.iterrows():
                val1, val2, count = row[col1], row[col2], row['count']
                
                if (col1, val1) in node_map and (col2, val2) in node_map:
                    if count >= 1:  # At least 1 co-occurrence
                        network.add_link(
                            node_map[(col1, val1)],
                            node_map[(col2, val2)],
                            link_type="co_occurs",
                            weight=float(count)
                        )
    
    return network


def filter_network_by_category(network, category):
    """Filter network to show only nodes of a specific category"""
    filtered = SemanticNetwork()
    filtered.set_metadata(network.metadata["name"], network.metadata["description"], 
                         network.metadata["source"])
    
    # Add nodes of selected category
    for node in network.nodes:
        if node["category"] == category:
            filtered.nodes.append(node)
    
    # Add links between filtered nodes
    node_ids = {n["id"] for n in filtered.nodes}
    for link in network.links:
        if link["source"] in node_ids and link["target"] in node_ids:
            filtered.links.append(link)
    
    return filtered


def search_network(network, query):
    """Search nodes by label or category"""
    query_lower = query.lower()
    results = []
    
    for node in network.nodes:
        if (query_lower in node["label"].lower() or 
            query_lower in node["category"].lower() or
            query_lower in node.get("description", "").lower()):
            results.append(node)
    
    return results
