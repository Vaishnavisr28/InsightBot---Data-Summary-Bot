#  Data Summary Chatbot

An intelligent data analysis chatbot built with Python and Streamlit that combines local LLM capabilities with rule-based logic for comprehensive data exploration and visualization.

##  Features

###  Core Capabilities
- **Multi-format File Support**: Upload CSV, TSV, Excel (.xlsx), and JSON files
- **Automatic EDA**: Instant exploratory data analysis with summary statistics
- **Smart Intent Detection**: Classifies queries into chart, statistical, or textual categories
- **Hybrid Response System**: Combines local LLM (Ollama) with rule-based logic
- **Offline Functionality**: Works without internet when Ollama is running locally

###  Chart Generation
- **Bar Charts**: For categorical data visualization
- **Pie Charts**: For proportion analysis
- **Line Charts**: For trend visualization
- **Scatter Plots**: For correlation analysis
- **Histograms**: For distribution analysis
- **Box Plots**: For statistical summaries
- **Heatmaps**: For correlation matrices

###  AI Integration
- **Local LLM**: Powered by Ollama with gemma:2b model
- **Natural Language Processing**: Understands conversational queries
- **Context-Aware Responses**: Provides relevant insights based on data characteristics
- **Fallback System**: Rule-based responses when LLM is unavailable

###  Export & Reporting
- **PDF Reports**: Download comprehensive analysis reports
- **Chat History**: Complete conversation logs
- **Visualizations**: Charts included in reports
- **Summary Statistics**: Detailed data insights

##  Quick Start

### Prerequisites
- Python 3.8 or higher
- Ollama (optional, for LLM features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd InsightBot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama (Optional)**
   ```bash
   # Download from https://ollama.ai/
   # Or use package manager
   
   # Pull the gemma:2b model
   ollama pull gemma:2b
   ```

4. **Start Ollama (Optional)**
   ```bash
   ollama serve
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

The application will open in your browser at `http://localhost:8501`

##  Usage Guide

### 1. Upload Your Data
- Use the sidebar to upload CSV, TSV, Excel, or JSON files
- The system automatically performs EDA and displays summary statistics

### 2. Ask Questions
You can ask questions in natural language:

#### Statistical Questions
```
"What is the average of views?"
"Show me the minimum value of likes"
"What's the standard deviation of subscribers?"
```

#### Chart Requests
```
"Show bar chart of category_id"
"Create pie chart for channel_type"
"Plot histogram of views"
"Generate scatter plot of views vs likes"
```

#### Natural Language Queries
```
"What insights can you find in this data?"
"Are there any patterns in the video performance?"
"What should I focus on for improvement?"
```

### 3. Export Results
- Generate PDF reports with complete analysis
- Download chat history and visualizations
- Share insights with stakeholders

##  Architecture

### Backend (`chatbot_agent.py`)
- **DataSummaryChatbot Class**: Core chatbot logic
- **Intent Detection**: Smart query classification
- **Chart Generation**: Matplotlib/Seaborn visualizations
- **Statistical Analysis**: Rule-based calculations
- **LLM Integration**: Ollama API communication

### Frontend (`app.py`)
- **Streamlit Interface**: Modern web UI
- **File Upload**: Multi-format support
- **Chat Interface**: Real-time conversation
- **EDA Display**: Organized data insights
- **PDF Export**: Report generation

##  Configuration

### Ollama Setup
1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Pull the gemma:2b model: `ollama pull gemma:2b`
3. Start the service: `ollama serve`
4. The chatbot will automatically detect Ollama availability

### Customization
- Modify chart styles in `chatbot_agent.py`
- Add new chart types in the `chart_keywords` dictionary
- Extend statistical functions in `get_statistical_answer()`
- Customize UI styling in `app.py`

##  Supported File Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| CSV | `.csv` | Comma-separated values |
| TSV | `.tsv` | Tab-separated values |
| Excel | `.xlsx` | Microsoft Excel files |
| JSON | `.json` | JavaScript Object Notation |

##  Example Use Cases

### YouTube Analytics
- Analyze video performance metrics
- Identify trending content categories
- Compare engagement rates across channels

### Sales Data
- Track revenue trends over time
- Analyze customer demographics
- Identify top-performing products

### Survey Results
- Visualize response distributions
- Analyze demographic patterns
- Identify correlation patterns

##  Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check if gemma:2b model is installed: `ollama list`
   - Verify port 11434 is accessible

2. **File Upload Issues**
   - Check file format compatibility
   - Ensure file is not corrupted
   - Verify file size limits

3. **Chart Generation Errors**
   - Confirm column names exist in dataset
   - Check data types for chart compatibility
   - Ensure sufficient data for visualization

### Performance Tips
- Use smaller datasets for faster processing
- Close unnecessary browser tabs
- Restart Streamlit if memory issues occur

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Acknowledgments

- **Streamlit**: For the amazing web framework
- **Ollama**: For local LLM capabilities
- **Pandas**: For data manipulation
- **Matplotlib/Seaborn**: For visualization
- **FPDF**: For PDF generation

---

**Happy Data Analysis! **
