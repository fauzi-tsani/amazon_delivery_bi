"""
Star Schema Visualization for Amazon Delivery Data Warehouse
=============================================================
This script generates a visual representation of the Star Schema
with the Fact table at the center and Dimension tables surrounding it.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

OUTPUT_DIR = 'diagrams'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_star_schema():
    """
    Create a visual Star Schema diagram
    """
    print("="*60)
    print("STAR SCHEMA DIAGRAM GENERATION")
    print("="*60)
    
    # Create figure with white background
    fig, ax = plt.subplots(1, 1, figsize=(16, 14), facecolor='white')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    ax.text(50, 97, 'STAR SCHEMA - Amazon Delivery Data Warehouse', 
            fontsize=18, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#2C3E50', edgecolor='none'),
            color='white')
    
    # Define positions (Star pattern - Fact in center)
    fact_pos = (50, 50)
    dim_positions = {
        'Dim_Agent': (50, 85),          # Top
        'Dim_Time': (85, 65),           # Top-Right
        'Dim_Location': (85, 35),      # Bottom-Right
        'Dim_Weather': (50, 15),       # Bottom
        'Dim_Vehicle': (15, 35),       # Bottom-Left
        'Dim_Category': (15, 65)       # Top-Left
    }
    
    # Fact Table Properties
    fact_name = 'Fact_Deliveries'
    fact_measures = [
        '• Delivery_Fact_ID (PK)',
        '• Agent_ID (FK)',
        '• Time_ID (FK)',
        '• Location_ID (FK)',
        '• Weather_ID (FK)',
        '• Vehicle_ID (FK)',
        '• Category_ID (FK)',
        '• Distance_KM',
        '• Delivery_Time (min)',
        '• Speed_KM_H',
        '• Pickup_Delay_Min',
        '• Performance_Category'
    ]
    
    # Draw Fact Table (Center)
    draw_dimension_box(ax, fact_pos[0], fact_pos[1], 28, 30, fact_name, fact_measures, 
                      facecolor='#E74C3C', text_color='white')
    
    # Dimension Tables Content
    dims_content = {
        'Dim_Agent': [
            '• Agent_ID (PK)',
            '• Agent_Age',
            '• Agent_Rating',
            '• Rating_Category'
        ],
        'Dim_Time': [
            '• Time_ID (PK)',
            '• Order_Date',
            '• Year/Month/Day',
            '• Quarter',
            '• Weekday/Weekend',
            '• Time_Category',
            '• Season'
        ],
        'Dim_Location': [
            '• Location_ID (PK)',
            '• Store_Lat/Lon',
            '• Drop_Lat/Lon',
            '• Area',
            '• Distance_KM',
            '• Distance_Category'
        ],
        'Dim_Weather': [
            '• Weather_ID (PK)',
            '• Weather',
            '• Weather_Severity',
            '• Delivery_Impact'
        ],
        'Dim_Vehicle': [
            '• Vehicle_ID (PK)',
            '• Vehicle_Type',
            '• Vehicle_Category',
            '• Traffic',
            '• Traffic_Impact'
        ],
        'Dim_Category': [
            '• Category_ID (PK)',
            '• Category',
            '• Product_Type',
            '• Fragility_Level'
        ]
    }
    
    # Dimension colors
    dim_colors = ['#3498DB', '#2ECC71', '#9B59B6', '#F39C12', '#1ABC9C', '#E67E22']
    
    # Draw Dimension Tables
    for i, (dim_name, content) in enumerate(dims_content.items()):
        pos = dim_positions[dim_name]
        color = dim_colors[i % len(dim_colors)]
        
        draw_dimension_box(ax, pos[0], pos[1], 20, 22, dim_name, content,
                          facecolor=color, text_color='white')
        
        # Draw connection lines to fact table
        draw_connection_line(ax, pos[0], pos[1], fact_pos[0], fact_pos[1], color)
    
    # Add Star Schema Description
    description_text = (
        "Schema Type: STAR SCHEMA\n"
        "• Central Fact Table surrounded by Dimension Tables\n"
        "• No snowflaking - dimensions are denormalized\n"
        "• Optimized for query performance\n"
        "• Single-level hierarchy in dimensions"
    )
    
    ax.text(50, 3, description_text, fontsize=9, ha='center', va='bottom',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#ECF0F1', edgecolor='#7F8C8D', linewidth=2),
           family='monospace')
    
    # Save diagram
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'star_schema.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"\n✓ Star Schema diagram saved to: {output_path}")
    
    # Also create a summary text file
    summary_path = os.path.join(OUTPUT_DIR, 'star_schema_summary.txt')
    with open(summary_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write("STAR SCHEMA SUMMARY\n")
        f.write("="*60 + "\n\n")
        f.write("CENTRAL FACT TABLE:\n")
        f.write("-" * 40 + "\n")
        f.write("Table: Fact_Deliveries\n")
        f.write("Grain: One row per delivery transaction\n")
        f.write("Measures:\n")
        for m in fact_measures[7:]:
            f.write(f"  {m}\n")
        
        f.write("\n\nDIMENSION TABLES:\n")
        f.write("-" * 40 + "\n")
        
        dim_info = [
            ("Dim_Agent", "Agent attributes and ratings", 4),
            ("Dim_Time", "Date and time hierarchy", 10),
            ("Dim_Location", "Geographic locations", 8),
            ("Dim_Weather", "Weather conditions", 4),
            ("Dim_Vehicle", "Vehicle and traffic info", 5),
            ("Dim_Category", "Product categories", 4)
        ]
        
        for name, desc, attrs in dim_info:
            f.write(f"\n{name}:\n")
            f.write(f"  Description: {desc}\n")
            f.write(f"  Attributes: {attrs}\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("SCHEMA CHARACTERISTICS:\n")
        f.write("="*60 + "\n")
        f.write("Type: Star Schema (Denormalized)\n")
        f.write("Dimensions: 6 (directly connected to fact)\n")
        f.write("Relationships: All 1-to-Many (1:N)\n")
        f.write("Optimization: Query performance focused\n")
    
    print(f"✓ Schema summary saved to: {summary_path}")
    
    return output_path

def draw_dimension_box(ax, x, y, width, height, title, attributes, facecolor='#3498DB', text_color='white'):
    """
    Draw a dimension box with title and attributes
    """
    # Draw main box
    rect = FancyBboxPatch((x - width/2, y - height/2), width, height,
                          boxstyle="round,pad=0.05,rounding_size=0.5",
                          facecolor=facecolor, edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    
    # Draw title section
    title_height = height * 0.2
    title_rect = FancyBboxPatch((x - width/2, y + height/2 - title_height), width, title_height,
                               boxstyle="round,pad=0.02,rounding_size=0.3",
                               facecolor='black', edgecolor='black', linewidth=1, alpha=0.3)
    ax.add_patch(title_rect)
    
    # Add title text
    ax.text(x, y + height/2 - title_height/2, title, fontsize=10, fontweight='bold',
           ha='center', va='center', color=text_color)
    
    # Add attributes
    attr_text = '\n'.join(attributes[:8])  # Limit to 8 attributes
    ax.text(x, y - height/2 + height*0.15, attr_text, fontsize=7,
           ha='center', va='bottom', color=text_color, linespacing=1.2)

def draw_connection_line(ax, x1, y1, x2, y2, color='#555555'):
    """
    Draw a connection line between two points with arrow
    """
    # Calculate direction
    dx = x2 - x1
    dy = y2 - y1
    dist = np.sqrt(dx**2 + dy**2)
    
    # Normalize and scale to start/end at box edges
    offset_x = (dx / dist) * 10  # Offset from center
    offset_y = (dy / dist) * 10
    
    # Adjust start and end points
    start_x = x1 + offset_x
    start_y = y1 + offset_y
    end_x = x2 - offset_x
    end_y = y2 - offset_y
    
    # Draw line with arrow
    arrow = FancyArrowPatch((start_x, start_y), (end_x, end_y),
                           arrowstyle='-|>', color=color, linewidth=2,
                           mutation_scale=15, alpha=0.7)
    ax.add_patch(arrow)
    
    # Add relationship label (1:N) at midpoint
    mid_x = (start_x + end_x) / 2
    mid_y = (start_y + end_y) / 2
    ax.text(mid_x, mid_y + 2, '1:N', fontsize=7, ha='center', va='bottom',
           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=color, alpha=0.9),
           fontweight='bold')

def main():
    """
    Main function to generate Star Schema diagram
    """
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*14 + "STAR SCHEMA GENERATOR" + " "*23 + "║")
    print("║" + " "*10 + "Amazon Delivery Data Warehouse" + " "*18 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")
    
    # Generate the Star Schema diagram
    output_path = create_star_schema()
    
    print("\n" + "="*60)
    print("STAR SCHEMA GENERATION COMPLETE!")
    print("="*60)
    
    return output_path

if __name__ == "__main__":
    main()
