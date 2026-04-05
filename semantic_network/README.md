# Semantic Network Visualization Website

A powerful, interactive web application that visualizes semantic networks extracted from real-world datasets. Built with **Flask**, **D3.js**, and **Kaggle API** integration.

## 🚀 Features

- **Kaggle Integration**: Search, download, and process datasets directly from Kaggle
- **Automatic Analysis**: Intelligently detects relationships and patterns in data
- **Interactive D3.js Visualization**: Explore networks with zoom, pan, drag, and filter capabilities
- **Multi-Column Support**: Works with any CSV structure; auto-detects best columns for semantic relationships
- **Real-time Search**: Find and filter nodes with instant visual feedback
- **Category Filtering**: View networks by data categories
- **Dark/Light Mode**: Comfortable viewing in any environment
- **Fully Responsive**: Desktop, tablet, and mobile support
- **Export Data**: Download network as JSON for external analysis
- **Statistics Panel**: View key metrics about the loaded dataset
- **Mobile-Optimized**: Touch-friendly controls and sidebar drawer on mobile

## 📋 Tech Stack

### Backend
- **Flask** - Python web framework with CORS support
- **NetworkX** - Graph analysis and manipulation
- **Pandas** - Data processing and analysis
- **Kaggle API** - Dataset access and download
- **scikit-learn** - Machine learning utilities

### Frontend
- **D3.js v7** - Interactive data visualization
- **HTML5/CSS3** - Modern web standards
- **JavaScript ES6+** - Dynamic interactions and animations
- **Jinja2** - Server-side templating

## 📁 Project Structure

```
semantic_network/
├── app.py                        # Flask main application
├── network.py                    # NetworkX semantic network logic
├── kaggle_loader.py              # Kaggle API integration
├── data.py                       # Fallback/default data
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (Kaggle credentials)
├── kaggle.json                   # Kaggle API key file (optional)
├── datasets/                     # Downloaded Kaggle CSV files
├── templates/
│   ├── index.html               # Main graph visualization
│   ├── dataset.html             # Kaggle dataset browser
│   └── about.html               # About/documentation page
├── static/
│   ├── css/style.css            # Styling with dark/light themes
│   ├── js/graph.js              # D3.js graph rendering
│   ├── js/ui.js                 # UI interactions and utilities
│   └── assets/                  # Images and assets
└── README.md                     # This file
```

## 🔧 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Kaggle account (free)
- Git (optional)

### 1. Clone or Download the Project

```bash
cd semantic_network
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Kaggle API Credentials

#### Option A: Using kaggle.json (Recommended)

1. Visit [Kaggle Account Settings](https://www.kaggle.com/account)
2. Scroll down and click **"Create New API Token"**
3. This downloads `kaggle.json`
4. Move `kaggle.json` to your project root directory, OR
5. Move it to `~/.kaggle/kaggle.json` (standard location)

#### Option B: Using Environment Variables

1. Create `.env` file in project root (already provided as template)
2. Update with your Kaggle credentials:
   ```
   KAGGLE_USERNAME=your_kaggle_username
   KAGGLE_KEY=your_kaggle_api_key
   FLASK_DEBUG=True
   FLASK_PORT=5000
   ```

### 5. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## 🌐 Usage

### 1. **Main Dashboard** (`/`)
   - View the semantic network graph
   - Click nodes to see details
   - Search for nodes in real-time
   - Filter by category
   - Control zoom and pan
   - Toggle dark/light mode

### 2. **Dataset Browser** (`/datasets`)
   - Search Kaggle for datasets
   - View local downloaded datasets
   - Load any Kaggle dataset with one click
   - See dataset statistics (size, downloads)
   - System automatically processes CSV and builds network

### 3. **About Page** (`/about`)
   - Learn more about the tool
   - Technology and use cases
   - Kaggle API setup guide

## 📡 API Endpoints

### Graph Data
- `GET /api/graph` - Get current graph as JSON
- `GET /api/graph?category=X` - Get graph filtered by category
- `GET /api/node/<id>` - Get single node details
- `GET /api/search?q=term` - Search nodes
- `GET /api/stats` - Get network statistics

### Kaggle Integration
- `GET /api/kaggle/search?q=query` - Search Kaggle datasets
- `POST /api/kaggle/download` - Download and process dataset
- `GET /api/kaggle/datasets` - List local datasets
- `POST /api/kaggle/load` - Load local dataset
- `GET /api/export` - Export current graph as JSON

## 🎨 How the Semantic Network is Built

1. **Data Loading**: CSV is loaded into a Pandas DataFrame
2. **Column Analysis**: System analyzes data types and cardinality
3. **Node Selection**: Most relevant columns are selected for nodes
4. **Node Creation**: Unique values become network nodes
5. **Edge Building**: Relationships detected from:
   - Row co-occurrences (same row = related)
   - Value_counts() frequency
   - Column correlations
6. **Categorization**: Nodes grouped by source column
7. **Visualization**: Force-directed layout with D3.js

## 🔍 Example Datasets

Try these publicly available Kaggle datasets:

- **iris** - Classic Iris flower classification data
- **housing** - California housing market data
- **wine** - Wine quality and chemical properties
- **titanic** - Famous Titanic passenger data
- **pokemon** - Pokémon species and stats
- **iris-flowers** - Extended iris dataset variants
- **covid** - COVID-19 pandemic data

## ⌨️ Keyboard Shortcuts

- `Ctrl+K` (Windows/Linux) or `Cmd+K` (Mac) - Focus search bar
- `Escape` - Clear search
- Click on nodes - Select and view details
- Double-click - Center on node
- Scroll - Zoom in/out
- Drag - Pan across graph

## 📱 Mobile Features

- **Responsive Design**: Adapts to all screen sizes
- **Touch Support**: Swipe, pinch to zoom
- **Hamburger Menu**: Easy navigation on small screens
- **Bottom Drawer**: Sidebar becomes bottom sheet on mobile
- **Touch Drag**: Move nodes with finger

## 🎨 Dark/Light Mode

- Toggle button in navbar
- Preference saved in localStorage
- Automatically applies smooth transitions
- Colors optimized for both themes

## 📊 Supported File Formats

Currently supports:
- **CSV files** (.csv) from Kaggle

Future support planned for:
- JSON files
- Excel files (.xlsx)
- SQL databases
- APIs

## 🐛 Troubleshooting

### "Kaggle API Error: AuthenticationError"
- Make sure `kaggle.json` is in the correct location
- Verify credentials are correct on Kaggle account
- Try regenerating API token

### "No CSV files found"
- Ensure dataset contains CSV files
- Some Kaggle datasets are not CSV-based
- Try a different dataset

### Graph renders but is empty
- Dataset may have unusual structure
- Try a simpler dataset first (iris, wine)
- Check browser console for errors

### CORS errors
- Flask-CORS is installed and enabled
- Check that ports don't conflict
- Try a different port (modify `.env`)

## 🚀 Deployment

### For Production

1. Set `FLASK_DEBUG=False` in `.env`
2. Install production server: `pip install gunicorn`
3. Run with Gunicorn: `gunicorn -w 4 app:app`
4. Use nginx as reverse proxy
5. Enable HTTPS with Let's Encrypt

### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w", "4", "app:app"]
```

Build and run:
```bash
docker build -t semantic-network .
docker run -p 5000:5000 -e KAGGLE_USERNAME=... -e KAGGLE_KEY=... semantic-network
```

## 📈 Advanced Usage

### Custom Network Building

Edit `network.py` to customize:
- Node/edge detection algorithms
- Relationship strength calculations
- Force simulation parameters
- Category detection logic

### Custom Styling

Edit `static/css/style.css` to:
- Change color schemes
- Modify animations
- Adjust responsive breakpoints
- Add custom themes

### Extending the API

Add new routes in `app.py` for:
- Additional analysis
- Custom export formats
- Integration with other services
- Database storage

## 📚 Learning Resources

- [D3.js Documentation](https://d3js.org)
- [Flask Documentation](https://flask.palletsprojects.com)
- [NetworkX Tutorial](https://networkx.org)
- [Kaggle API Guide](https://github.com/Kaggle/kaggle-api)
- [Pandas User Guide](https://pandas.pydata.org/docs)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created as a demonstration of modern web technologies combined with data science and network visualization.

## 🙏 Acknowledgments

- Kaggle for providing the dataset API
- D3.js for visualization capabilities
- NetworkX for graph analysis
- Flask for the web framework
- The open-source community

## 📞 Support

For issues, questions, or suggestions:
- Check the troubleshooting section
- Review API documentation
- Consult the About page in the app
- Check the GitHub repository

---

**Happy Network Visualizing!** 🎉

Try loading different Kaggle datasets and exploring the semantic relationships hidden in your data.
