import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

# Set page config
st.set_page_config(
    page_title="Employee Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv('work.csv')
    
    # Clean data
    df['salario_anual'] = pd.to_numeric(df['salario_anual'], errors='coerce')
    df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
    df['experiencia_anos'] = pd.to_numeric(df['experiencia_anos'], errors='coerce')
    
    # Create derived columns
    df['work_life_balance_score'] = (
        df['horas_sueno_noche'] * 0.4 + 
        df['horas_ocio_semana'] * 0.3 +
        (50 - df['horas_semanales']) * 0.3
    )
    
    # Map numeric education levels
    education_order = {
        'Bachillerato': 1,
        'Licenciatura': 2,
        'Maestría': 3,
        'Doctorado': 4
    }
    df['education_level_num'] = df['nivel_educacion'].map(education_order)
    
    # Create a count column for visualizations
    df['count'] = 1
    
    return df

df = load_data()

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .st-bw {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .header {
        color: #2c3e50;
    }
    .kpi-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .kpi-title {
        font-size: 14px;
        color: #7f8c8d;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar filters
with st.sidebar:
    st.title("📊 Filters")
    
    departments = st.multiselect(
        "Department",
        options=df['departamento'].unique(),
        default=df['departamento'].unique()
    )
    
    education_levels = st.multiselect(
        "Education Level",
        options=df['nivel_educacion'].unique(),
        default=df['nivel_educacion'].unique()
    )
    
    zones = st.multiselect(
        "Geographic Zone",
        options=df['zona_geografica'].unique(),
        default=df['zona_geografica'].unique()
    )
    
    work_modes = st.multiselect(
        "Work Modality",
        options=df['modalidad_trabajo'].unique(),
        default=df['modalidad_trabajo'].unique()
    )
    
    age_range = st.slider(
        "Age Range",
        min_value=int(df['edad'].min()),
        max_value=int(df['edad'].max()),
        value=(int(df['edad'].min()), int(df['edad'].max()))
    )
    
    salary_range = st.slider(
        "Salary Range (Annual)",
        min_value=int(df['salario_anual'].min()),
        max_value=int(df['salario_anual'].max()),
        value=(int(df['salario_anual'].min()), int(df['salario_anual'].max()))
    )

# Apply filters
filtered_df = df[
    (df['departamento'].isin(departments)) &
    (df['nivel_educacion'].isin(education_levels)) &
    (df['zona_geografica'].isin(zones)) &
    (df['modalidad_trabajo'].isin(work_modes)) &
    (df['edad'] >= age_range[0]) &
    (df['edad'] <= age_range[1]) &
    (df['salario_anual'] >= salary_range[0]) &
    (df['salario_anual'] <= salary_range[1])
]

# Header
st.title("Employee Analytics Dashboard")
st.markdown("Interactive visualization of employee demographics, compensation, and work patterns")

# KPI Cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown('<div class="kpi-card"><div class="kpi-title">Total Employees</div><div class="kpi-value">{:,}</div></div>'.format(len(filtered_df)), unsafe_allow_html=True)
with col2:
    st.markdown('<div class="kpi-card"><div class="kpi-title">Avg Salary</div><div class="kpi-value">${:,.0f}</div></div>'.format(filtered_df['salario_anual'].mean()), unsafe_allow_html=True)
with col3:
    st.markdown('<div class="kpi-card"><div class="kpi-title">Avg Work Hours</div><div class="kpi-value">{:.1f}</div></div>'.format(filtered_df['horas_semanales'].mean()), unsafe_allow_html=True)
with col4:
    st.markdown('<div class="kpi-card"><div class="kpi-title">Avg Stress Level</div><div class="kpi-value">{:.1f}/10</div></div>'.format(filtered_df['nivel_estres'].mean()), unsafe_allow_html=True)
with col5:
    st.markdown('<div class="kpi-card"><div class="kpi-title">Avg Productivity</div><div class="kpi-value">{:.1f}/10</div></div>'.format(filtered_df['productividad_score'].mean()), unsafe_allow_html=True)

# Main visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Salary Analysis", 
    "Geographic Distribution", 
    "Work-Life Balance",
    "Education & Experience",
    "Department Composition"
])

with tab1:
    st.subheader("Salary Distribution by Department")
    col1, col2 = st.columns([3, 1])
    with col1:
        fig1 = px.box(
            filtered_df,
            x='departamento',
            y='salario_anual',
            color='departamento',
            points="all",
            hover_data=['nivel_educacion', 'experiencia_anos'],
            title="Salary Distribution by Department"
        )
        fig1.update_traces(boxmean=True)
        fig1.update_layout(
            xaxis_title="Department",
            yaxis_title="Annual Salary",
            showlegend=False
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("### Insights")
        st.write("""
        - Hover over points to see education and experience details
        - The line in the middle of each box shows the median salary
        - Wider boxes indicate more salary variability in that department
        - Points outside the whiskers may represent outliers
        """)

with tab2:
    st.subheader("Geographic Distribution of Employees")
    
    # Create a count by city
    city_counts = filtered_df['ciudad'].value_counts().reset_index()
    city_counts.columns = ['ciudad', 'count']
    
    # Create a map figure
    fig2 = px.scatter_geo(
        city_counts,
        locationmode='country names',
        locations=['Mexico'] * len(city_counts),
        lat=filtered_df.groupby('ciudad')['ciudad'].first().apply(lambda x: 19.4326 if x == 'Ciudad de México' else 20.9674),  # Simplified coordinates
        lon=filtered_df.groupby('ciudad')['ciudad'].first().apply(lambda x: -99.1332 if x == 'Ciudad de México' else -89.5926),
        size='count',
        hover_name='ciudad',
        hover_data={'count': True},
        projection="natural earth",
        title="Employee Distribution by City"
    )
    
    fig2.update_geos(
        visible=False, resolution=50,
        showcountries=True, countrycolor="Black",
        showsubunits=True, subunitcolor="Blue"
    )
    
    fig2.update_layout(
        geo=dict(
            scope='north america',
            center=dict(lat=23, lon=-102),
            projection_scale=5
        )
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Employees by Geographic Zone")
        fig2a = px.pie(
            filtered_df,
            names='zona_geografica',
            hole=0.3,
            title="Employee Distribution by Zone"
        )
        st.plotly_chart(fig2a, use_container_width=True)
    
    with col2:
        st.markdown("### Avg Salary by Zone")
        fig2b = px.bar(
            filtered_df.groupby('zona_geografica')['salario_anual'].mean().reset_index(),
            x='zona_geografica',
            y='salario_anual',
            color='zona_geografica',
            title="Average Salary by Geographic Zone"
        )
        fig2b.update_layout(showlegend=False)
        st.plotly_chart(fig2b, use_container_width=True)

with tab3:
    st.subheader("Work-Life Balance Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        fig3a = px.parallel_coordinates(
            filtered_df,
            dimensions=[
                'horas_semanales',
                'horas_ejercicio_semana',
                'horas_ocio_semana',
                'horas_sueno_noche',
                'nivel_estres',
                'work_life_balance_score'
            ],
            color='work_life_balance_score',
            color_continuous_scale=px.colors.diverging.RdYlGn,
            title="Work-Life Balance Metrics"
        )
        st.plotly_chart(fig3a, use_container_width=True)
    
    with col2:
        fig3b = px.scatter(
            filtered_df,
            x='horas_semanales',
            y='work_life_balance_score',
            color='departamento',
            hover_data=['ciudad', 'modalidad_trabajo'],
            title="Work Hours vs. Work-Life Balance Score"
        )
        st.plotly_chart(fig3b, use_container_width=True)
    
    st.markdown("""
    **Work-Life Balance Score Calculation:**
    - 40% weight to sleep hours (7-9 recommended)
    - 30% weight to leisure hours
    - 30% weight to inverse of work hours (less hours = better score)
    """)

with tab4:
    st.subheader("Education & Experience Analysis")
    
    fig4 = px.scatter_3d(
        filtered_df,
        x='experiencia_anos',
        y='education_level_num',
        z='salario_anual',
        color='departamento',
        size='productividad_score',
        hover_name='nivel_educacion',
        hover_data=['ciudad', 'modalidad_trabajo'],
        labels={
            'education_level_num': 'Education Level',
            'experiencia_anos': 'Years of Experience',
            'salario_anual': 'Annual Salary'
        },
        title="Education, Experience & Salary (3D View)"
    )
    
    # Update education level labels
    fig4.update_layout(
        scene=dict(
            yaxis=dict(
                ticktext=['Bachillerato', 'Licenciatura', 'Maestría', 'Doctorado'],
                tickvals=[1, 2, 3, 4]
            )
        )
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("""
    **Interactions:**
    - Rotate the chart by clicking and dragging
    - Zoom in/out using mouse wheel
    - Hover over points for details
    - Larger bubbles indicate higher productivity scores
    """)

with tab5:
    st.subheader("Department Composition Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        # Use the count column we created earlier
        fig5a = px.sunburst(
            filtered_df,
            path=['departamento', 'nivel_educacion', 'modalidad_trabajo'],
            values='count',
            title="Department Composition by Education & Work Mode"
        )
        st.plotly_chart(fig5a, use_container_width=True)
    
    with col2:
        fig5b = px.treemap(
            filtered_df,
            path=['departamento', 'genero', 'estado_civil'],
            values='count',
            color='salario_anual',
            color_continuous_scale='RdBu',
            title="Department Composition by Gender & Marital Status"
        )
        st.plotly_chart(fig5b, use_container_width=True)
    
    st.markdown("""
    **Interactions:**
    - Click on any segment to drill down
    - Hover for detailed breakdowns
    - The size represents the count of employees
    - Color represents average salary (right chart)
    """)

# Footer
st.markdown("---")
st.markdown("""
**Dashboard Features:**
- Interactive filters in the sidebar
- Hover tooltips on all charts
- Drill-down capabilities
- Responsive design
- Real-time updates when filters change
""")
