import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("work.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Convert to datetime if date column exists
    if 'fecha_contratacion' in df.columns:
        df['fecha_contratacion'] = pd.to_datetime(df['fecha_contratacion'])
    return df

df = load_data()

# Page configuration
st.set_page_config(
    page_title="Employee Analytics Dashboard",
    layout="wide",
    page_icon="📊"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .st-emotion-cache-1v0mbdj {
        border-radius: 10px;
    }
    .tab-container {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header section
st.title("📊 Employee Analytics Dashboard")
st.markdown("""
Explore workforce metrics, employee satisfaction, and productivity trends across departments.
""")

# Filter panel in sidebar
st.sidebar.header("🔍 Filters")

# Date filter (if date column exists)
if 'fecha_contratacion' in df.columns:
    min_date = df['fecha_contratacion'].min().date()
    max_date = df['fecha_contratacion'].max().date()
    date_range = st.sidebar.date_input(
        "Hire Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    date_range = None

# Other filters
deptos = st.sidebar.multiselect(
    "Department", 
    df["departamento"].unique(), 
    default=df["departamento"].unique(),
    key="dept_filter"
)

generos = st.sidebar.multiselect(
    "Gender", 
    df["genero"].unique(), 
    default=df["genero"].unique(),
    key="gender_filter"
)

modalidades = st.sidebar.multiselect(
    "Work Mode", 
    df["modalidad_trabajo"].unique(), 
    default=df["modalidad_trabajo"].unique(),
    key="work_mode_filter"
)

# Age range filter
age_min, age_max = st.sidebar.slider(
    "Age Range",
    min_value=int(df["edad"].min()),
    max_value=int(df["edad"].max()),
    value=(int(df["edad"].min()), int(df["edad"].max()))
)

# Apply filters
def apply_filters(df):
    filtered_df = df[
        (df["departamento"].isin(deptos)) &
        (df["genero"].isin(generos)) &
        (df["modalidad_trabajo"].isin(modalidades)) &
        (df["edad"] >= age_min) &
        (df["edad"] <= age_max)
    ]
    
    if date_range and 'fecha_contratacion' in df.columns:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_df = filtered_df[
            (filtered_df['fecha_contratacion'] >= start_date) & 
            (filtered_df['fecha_contratacion'] <= end_date)
        ]
    
    return filtered_df

filtro_df = apply_filters(df)

# Reset filters button
if st.sidebar.button("Reset All Filters"):
    st.rerun()

# KPI Cards
st.markdown("## 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("👥 Total Employees", len(filtro_df))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("😊 Avg Satisfaction", f"{round(filtro_df['satisfaccion_laboral'].mean(), 2)}/10")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📈 Avg Productivity", f"{round(filtro_df['productividad_score'].mean(), 2)}/100")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("😫 Avg Stress Level", f"{round(filtro_df['nivel_estres'].mean(), 2)}/10")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Visualization tabs
tab1, tab2, tab3 = st.tabs(["📊 Workforce Distribution", "📈 Performance Metrics", "🔍 Deep Dive Analysis"])

with tab1:
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Department distribution
        dept_counts = filtro_df["departamento"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        
        bar_fig = px.bar(
            dept_counts,
            x="Department",
            y="Count",
            color="Department",
            labels={"Department": "Department", "Count": "Number of Employees"},
            title="Employee Distribution by Department",
            height=400
        )
        bar_fig.update_layout(showlegend=False)
        st.plotly_chart(bar_fig, use_container_width=True)
    
    with col2:
        # Education level distribution
        pie_fig = px.pie(
            filtro_df, 
            names="nivel_educacion",
            title="Education Level Distribution",
            height=400
        )
        pie_fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(pie_fig, use_container_width=True)
    
    # Age distribution
    hist_fig = px.histogram(
        filtro_df, 
        x="edad",
        nbins=20,
        title="Age Distribution",
        color="genero",
        barmode="overlay",
        opacity=0.7,
        labels={"edad": "Age", "genero": "Gender"}
    )
    st.plotly_chart(hist_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Weekly hours by department
        box_fig = px.box(
            filtro_df, 
            x="departamento", 
            y="horas_semanales",
            color="departamento",
            title="Weekly Hours by Department",
            labels={"departamento": "Department", "horas_semanales": "Weekly Hours"},
            height=400
        )
        box_fig.update_layout(showlegend=False)
        st.plotly_chart(box_fig, use_container_width=True)
    
    with col2:
        # Productivity distribution
        hist_fig = px.histogram(
            filtro_df, 
            x="productividad_score",
            nbins=20,
            title="Productivity Score Distribution",
            color="departamento",
            labels={"productividad_score": "Productivity Score"},
            height=400
        )
        st.plotly_chart(hist_fig, use_container_width=True)
    
    # Scatter plot: Satisfaction vs Stress (without trendline)
    scatter_fig = px.scatter(
        filtro_df, 
        x="satisfaccion_laboral", 
        y="nivel_estres",
        color="departamento",
        hover_data=["edad", "genero", "modalidad_trabajo"],
        title="Job Satisfaction vs Stress Level",
        labels={
            "satisfaccion_laboral": "Job Satisfaction (1-10)",
            "nivel_estres": "Stress Level (1-10)",
            "departamento": "Department"
        }
        # Removed trendline parameter to avoid statsmodels dependency
    )
    st.plotly_chart(scatter_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    # Correlation heatmap (numerical columns only)
    numerical_cols = filtro_df.select_dtypes(include=['int64', 'float64']).columns
    if len(numerical_cols) > 1:
        corr_matrix = filtro_df[numerical_cols].corr()
        heatmap_fig = px.imshow(
            corr_matrix,
            text_auto=True,
            title="Correlation Matrix",
            color_continuous_scale='RdBu',
            range_color=[-1, 1]
        )
        st.plotly_chart(heatmap_fig, use_container_width=True)
    else:
        st.warning("Not enough numerical columns for correlation analysis")
    
    # Interactive cross-filtering
    st.markdown("### 🔗 Interactive Exploration")
    selected_points = st.selectbox(
        "Select a department to highlight across all visualizations:",
        options=["All"] + list(filtro_df["departamento"].unique())
    )
    
    if selected_points != "All":
        highlight_df = filtro_df[filtro_df["departamento"] == selected_points]
    else:
        highlight_df = filtro_df
    
    # Show raw data option
    if st.checkbox("Show filtered data table"):
        st.dataframe(filtro_df)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Created with Streamlit + Plotly • © 2025 • Data last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))