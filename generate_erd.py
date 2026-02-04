"""
ERD (Entity Relationship Diagram) Generator
=============================================
Generates ERD for Amazon Delivery Data Warehouse
"""

import graphviz
from graphviz import Digraph
import os

OUTPUT_DIR = 'diagrams'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_erd():
    """
    Create Entity Relationship Diagram for Data Warehouse
    """
    print("="*60)
    print("ERD DIAGRAM GENERATION")
    print("="*60)
    
    # Create a new directed graph
    dot = Digraph(comment='Amazon Delivery Data Warehouse ERD', format='png')
    dot.attr(rankdir='TB', bgcolor='white', dpi='300')
    dot.attr('node', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial', fontsize='9')
    
    # Define Fact Table (Central Node)
    fact_attrs = [
        'PK: Delivery_Fact_ID',
        'FK: Agent_ID',
        'FK: Time_ID',
        'FK: Location_ID',
        'FK: Weather_ID',
        'FK: Vehicle_ID',
        'FK: Category_ID',
        'Order_Time',
        'Pickup_Time',
        'Distance_KM',
        'Pickup_Delay_Min',
        'Delivery_Time',
        'Speed_KM_H',
        'Performance_Category'
    ]
    
    fact_label = f'{{Fact_Deliveries|{" | ".join(fact_attrs)}}}'
    dot.node('Fact', fact_label, shape='record', style='filled', fillcolor='#FF6B6B', fontcolor='white', penwidth='2')
    
    # Define Dimension Tables
    
    # 1. Agent Dimension
    agent_attrs = [
        'PK: Agent_ID',
        'Agent_Age',
        'Agent_Rating',
        'Rating_Category'
    ]
    agent_label = f'{{Dim_Agent|{" | ".join(agent_attrs)}}}'
    dot.node('Agent', agent_label, shape='record', style='filled', fillcolor='#4ECDC4', penwidth='1.5')
    
    # 2. Time Dimension
    time_attrs = [
        'PK: Time_ID',
        'Order_Date',
        'Order_Year',
        'Order_Month',
        'Order_Day',
        'Order_Weekday',
        'Order_Quarter',
        'Order_Time_Category',
        'Season',
        'Is_Weekend'
    ]
    time_label = f'{{Dim_Time|{" | ".join(time_attrs)}}}'
    dot.node('Time', time_label, shape='record', style='filled', fillcolor='#45B7D1', penwidth='1.5')
    
    # 3. Location Dimension
    location_attrs = [
        'PK: Location_ID',
        'Store_Latitude',
        'Store_Longitude',
        'Drop_Latitude',
        'Drop_Longitude',
        'Area',
        'Distance_KM',
        'Distance_Category'
    ]
    location_label = f'{{Dim_Location|{" | ".join(location_attrs)}}}'
    dot.node('Location', location_label, shape='record', style='filled', fillcolor='#96CEB4', penwidth='1.5')
    
    # 4. Weather Dimension
    weather_attrs = [
        'PK: Weather_ID',
        'Weather',
        'Weather_Severity',
        'Delivery_Impact'
    ]
    weather_label = f'{{Dim_Weather|{" | ".join(weather_attrs)}}}'
    dot.node('Weather', weather_label, shape='record', style='filled', fillcolor='#FFEAA7', penwidth='1.5')
    
    # 5. Vehicle Dimension
    vehicle_attrs = [
        'PK: Vehicle_ID',
        'Vehicle',
        'Vehicle_Category',
        'Traffic',
        'Traffic_Impact'
    ]
    vehicle_label = f'{{Dim_Vehicle|{" | ".join(vehicle_attrs)}}}'
    dot.node('Vehicle', vehicle_label, shape='record', style='filled', fillcolor='#DDA0DD', penwidth='1.5')
    
    # 6. Category Dimension
    category_attrs = [
        'PK: Category_ID',
        'Category',
        'Product_Type',
        'Fragility_Level'
    ]
    category_label = f'{{Dim_Category|{" | ".join(category_attrs)}}}'
    dot.node('Category', category_label, shape='record', style='filled', fillcolor='#98D8C8', penwidth='1.5')
    
    # Define Relationships (Edges)
    # Fact to Dimension relationships
    edges = [
        ('Agent', 'Fact', '1:N'),
        ('Time', 'Fact', '1:N'),
        ('Location', 'Fact', '1:N'),
        ('Weather', 'Fact', '1:N'),
        ('Vehicle', 'Fact', '1:N'),
        ('Category', 'Fact', '1:N')
    ]
    
    # Add edges with labels
    for source, target, label in edges:
        dot.edge(source, target, label=label, fontsize='9', color='#555555', penwidth='1.5')
    
    # Add a legend/cluster for better visualization
    with dot.subgraph(name='cluster_legend') as c:
        c.attr(label='Legend', style='filled', color='lightblue', fontsize='12')
        c.node('legend_fact', 'Fact Table', shape='box', style='filled', fillcolor='#FF6B6B', fontcolor='white')
        c.node('legend_dim', 'Dimension', shape='box', style='filled', fillcolor='#4ECDC4')
        c.node('legend_rel', 'Relationship', shape='ellipse')
    
    # Render the diagram
    output_path = os.path.join(OUTPUT_DIR, 'erd_diagram')
    dot.render(output_path, cleanup=True)
    
    print(f"\n✓ ERD Diagram saved to: {output_path}.png")
    print(f"  - Nodes: 8 (1 Fact + 7 Dimensions)")
    print(f"  - Edges: {len(edges)} relationships")
    
    return dot

def generate_legend_table():
    """
    Generate a legend table for the ERD
    """
    print("\n" + "="*60)
    print("ERD LEGEND & ENTITY DESCRIPTIONS")
    print("="*60)
    
    legend = """
    ┌─────────────────────────────────────────────────────────────────────┐
    │                        ERD LEGEND                                   │
    ├─────────────────────────────────────────────────────────────────────┤
    │  SYMBOL          │ DESCRIPTION                                     │
    ├──────────────────┼─────────────────────────────────────────────────┤
    │  [Red Box]       │ Fact Table (contains measurements/metrics)      │
    │  [Green Box]     │ Dimension Table (descriptive attributes)        │
    │  --> (Arrow)     │ Relationship (Foreign Key to Primary Key)       │
    │  1:N             │ One-to-Many relationship cardinality              │
    └─────────────────────────────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │                     ENTITY DESCRIPTIONS                             │
    ├─────────────────────────────────────────────────────────────────────┤
    │ FACT TABLE: Fact_Deliveries                                         │
    │   - Central fact table containing delivery metrics                   │
    │   - Grain: One row per delivery/order                              │
    │   - Measures: Delivery_Time, Distance_KM, Speed_KM_H, etc.         │
    │                                                                      │
    │ DIMENSIONS:                                                          │
    │   1. Dim_Agent      - Delivery agent details and ratings            │
    │   2. Dim_Time       - Date/time hierarchy (year, month, day, etc.)  │
    │   3. Dim_Location   - Geographic locations and distance metrics     │
    │   4. Dim_Weather    - Weather conditions and impact levels          │
    │   5. Dim_Vehicle    - Vehicle types and traffic conditions          │
    │   6. Dim_Category   - Product categories and types                  │
    └─────────────────────────────────────────────────────────────────────┘
    """
    print(legend)
    
    # Save legend to file
    legend_file = os.path.join(OUTPUT_DIR, 'erd_legend.txt')
    with open(legend_file, 'w') as f:
        f.write(legend)
    print(f"\n✓ ERD Legend saved to: {legend_file}")

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*12 + "ERD DIAGRAM GENERATOR" + " "*25 + "║")
    print("║" + " "*8 + "Amazon Delivery Data Warehouse" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")
    
    # Generate ERD
    erd = create_erd()
    
    # Generate Legend
    generate_legend_table()
    
    print("\n" + "="*60)
    print("ALL DIAGRAMS GENERATED SUCCESSFULLY!")
    print("="*60)
    print(f"Output directory: {OUTPUT_DIR}/")
    print("  - erd_diagram.png")
    print("  - erd_legend.txt")
