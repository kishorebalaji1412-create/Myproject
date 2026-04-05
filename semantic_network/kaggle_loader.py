"""
Kaggle API loader - Handles dataset search, download, and processing
"""

import os
import json
import pandas as pd
from pathlib import Path
import subprocess
import sys

# Try to import kaggle, install if not available
try:
    from kaggle.api.kaggle_api_extended import KaggleApi
except ImportError:
    KaggleApi = None

from network import auto_build_semantic_network, SemanticNetwork


class KaggleLoader:
    """Handles Kaggle API interactions and dataset processing"""
    
    def __init__(self, credentials_path=None):
        self.api = None
        self.credentials_path = credentials_path or os.path.expanduser("~/.kaggle/kaggle.json")
        self.datasets_dir = "datasets"
        self.downloaded_datasets = {}
        
        # Ensure datasets directory exists
        Path(self.datasets_dir).mkdir(exist_ok=True)
        
        self._initialize_kaggle()
    
    def _initialize_kaggle(self):
        """Initialize Kaggle API"""
        if KaggleApi is None:
            print("Warning: kaggle package not installed. Install with: pip install kaggle")
            return False
        
        try:
            self.api = KaggleApi()
            self.api.authenticate()
            print("Kaggle API authenticated successfully")
            return True
        except Exception as e:
            print(f"Failed to authenticate Kaggle API: {e}")
            print("To set up Kaggle credentials:")
            print("1. Go to https://www.kaggle.com/account")
            print("2. Click 'Create New API Token' (downloads kaggle.json)")
            print("3. Place kaggle.json in ~/.kaggle/ directory")
            return False
    
    def search_datasets(self, query, max_results=20):
        """
        Search Kaggle for datasets by keyword
        
        Args:
            query: Search term
            max_results: Maximum datasets to return
        
        Returns:
            List of dataset dicts with metadata
        """
        if not self.api:
            return self._get_mock_datasets(query)
        
        try:
            datasets = self.api.dataset_list(search=query, max_size=1000)
            
            results = []
            for i, dataset in enumerate(datasets):
                if i >= max_results:
                    break
                
                results.append({
                    "id": dataset.ref,
                    "slug": dataset.ref,
                    "title": dataset.title,
                    "author": dataset.owner,
                    "size": dataset.totalDatasetSize,
                    "downloads": dataset.downloads,
                    "created": str(dataset.createdDate) if hasattr(dataset, 'createdDate') else "Unknown",
                    "description": dataset.subtitle or "No description",
                })
            
            return results
        except Exception as e:
            print(f"Error searching datasets: {e}")
            return self._get_mock_datasets(query)
    
    def _get_mock_datasets(self, query):
        """Return mock datasets for demo/testing"""
        mock_datasets = [
            {
                "id": "uciml/iris",
                "slug": "uciml/iris",
                "title": "Iris Flower Dataset",
                "author": "UCI ML",
                "size": 50000,
                "downloads": 1000000,
                "created": "2016-11-02",
                "description": "Famous iris classification dataset with flower measurements",
            },
            {
                "id": "bls/consumer_price_index",
                "slug": "bls/consumer-price-index",
                "title": "Consumer Price Index",
                "author": "BLS",
                "size": 5000000,
                "downloads": 50000,
                "created": "2020-01-15",
                "description": "CPI data for economic analysis",
            },
            {
                "id": "bing-liu/sentiment-analysis-sample-data",
                "slug": "bing-liu/sentiment-analysis-sample-data",
                "title": "Sentiment Analysis Sample Data",
                "author": "Bing Liu",
                "size": 1000000,
                "downloads": 30000,
                "created": "2019-05-10",
                "description": "Sample data for sentiment analysis tasks",
            },
        ]
        
        return [d for d in mock_datasets if query.lower() in d["title"].lower()]
    
    def download_dataset(self, dataset_slug, path="datasets/"):
        """
        Download a Kaggle dataset
        
        Args:
            dataset_slug: Dataset identifier (e.g., "uciml/iris")
            path: Directory to save files
        
        Returns:
            Dict with download status and file info
        """
        Path(path).mkdir(parents=True, exist_ok=True)
        
        if not self.api:
            return {"success": False, "error": "Kaggle API not initialized"}
        
        try:
            self.api.dataset_download_files(dataset_slug, path=path, unzip=True)
            
            # List downloaded files
            files = list(Path(path).glob("**/*.csv"))
            
            return {
                "success": True,
                "dataset_slug": dataset_slug,
                "path": path,
                "files": [str(f) for f in files],
                "file_count": len(files),
            }
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            return {"success": False, "error": str(e), "dataset_slug": dataset_slug}
    
    def load_csv_as_dataframe(self, filename):
        """
        Load a CSV file into a Pandas DataFrame
        
        Args:
            filename: Path to CSV file
        
        Returns:
            Pandas DataFrame or None if error
        """
        try:
            df = pd.read_csv(filename, nrows=5000)  # Limit rows for performance
            return df
        except Exception as e:
            print(f"Error loading CSV {filename}: {e}")
            return None
    
    def get_available_datasets(self):
        """
        List all CSV files in the datasets directory
        
        Returns:
            List of dicts with filename and metadata
        """
        datasets_path = Path(self.datasets_dir)
        csv_files = list(datasets_path.rglob("*.csv"))
        
        results = []
        for csv_file in csv_files:
            size = csv_file.stat().st_size
            results.append({
                "filename": str(csv_file),
                "name": csv_file.name,
                "size": size,
                "size_mb": round(size / 1024 / 1024, 2),
            })
        
        return results
    
    def process_dataset_to_network(self, csv_path, dataset_name="Kaggle Dataset"):
        """
        Load a CSV and automatically build a semantic network
        
        Args:
            csv_path: Path to CSV file
            dataset_name: Name for the network
        
        Returns:
            SemanticNetwork object as JSON
        """
        try:
            df = self.load_csv_as_dataframe(csv_path)
            if df is None:
                return None
            
            network = auto_build_semantic_network(df, name=dataset_name, max_nodes=100)
            return network.to_json()
        except Exception as e:
            print(f"Error processing dataset: {e}")
            return None


def initialize_kaggle_loader():
    """Factory function to create initialized KaggleLoader"""
    return KaggleLoader()
