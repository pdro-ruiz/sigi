
"""
Componentes de gráficos reutilizables para el dashboard
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Any

class ChartComponents:
    """Clase para generar gráficos estandarizados"""
    
    @staticmethod
    def create_category_pie_chart(data: Dict[str, int]) -> go.Figure:
        """Crear gráfico de torta para categorías"""
        if not data:
            return go.Figure()
        
        df = pd.DataFrame(list(data.items()), columns=["Categoría", "Cantidad"])
        
        colors = {
            "authentication": "#9b59b6",
            "performance": "#e67e22", 
            "integration": "#1abc9c",
            "data": "#34495e",
            "ui_bug": "#95a5a6"
        }
        
        fig = px.pie(
            df,
            values="Cantidad",
            names="Categoría",
            color="Categoría",
            color_discrete_map=colors
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>"
        )
        
        fig.update_layout(
            height=400,
            font=dict(size=12),
            showlegend=True,
            legend=dict(orientation="h", y=-0.1)
        )
        
        return fig
    
    @staticmethod
    def create_priority_bar_chart(data: Dict[str, int]) -> go.Figure:
        """Crear gráfico de barras para prioridades"""
        if not data:
            return go.Figure()
        
        # Orden específico para prioridades
        priority_order = ["critical", "high", "medium", "low"]
        
        ordered_data = []
        for priority in priority_order:
            if priority in data:
                ordered_data.append((priority, data[priority]))
        
        if not ordered_data:
            ordered_data = list(data.items())
        
        df = pd.DataFrame(ordered_data, columns=["Prioridad", "Cantidad"])
        
        colors = {
            "critical": "#e74c3c",
            "high": "#f39c12",
            "medium": "#3498db", 
            "low": "#2ecc71"
        }
        
        fig = px.bar(
            df,
            x="Prioridad",
            y="Cantidad",
            color="Prioridad",
            color_discrete_map=colors
        )
        
        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Cantidad: %{y}<extra></extra>"
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Prioridad",
            yaxis_title="Cantidad",
            showlegend=False
        )
        
        return fig
    
    @staticmethod 
    def create_timeline_chart(data: List[Dict]) -> go.Figure:
        """Crear gráfico de línea temporal"""
        if not data:
            return go.Figure()
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        fig = go.Figure()
        
        # Línea de incidencias creadas
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['created'],
            mode='lines+markers',
            name='Creadas',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8, color='#3498db'),
            hovertemplate="<b>Creadas</b><br>Fecha: %{x}<br>Cantidad: %{y}<extra></extra>"
        ))
        
        # Línea de incidencias resueltas
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['resolved'],
            mode='lines+markers',
            name='Resueltas',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=8, color='#2ecc71'),
            hovertemplate="<b>Resueltas</b><br>Fecha: %{x}<br>Cantidad: %{y}<extra></extra>"
        ))
        
        fig.update_layout(
            height=400,
            xaxis_title="Fecha",
            yaxis_title="Número de Incidencias",
            legend=dict(orientation="h", y=1.02, x=0),
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def create_sentiment_chart(data: Dict[str, int]) -> go.Figure:
        """Crear gráfico de sentimientos"""
        if not data:
            return go.Figure()
        
        # Orden específico para sentimientos
        sentiment_order = ["positive", "neutral", "negative"]
        
        ordered_data = []
        for sentiment in sentiment_order:
            if sentiment in data:
                ordered_data.append((sentiment, data[sentiment]))
        
        if not ordered_data:
            ordered_data = list(data.items())
        
        df = pd.DataFrame(ordered_data, columns=["Sentimiento", "Cantidad"])
        
        colors = {
            "positive": "#2ecc71",
            "neutral": "#95a5a6",
            "negative": "#e74c3c"
        }
        
        labels = {
            "positive": "😊 Positivo",
            "neutral": "😐 Neutral", 
            "negative": "😞 Negativo"
        }
        
        df["Label"] = df["Sentimiento"].map(labels)
        
        fig = px.bar(
            df,
            x="Label",
            y="Cantidad",
            color="Sentimiento",
            color_discrete_map=colors
        )
        
        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Cantidad: %{y}<extra></extra>"
        )
        
        fig.update_layout(
            height=350,
            xaxis_title="Sentimiento",
            yaxis_title="Cantidad",
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_resolution_time_chart(data: Dict[str, Dict]) -> go.Figure:
        """Crear gráfico de tiempos de resolución por categoría"""
        if not data:
            return go.Figure()
        
        categories = []
        avg_times = []
        counts = []
        
        for category, stats in data.items():
            categories.append(category.replace("_", " ").title())
            avg_times.append(stats.get("avg_hours", 0))
            counts.append(stats.get("count", 0))
        
        df = pd.DataFrame({
            "Categoría": categories,
            "Tiempo Promedio (h)": avg_times,
            "Cantidad": counts
        })
        
        fig = px.bar(
            df,
            x="Categoría", 
            y="Tiempo Promedio (h)",
            color="Tiempo Promedio (h)",
            color_continuous_scale="RdYlGn_r",
            hover_data=["Cantidad"]
        )
        
        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Tiempo Promedio: %{y:.1f}h<br>Incidencias: %{customdata[0]}<extra></extra>"
        )
        
        fig.update_layout(
            height=350,
            xaxis_title="Categoría",
            yaxis_title="Tiempo Promedio (horas)",
            coloraxis_showscale=False
        )
        
        return fig
    
    @staticmethod
    def create_gauge_chart(value: float, title: str, max_value: float = 100) -> go.Figure:
        """Crear gráfico de gauge/velocímetro"""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title},
            delta = {'reference': max_value * 0.8},
            gauge = {
                'axis': {'range': [None, max_value]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, max_value * 0.5], 'color': "#ecf0f1"},
                    {'range': [max_value * 0.5, max_value * 0.8], 'color': "#bdc3c7"}
                ],
                'threshold': {
                    'line': {'color': "#e74c3c", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.9
                }
            }
        ))
        
        fig.update_layout(height=300)
        return fig
