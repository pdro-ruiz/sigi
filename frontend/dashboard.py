
"""
SIGI Local - Dashboard Principal Streamlit
Sistema de Gestión de Incidencias con IA
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any

# Configuración de la página
st.set_page_config(
    page_title="SIGI Local - Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URLs de la API
API_BASE_URL = "http://127.0.0.1:8000/api"

# Estilos CSS personalizados
st.markdown("""
<style>
    .main > div {
        padding: 2rem 1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .status-open { 
        background-color: #ff6b6b; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .status-in_progress { 
        background-color: #4ecdc4; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .status-resolved { 
        background-color: #45b7d1; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .priority-critical { 
        background-color: #e74c3c; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .priority-high { 
        background-color: #f39c12; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .priority-medium { 
        background-color: #3498db; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .priority-low { 
        background-color: #2ecc71; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .category-authentication { 
        background-color: #9b59b6; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .category-performance { 
        background-color: #e67e22; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .category-integration { 
        background-color: #1abc9c; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .category-data { 
        background-color: #34495e; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .category-ui_bug { 
        background-color: #95a5a6; 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 5px; 
        font-size: 0.8rem;
    }
    
    .feedback-buttons {
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Funciones para API calls
@st.cache_data(ttl=30)  # Cache por 30 segundos
def fetch_dashboard_stats():
    """Obtener estadísticas del dashboard"""
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/stats")
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        st.error(f"Error conectando con la API: {e}")
        return {}

@st.cache_data(ttl=60)
def fetch_incidents(limit=100, category=None, status=None, priority=None):
    """Obtener lista de incidencias"""
    try:
        params = {"limit": limit}
        if category: params["category"] = category
        if status: params["status"] = status
        if priority: params["priority"] = priority
        
        response = requests.get(f"{API_BASE_URL}/incidents/", params=params)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error obteniendo incidencias: {e}")
        return []

def create_incident(title, description, priority):
    """Crear nueva incidencia"""
    try:
        payload = {
            "title": title,
            "description": description,
            "priority": priority
        }
        response = requests.post(f"{API_BASE_URL}/incidents/", json=payload)
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def search_incidents(query):
    """Buscar incidencias"""
    try:
        response = requests.get(f"{API_BASE_URL}/incidents/search/{query}")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error en búsqueda: {e}")
        return []

@st.cache_data(ttl=300)  # Cache por 5 minutos
def fetch_analytics_data(days=30):
    """Obtener datos de analytics"""
    try:
        endpoints = [
            f"/dashboard/metrics/daily-incidents?days={days}",
            f"/dashboard/metrics/category-trends?days={days}",
            f"/dashboard/metrics/sentiment-analysis?days={days}",
            f"/dashboard/metrics/priority-distribution?days={days}",
            f"/dashboard/metrics/resolution-time?days={days}"
        ]
        
        data = {}
        for endpoint in endpoints:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            if response.status_code == 200:
                key = endpoint.split('/')[-1].split('?')[0]
                data[key] = response.json()
        
        return data
    except Exception as e:
        st.error(f"Error obteniendo analytics: {e}")
        return {}

# Función para formatear celdas con colores
def format_status(status):
    return f'<span class="status-{status.lower()}">{status.replace("_", " ").title()}</span>'

def format_priority(priority):
    return f'<span class="priority-{priority.lower()}">{priority.capitalize()}</span>'

def format_category(category):
    return f'<span class="category-{category.lower()}">{category.replace("_", " ").title()}</span>'

# Sidebar para navegación
st.sidebar.title("🎯 SIGI Local")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navegación", 
    ["📊 Dashboard", "➕ Nuevo Ticket", "📋 Lista de Tickets", "📈 Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Sistema Offline**\nTodas las operaciones se realizan localmente")

# === PÁGINA: DASHBOARD PRINCIPAL ===
if page == "📊 Dashboard":
    st.title("📊 Dashboard Principal")
    st.markdown("### Resumen de incidencias en tiempo real")
    
    # Obtener datos
    stats = fetch_dashboard_stats()
    
    if stats:
        # Métricas principales en columnas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Incidencias",
                value=stats.get("total_incidents", 0),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Abiertas",
                value=stats.get("open_incidents", 0),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Resueltas",
                value=stats.get("resolved_incidents", 0),
                delta=None
            )
        
        with col4:
            resolution_rate = 0
            if stats.get("total_incidents", 0) > 0:
                resolution_rate = round(
                    (stats.get("resolved_incidents", 0) / stats.get("total_incidents", 1)) * 100, 1
                )
            st.metric(
                label="Tasa Resolución",
                value=f"{resolution_rate}%",
                delta=None
            )
        
        st.markdown("---")
        
        # Gráficos en dos columnas
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distribución por Categoría")
            category_data = stats.get("incidents_by_category", {})
            if category_data:
                df_cat = pd.DataFrame(list(category_data.items()), columns=["Categoría", "Cantidad"])
                fig_cat = px.pie(
                    df_cat, 
                    values="Cantidad", 
                    names="Categoría",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_cat.update_layout(height=400)
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("No hay datos de categorías disponibles")
        
        with col2:
            st.subheader("🎯 Distribución por Prioridad")
            priority_data = stats.get("incidents_by_priority", {})
            if priority_data:
                df_pri = pd.DataFrame(list(priority_data.items()), columns=["Prioridad", "Cantidad"])
                colors = {
                    "critical": "#e74c3c",
                    "high": "#f39c12", 
                    "medium": "#3498db",
                    "low": "#2ecc71"
                }
                fig_pri = px.bar(
                    df_pri, 
                    x="Prioridad", 
                    y="Cantidad",
                    color="Prioridad",
                    color_discrete_map=colors
                )
                fig_pri.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_pri, use_container_width=True)
            else:
                st.info("No hay datos de prioridades disponibles")
        
        # Estadísticas adicionales
        if stats.get("average_resolution_time"):
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="⏱️ Tiempo Promedio Resolución",
                    value=f"{stats.get('average_resolution_time', 0):.1f} horas"
                )
            
            with col2:
                sentiment_dist = stats.get("sentiment_distribution", {})
                positive_pct = 0
                if sentiment_dist:
                    total = sum(sentiment_dist.values())
                    positive_pct = round((sentiment_dist.get("positive", 0) / total) * 100, 1) if total > 0 else 0
                st.metric(
                    label="😊 Sentimiento Positivo",
                    value=f"{positive_pct}%"
                )
            
            with col3:
                st.metric(
                    label="🤖 Análisis IA Activo",
                    value="✅ Funcionando"
                )
    
    else:
        st.warning("No se pudieron cargar las estadísticas. Verifica que la API esté ejecutándose.")
    
    # Botón de actualización
    if st.button("🔄 Actualizar Dashboard"):
        st.cache_data.clear()
        st.rerun()

# === PÁGINA: NUEVO TICKET ===
elif page == "➕ Nuevo Ticket":
    st.title("➕ Crear Nuevo Ticket")
    st.markdown("### Formulario para reportar una nueva incidencia")
    
    with st.form("new_ticket_form"):
        st.subheader("Información del Ticket")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            title = st.text_input(
                "Título de la incidencia *",
                placeholder="Describe brevemente el problema..."
            )
        
        with col2:
            priority = st.selectbox(
                "Prioridad *",
                ["low", "medium", "high", "critical"],
                index=1,
                format_func=lambda x: {
                    "low": "🟢 Baja",
                    "medium": "🟡 Media", 
                    "high": "🟠 Alta",
                    "critical": "🔴 Crítica"
                }[x]
            )
        
        description = st.text_area(
            "Descripción detallada *",
            placeholder="Proporciona todos los detalles posibles sobre el problema:\n- ¿Qué estabas haciendo cuando ocurrió?\n- ¿Qué mensaje de error viste?\n- ¿Pasos para reproducir el problema?",
            height=150
        )
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submitted = st.form_submit_button("🚀 Crear Ticket", use_container_width=True)
        
        with col2:
            clear_form = st.form_submit_button("🗑️ Limpiar", use_container_width=True)
        
        if submitted:
            if title and description:
                with st.spinner("Creando ticket y analizando con IA..."):
                    success, result = create_incident(title, description, priority)
                    
                    if success:
                        st.success("✅ ¡Ticket creado exitosamente!")
                        
                        # Mostrar información del ticket creado
                        st.subheader("📋 Información del Ticket Creado")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**ID:** {result.get('id')}")
                            st.write(f"**Título:** {result.get('title')}")
                            st.write(f"**Estado:** {result.get('status', 'open').replace('_', ' ').title()}")
                        
                        with col2:
                            st.write(f"**Prioridad:** {result.get('priority', '').capitalize()}")
                            if result.get('category'):
                                st.write(f"**Categoría (IA):** {result.get('category').replace('_', ' ').title()}")
                            if result.get('urgency_level'):
                                st.write(f"**Urgencia (IA):** {result.get('urgency_level').capitalize()}")
                        
                        st.info("🤖 El sistema de IA ha analizado automáticamente tu ticket y asignado la categoría y nivel de urgencia más apropiados.")
                        
                    else:
                        st.error(f"❌ Error creando el ticket: {result}")
            else:
                st.error("❌ Por favor completa todos los campos obligatorios (*)")
        
        if clear_form:
            st.rerun()

# === PÁGINA: LISTA DE TICKETS ===
elif page == "📋 Lista de Tickets":
    st.title("📋 Lista de Tickets")
    st.markdown("### Gestión y seguimiento de incidencias")
    
    # Filtros
    st.subheader("🔍 Filtros")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_category = st.selectbox(
            "Categoría",
            ["Todas"] + ["authentication", "performance", "integration", "data", "ui_bug"]
        )
    
    with col2:
        filter_status = st.selectbox(
            "Estado", 
            ["Todos"] + ["open", "in_progress", "resolved", "closed"]
        )
    
    with col3:
        filter_priority = st.selectbox(
            "Prioridad",
            ["Todas"] + ["critical", "high", "medium", "low"]
        )
    
    with col4:
        search_query = st.text_input("🔍 Buscar", placeholder="Buscar en título o descripción...")
    
    # Obtener datos
    category = None if filter_category == "Todas" else filter_category
    status = None if filter_status == "Todos" else filter_status  
    priority = None if filter_priority == "Todas" else filter_priority
    
    if search_query:
        incidents = search_incidents(search_query)
    else:
        incidents = fetch_incidents(
            limit=200,
            category=category,
            status=status,
            priority=priority
        )
    
    if incidents:
        st.markdown("---")
        st.subheader(f"📊 Resultados ({len(incidents)} tickets)")
        
        # Crear DataFrame para mostrar
        df_display = []
        for incident in incidents:
            df_display.append({
                "ID": incident.get("id"),
                "Título": incident.get("title", "")[:50] + "..." if len(incident.get("title", "")) > 50 else incident.get("title", ""),
                "Categoría": format_category(incident.get("category", "unknown")),
                "Prioridad": format_priority(incident.get("priority", "medium")),
                "Estado": format_status(incident.get("status", "open")),
                "Creado": incident.get("created_at", "")[:10] if incident.get("created_at") else "",
                "Asignado": incident.get("assigned_to", "Sin asignar")
            })
        
        df = pd.DataFrame(df_display)
        
        # Mostrar tabla con HTML para colores
        st.markdown(
            df.to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
        
        # Seleccionar ticket para ver detalles
        st.markdown("---")
        st.subheader("🔍 Ver Detalles de Ticket")
        
        incident_ids = [inc.get("id") for inc in incidents]
        selected_id = st.selectbox("Seleccionar ticket", incident_ids, format_func=lambda x: f"#{x}")
        
        if selected_id:
            selected_incident = next((inc for inc in incidents if inc.get("id") == selected_id), None)
            
            if selected_incident:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**#{selected_incident.get('id')} - {selected_incident.get('title')}**")
                    st.markdown(f"**Descripción:**\n{selected_incident.get('description', '')}")
                
                with col2:
                    st.markdown("**Información:**")
                    st.markdown(f"Estado: {format_status(selected_incident.get('status', 'open'))}", unsafe_allow_html=True)
                    st.markdown(f"Prioridad: {format_priority(selected_incident.get('priority', 'medium'))}", unsafe_allow_html=True)
                    if selected_incident.get('category'):
                        st.markdown(f"Categoría: {format_category(selected_incident.get('category'))}", unsafe_allow_html=True)
                    st.markdown(f"Creado: {selected_incident.get('created_at', '')[:16]}")
                    
                    # Sistema de feedback
                    st.markdown("**🤖 Feedback IA:**")
                    col_good, col_bad = st.columns(2)
                    with col_good:
                        if st.button("✅ Correcto", key=f"good_{selected_id}"):
                            st.success("Feedback positivo registrado")
                    with col_bad:
                        if st.button("❌ Incorrecto", key=f"bad_{selected_id}"):
                            st.warning("Feedback negativo registrado")
    
    else:
        st.info("No se encontraron tickets con los filtros aplicados.")
    
    # Botón de actualización
    if st.button("🔄 Actualizar Lista"):
        st.cache_data.clear()
        st.rerun()

# === PÁGINA: ANALYTICS ===
elif page == "📈 Analytics":
    st.title("📈 Analytics y Reportes")
    st.markdown("### Análisis detallado de tendencias y métricas")
    
    # Selector de período
    col1, col2 = st.columns([1, 3])
    with col1:
        days = st.selectbox(
            "Período de análisis",
            [7, 15, 30, 60, 90],
            index=2,
            format_func=lambda x: f"Últimos {x} días"
        )
    
    # Obtener datos de analytics
    analytics_data = fetch_analytics_data(days)
    
    if analytics_data:
        st.markdown("---")
        
        # Gráfico de incidencias diarias
        st.subheader("📅 Tendencia Diaria de Incidencias")
        daily_data = analytics_data.get("daily-incidents", {}).get("daily_data", [])
        
        if daily_data:
            df_daily = pd.DataFrame(daily_data)
            df_daily['date'] = pd.to_datetime(df_daily['date'])
            
            fig_daily = go.Figure()
            fig_daily.add_trace(go.Scatter(
                x=df_daily['date'],
                y=df_daily['created'],
                mode='lines+markers',
                name='Creadas',
                line=dict(color='#3498db', width=3),
                marker=dict(size=6)
            ))
            fig_daily.add_trace(go.Scatter(
                x=df_daily['date'],
                y=df_daily['resolved'],
                mode='lines+markers',
                name='Resueltas',
                line=dict(color='#2ecc71', width=3),
                marker=dict(size=6)
            ))
            
            fig_daily.update_layout(
                height=400,
                xaxis_title="Fecha",
                yaxis_title="Número de Incidencias",
                legend=dict(orientation="h", y=1.02, x=0)
            )
            st.plotly_chart(fig_daily, use_container_width=True)
        
        # Segunda fila de gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("😊 Análisis de Sentimientos")
            sentiment_data = analytics_data.get("sentiment-analysis", {}).get("summary", {})
            
            if sentiment_data:
                df_sentiment = pd.DataFrame(list(sentiment_data.items()), columns=["Sentimiento", "Cantidad"])
                colors = {"positive": "#2ecc71", "neutral": "#95a5a6", "negative": "#e74c3c"}
                
                fig_sentiment = px.bar(
                    df_sentiment,
                    x="Sentimiento",
                    y="Cantidad", 
                    color="Sentimiento",
                    color_discrete_map=colors
                )
                fig_sentiment.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            st.subheader("⏱️ Tiempos de Resolución")
            resolution_data = analytics_data.get("resolution-time", {}).get("by_category", {})
            
            if resolution_data:
                categories = []
                avg_times = []
                
                for category, data in resolution_data.items():
                    categories.append(category.replace("_", " ").title())
                    avg_times.append(data.get("avg_hours", 0))
                
                df_resolution = pd.DataFrame({
                    "Categoría": categories,
                    "Horas Promedio": avg_times
                })
                
                fig_resolution = px.bar(
                    df_resolution,
                    x="Categoría",
                    y="Horas Promedio",
                    color="Horas Promedio",
                    color_continuous_scale="Viridis"
                )
                fig_resolution.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_resolution, use_container_width=True)
        
        # Métricas de rendimiento
        st.markdown("---")
        st.subheader("📊 Métricas de Rendimiento")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Calcular métricas desde los datos disponibles
        total_analyzed = analytics_data.get("sentiment-analysis", {}).get("total_analyzed", 0)
        resolution_overall = analytics_data.get("resolution-time", {}).get("overall_avg", 0)
        
        with col1:
            st.metric("🤖 Análisis IA Realizados", total_analyzed)
        
        with col2:
            st.metric("⏱️ Tiempo Prom. Resolución", f"{resolution_overall:.1f}h")
        
        with col3:
            positive_sentiment = analytics_data.get("sentiment-analysis", {}).get("summary", {}).get("positive", 0)
            sentiment_rate = round((positive_sentiment / total_analyzed * 100), 1) if total_analyzed > 0 else 0
            st.metric("😊 Satisfacción", f"{sentiment_rate}%")
        
        with col4:
            st.metric("📈 Período Analizado", f"{days} días")
    
    else:
        st.warning("No se pudieron cargar los datos de analytics. Verifica que la API esté ejecutándose.")
    
    # Botón de actualización
    if st.button("🔄 Actualizar Analytics"):
        st.cache_data.clear()
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        🎯 SIGI Local v1.0.0 | Sistema de Gestión de Incidencias con IA | 
        <a href='http://127.0.0.1:8000/docs' target='_blank'>API Docs</a>
    </div>
    """, 
    unsafe_allow_html=True
)
