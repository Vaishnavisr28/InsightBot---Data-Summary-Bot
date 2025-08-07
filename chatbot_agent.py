import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json
import re
from typing import Dict, List, Tuple, Optional, Any
import io
import base64
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class DataSummaryChatbot:
    def __init__(self):
        self.df = None
        self.summary_stats = {}
        self.chat_history = []
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_available = self._is_ollama_running()

        self.chart_keywords = {
            'bar': ['bar', 'bar chart', 'barplot', 'histogram'],
            'pie': ['pie', 'pie chart', 'pieplot', 'donut'],
            'line': ['line', 'line chart', 'lineplot', 'trend', 'time series'],
            'scatter': ['scatter', 'scatter plot', 'correlation'],
            'heatmap': ['heatmap', 'heat map', 'correlation matrix'],
            'box': ['box', 'boxplot', 'box plot', 'distribution'],
            'histogram': ['histogram', 'hist', 'distribution']
        }

        self.stat_keywords = [
            'mean', 'average', 'median', 'mode', 'min', 'minimum', 'max', 'maximum',
            'sum', 'count', 'std', 'standard deviation', 'variance', 'percentile',
            'top', 'bottom', 'highest', 'lowest', 'most', 'least'
        ]

    def _is_ollama_running(self) -> bool:
        try:
            res = requests.get("http://localhost:11434/api/tags", timeout=5)
            return res.status_code == 200
        except:
            return False

    def load_data(self, file_path: str) -> Dict[str, Any]:
        try:
            ext = file_path.split('.')[-1].lower()
            if ext == 'csv':
                self.df = pd.read_csv(file_path)
            elif ext == 'tsv':
                self.df = pd.read_csv(file_path, sep='\t')
            elif ext == 'xlsx':
                self.df = pd.read_excel(file_path)
            elif ext == 'json':
                self.df = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}")

            self._run_eda()
            return {'success': True, 'message': f"Data loaded. Shape: {self.df.shape}", 'summary': self.summary_stats}

        except Exception as e:
            return {'success': False, 'message': str(e), 'summary': {}}

    def _run_eda(self):
        if self.df is None:
            return

        self.summary_stats = {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'data_types': self.df.dtypes.to_dict(),
            'null_counts': self.df.isnull().sum().to_dict(),
            'null_percentage': (self.df.isnull().sum() / len(self.df) * 100).to_dict(),
            'numeric_columns': self.df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': self.df.select_dtypes(include=['object']).columns.tolist(),
            'datetime_columns': self.df.select_dtypes(include=['datetime']).columns.tolist()
        }

        if self.summary_stats['numeric_columns']:
            self.summary_stats['numeric_stats'] = self.df[self.summary_stats['numeric_columns']].describe().to_dict()

    def detect_intent(self, query: str) -> str:
        query = query.lower()

        for chart_type, keywords in self.chart_keywords.items():
            if any(k in query for k in keywords):
                return 'chart'

        if any(k in query for k in self.stat_keywords):
            return 'statistical'

        if any(re.search(p, query) for p in [r'show.*chart', r'plot.*chart', r'chart', r'graph', r'visualize']):
            return 'chart'

        return 'textual'

    def _extract_column(self, query: str) -> Optional[str]:
        query = query.lower()
        for col in self.df.columns:
            if col.lower() in query:
                return col

        quoted = re.search(r'"(.*?)"', query)
        if quoted and quoted.group(1) in self.df.columns:
            return quoted.group(1)

        if 'heatmap' in query or 'correlation' in query:
            return None

        context_map = {
            'trending': ['trending_date', 'views', 'likes'],
            'channel': ['channel_name', 'channel_title'],
            'video': ['video_id', 'title', 'views']
        }

        for key, options in context_map.items():
            if key in query:
                for col in options:
                    if col in self.df.columns:
                        return col

        return None

    def generate_chart(self, query: str) -> Dict[str, Any]:
        if self.df is None:
            return {'success': False, 'message': 'No data loaded'}

        query_lower = query.lower()
        chart_type = next((k for k, v in self.chart_keywords.items() if any(word in query_lower for word in v)), 'bar')
        col = self._extract_column(query)

        if 'heatmap' in query_lower:
            chart_type, col = 'heatmap', None

        if col and col not in self.df.columns:
            return {'success': False, 'message': f'Column "{col}" not found.'}

        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == 'bar' and self.df[col].dtype == 'object':
                self.df[col].value_counts().plot(kind='bar', ax=ax)
                ax.set_title(f'Bar Chart: {col}')

            elif chart_type == 'pie' and self.df[col].dtype == 'object':
                counts = self.df[col].value_counts()
                plt.pie(counts.values, labels=counts.index, autopct='%1.1f%%')
                plt.title(f'Pie Chart: {col}')

            elif chart_type == 'line' and self.df[col].dtype in ['int64', 'float64']:
                self.df[col].plot(kind='line', ax=ax)
                ax.set_title(f'Line Chart: {col}')

            elif chart_type == 'scatter':
                nums = self.summary_stats['numeric_columns']
                if len(nums) >= 2:
                    x, y = col, next(c for c in nums if c != col)
                    plt.scatter(self.df[x], self.df[y])
                    plt.title(f'Scatter: {x} vs {y}')
                else:
                    raise ValueError('At least 2 numeric columns required for scatter plot')

            elif chart_type == 'histogram' and self.df[col].dtype in ['int64', 'float64']:
                self.df[col].hist(bins=30, ax=ax)
                ax.set_title(f'Histogram: {col}')

            elif chart_type == 'box' and self.df[col].dtype in ['int64', 'float64']:
                self.df[col].plot(kind='box', ax=ax)
                ax.set_title(f'Box Plot: {col}')

            elif chart_type == 'heatmap':
                corr = self.df[self.summary_stats['numeric_columns']].corr()
                sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, ax=ax)
                ax.set_title('Correlation Heatmap')
                col = 'correlation_matrix'

            else:
                raise ValueError(f'Unsupported chart or invalid column for chart type: {chart_type}')

            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300)
            buf.seek(0)
            encoded_img = base64.b64encode(buf.read()).decode()
            plt.close()

            return {
                'success': True,
                'message': f'Generated {chart_type} chart for {col}',
                'chart_type': chart_type,
                'column_name': col,
                'image_base64': encoded_img
            }

        except Exception as e:
            plt.close()
            return {'success': False, 'message': str(e)}

    def get_statistical_answer(self, query: str) -> str:
        if self.df is None:
            return 'No data loaded.'

        col = self._extract_column(query)
        if not col or col not in self.df.columns:
            return 'Could not identify column for statistical analysis.'

        if col not in self.summary_stats['numeric_columns']:
            return f'Column "{col}" is not numeric.'

        series = self.df[col].dropna()
        query = query.lower()

        try:
            if 'mean' in query or 'average' in query:
                return f'Mean of {col}: {series.mean():.2f}'
            elif 'median' in query:
                return f'Median of {col}: {series.median():.2f}'
            elif 'min' in query:
                return f'Minimum of {col}: {series.min():.2f}'
            elif 'max' in query:
                return f'Maximum of {col}: {series.max():.2f}'
            elif 'sum' in query:
                return f'Sum of {col}: {series.sum():.2f}'
            elif 'std' in query:
                return f'Standard Deviation of {col}: {series.std():.2f}'
            elif 'variance' in query:
                return f'Variance of {col}: {series.var():.2f}'
            else:
                stats = series.describe()
                return f"Stats for {col}:\nCount: {stats['count']:.0f}, Mean: {stats['mean']:.2f}, Min: {stats['min']:.2f}, Max: {stats['max']:.2f}"
        except Exception as e:
            return f'Error calculating statistics: {str(e)}'

    def get_llm_response(self, query: str) -> str:
        if not self.ollama_available:
            return "Ollama is not running. Start Ollama with gemma:2b."

        try:
            context = f"Dataset shape: {self.df.shape}, Columns: {list(self.df.columns)}"
            payload = {
                "model": "gemma:2b",
                "prompt": f"You are a helpful assistant.\n\n{context}\n\nUser: {query}\n\nAssistant:",
                "stream": False
            }
            res = requests.post(self.ollama_url, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json().get('response', '')
            return f'LLM error: {res.status_code}'
        except Exception as e:
            return f'LLM exception: {str(e)}'

    def process_user_input(self, query: str) -> Dict[str, Any]:
        if self.df is None:
            return {'success': False, 'message': 'No data loaded.', 'response_type': 'text'}

        self.chat_history.append({'user': query, 'timestamp': datetime.now().isoformat()})
        intent = self.detect_intent(query)

        if intent == 'chart':
            result = self.generate_chart(query)
            self.chat_history[-1]['assistant'] = result['message']
            if result.get('image_base64'):
                self.chat_history[-1]['chart'] = result['image_base64']
            return result

        elif intent == 'statistical':
            msg = self.get_statistical_answer(query)
            self.chat_history[-1]['assistant'] = msg
            return {'success': True, 'message': msg, 'response_type': 'text'}

        else:
            msg = self.get_llm_response(query)
            self.chat_history[-1]['assistant'] = msg
            return {'success': True, 'message': msg, 'response_type': 'text'}

    def get_summary_report(self) -> Dict[str, Any]:
        if self.df is None:
            return {'success': False, 'message': 'No data loaded'}
        return {'success': True, 'summary': self.summary_stats, 'chat_history': self.chat_history}

    def reset(self):
        self.df = None
        self.summary_stats = {}
        self.chat_history = []
