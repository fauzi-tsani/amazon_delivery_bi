"""
Interactive Dashboard for Amazon Delivery Data Warehouse
"""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Amazon Delivery Analytics"

df = None

def load_data():
    """Load data from CSV"""
    global df
    try:
        df = pd.read_csv('amazon_delivery.csv')
        df['Order_Date'] = pd.to_datetime(df['Order_Date'])
        df['Order_Year'] = df['Order_Date'].dt.year
        df['Order_Month'] = df['Order_Date'].dt.month
        df['Order_Weekday'] = df['Order_Date'].dt.day_name()
        
        # Calculate Distance_KM using Haversine formula
        def haversine_distance(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius in kilometers
            lat1_rad = np.radians(lat1)
            lat2_rad = np.radians(lat2)
            delta_lat = np.radians(lat2 - lat1)
            delta_lon = np.radians(lon2 - lon1)
            
            a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            return R * c
        
        df['Distance_KM'] = haversine_distance(
            df['Store_Latitude'], df['Store_Longitude'],
            df['Drop_Latitude'], df['Drop_Longitude']
        )
        
        # Derived metrics
        df['Performance_Category'] = df['Delivery_Time'].apply(
            lambda x: 'Fast' if x <= 60 else 'Normal' if x <= 120 else 'Slow'
        )
        df['Rating_Category'] = df['Agent_Rating'].apply(
            lambda x: 'Excellent' if x >= 4.5 else 'Good' if x >= 4.0 else 'Average'
        )
        
        print(f"✓ Loaded {len(df)} records with Distance_KM calculated")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("📊 Amazon Delivery Analytics", className="text-center mt-4 mb-2"),
            html.P("Business Intelligence Dashboard", className="text-center text-muted mb-4")
        ])
    ]),
    
    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Date Range:", className="font-weight-bold"),
            dcc.DatePickerRange(
                id='date-filter',
                start_date='2022-01-01',
                end_date='2022-12-31'
            )
        ], width=3),
        dbc.Col([
            html.Label("Area:", className="font-weight-bold"),
            dcc.Dropdown(id='area-filter', options=[], multi=True, placeholder="Select Area...")
        ], width=3),
        dbc.Col([
            html.Label("Category:", className="font-weight-bold"),
            dcc.Dropdown(id='category-filter', options=[], multi=True, placeholder="Select Category...")
        ], width=3),
        dbc.Col([
            html.Label("Weather:", className="font-weight-bold"),
            dcc.Dropdown(id='weather-filter', options=[], multi=True, placeholder="Select Weather...")
        ], width=3),
    ], className="mb-4 p-3", style={'backgroundColor': '#ECF0F1', 'borderRadius': '10px'}),
    
    # KPI Cards
    html.Div(id='kpi-cards'),
    
    # Charts
    dbc.Tabs([
        dbc.Tab(label="📊 Executive Summary", children=[
            dbc.Row([
                dbc.Col([dcc.Graph(id='chart1')], width=6),
                dbc.Col([dcc.Graph(id='chart2')], width=6),
            ]),
        ]),
        dbc.Tab(label="🚚 Delivery Performance", children=[
            dbc.Row([
                dbc.Col([dcc.Graph(id='chart3')], width=6),
                dbc.Col([dcc.Graph(id='chart4')], width=6),
            ]),
        ]),
        dbc.Tab(label="👤 Agent Performance", children=[
            dbc.Row([
                dbc.Col([dcc.Graph(id='chart5')], width=12),
            ]),
        ]),
    ]),
    
], fluid=True)

# Callback to update filter options
@app.callback(
    [Output('area-filter', 'options'),
     Output('category-filter', 'options'),
     Output('weather-filter', 'options')],
    Input('date-filter', 'start_date')
)
def update_filter_options(_):
    if df is None:
        return [], [], []
    
    # Filter out NaN values and convert to strings for consistent sorting
    areas = sorted([str(a) for a in df['Area'].unique() if pd.notna(a)])
    categories = sorted([str(c) for c in df['Category'].unique() if pd.notna(c)])
    weathers = sorted([str(w) for w in df['Weather'].unique() if pd.notna(w)])
    
    return (
        [{'label': a, 'value': a} for a in areas],
        [{'label': c, 'value': c} for c in categories],
        [{'label': w, 'value': w} for w in weathers]
    )

# Filter function
def filter_data(start_date, end_date, area, category, weather):
    """Apply all filters to dataframe"""
    if df is None:
        return None
    
    filtered = df.copy()
    
    # Date filter
    if start_date and end_date:
        filtered = filtered[
            (filtered['Order_Date'] >= start_date) & 
            (filtered['Order_Date'] <= end_date)
        ]
    
    # Area filter (multi-select)
    if area and len(area) > 0:
        filtered = filtered[filtered['Area'].isin(area)]
    
    # Category filter (multi-select)
    if category and len(category) > 0:
        filtered = filtered[filtered['Category'].isin(category)]
    
    # Weather filter (multi-select)
    if weather and len(weather) > 0:
        filtered = filtered[filtered['Weather'].isin(weather)]
    
    return filtered

# Callback for KPI cards
@app.callback(
    Output('kpi-cards', 'children'),
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('area-filter', 'value'),
     Input('category-filter', 'value'),
     Input('weather-filter', 'value')]
)
def update_kpi_cards(start_date, end_date, area, category, weather):
    filtered = filter_data(start_date, end_date, area, category, weather)
    
    if filtered is None or len(filtered) == 0:
        return html.Div("No data available for selected filters", className="text-center text-danger")
    
    total_orders = len(filtered)
    avg_delivery_time = filtered['Delivery_Time'].mean()
    avg_rating = filtered['Agent_Rating'].mean()
    total_distance = filtered['Distance_KM'].sum() if 'Distance_KM' in filtered.columns else 0
    on_time_rate = (filtered['Performance_Category'] == 'Fast').mean() * 100
    
    cards = dbc.Row([
        dbc.Col(create_kpi_card("Total Orders", f"{total_orders:,}", "#3498DB", "📦"), width=2),
        dbc.Col(create_kpi_card("Avg Delivery", f"{avg_delivery_time:.1f} min", "#E74C3C", "⏱️"), width=2),
        dbc.Col(create_kpi_card("Agent Rating", f"{avg_rating:.2f} ⭐", "#F39C12", "👤"), width=2),
        dbc.Col(create_kpi_card("Total Distance", f"{total_distance:.0f} km", "#27AE60", "🛣️"), width=2),
        dbc.Col(create_kpi_card("On-Time Rate", f"{on_time_rate:.1f}%", "#9B59B6", "✅"), width=2),
    ], className="mb-4")
    
    return cards

def create_kpi_card(title, value, color, icon):
    return dbc.Card([
        dbc.CardBody([
            html.H4(icon, className="text-center mb-2"),
            html.H5(value, className="text-center font-weight-bold", style={'color': color}),
            html.P(title, className="text-center text-muted", style={'fontSize': '12px'}),
        ])
    ], style={'border': f'2px solid {color}', 'borderRadius': '10px'})

# Chart callbacks
@app.callback(
    Output('chart1', 'figure'),
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('area-filter', 'value'),
     Input('category-filter', 'value'),
     Input('weather-filter', 'value')]
)
def update_chart1(start_date, end_date, area, category, weather):
    filtered = filter_data(start_date, end_date, area, category, weather)
    if filtered is None or len(filtered) == 0:
        return go.Figure()
    
    fig = px.histogram(filtered, x='Delivery_Time', color='Performance_Category',
                       title='Delivery Time Distribution',
                       color_discrete_sequence=px.colors.sequential.Viridis)
    fig.update_layout(template='plotly_dark', height=400)
    return fig

@app.callback(
    Output('chart2', 'figure'),
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('area-filter', 'value'),
     Input('category-filter', 'value'),
     Input('weather-filter', 'value')]
)
def update_chart2(start_date, end_date, area, category, weather):
    filtered = filter_data(start_date, end_date, area, category, weather)
    if filtered is None or len(filtered) == 0:
        return go.Figure()
    
    perf_counts = filtered['Performance_Category'].value_counts()
    colors = {'Fast': '#27AE60', 'Normal': '#F39C12', 'Slow': '#E74C3C'}
    
    fig = go.Figure(data=[go.Pie(
        labels=perf_counts.index,
        values=perf_counts.values,
        hole=0.4,
        marker_colors=[colors.get(l, '#3498DB') for l in perf_counts.index]
    )])
    fig.update_layout(title='Performance Distribution', template='plotly_dark', height=400)
    return fig

@app.callback(
    Output('chart3', 'figure'),
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('area-filter', 'value'),
     Input('category-filter', 'value'),
     Input('weather-filter', 'value')]
)
def update_chart3(start_date, end_date, area, category, weather):
    filtered = filter_data(start_date, end_date, area, category, weather)
    if filtered is None or len(filtered) == 0:
        return go.Figure()
    
    fig = px.box(filtered, x='Category', y='Delivery_Time', color='Category',
                 title='Delivery Time by Category')
    fig.update_layout(template='plotly_dark', height=400, xaxis_tickangle=-45)
    return fig

@app.callback(
    Output('chart4', 'figure'),
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('area-filter', 'value'),
     Input('category-filter', 'value'),
     Input('weather-filter', 'value')]
)
def update_chart4(start_date, end_date, area, category, weather):
    filtered = filter_data(start_date, end_date, area, category, weather)
    if filtered is None or len(filtered) == 0:
        return go.Figure()
    
    fig = px.box(filtered, x='Area', y='Delivery_Time', color='Area',
                 title='Delivery Time by Area')
    fig.update_layout(template='plotly_dark', height=400)
    return fig

@app.callback(
    Output('chart5', 'figure'),
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('area-filter', 'value'),
     Input('category-filter', 'value'),
     Input('weather-filter', 'value')]
)
def update_chart5(start_date, end_date, area, category, weather):
    filtered = filter_data(start_date, end_date, area, category, weather)
    if filtered is None or len(filtered) == 0:
        return go.Figure()
    
    agent_perf = filtered.groupby('Agent_Age')['Agent_Rating'].mean().reset_index()
    fig = px.scatter(agent_perf, x='Agent_Age', y='Agent_Rating', 
                     title='Agent Performance by Age',
                     trendline='ols', size='Agent_Rating')
    fig.update_layout(template='plotly_dark', height=400)
    return fig

if __name__ == '__main__':
    print("="*60)
    print("AMAZON DELIVERY ANALYTICS DASHBOARD")
    print("="*60)
    print("\nLoading data...")
    load_data()
    print("\nStarting server...")
    print("Access at: http://127.0.0.1:8050")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=8050)
