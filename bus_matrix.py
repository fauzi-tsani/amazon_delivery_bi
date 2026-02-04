"""
Enterprise Bus Matrix Generator
================================
Generates Enterprise Bus Matrix showing the relationship
between Business Processes and Conformed Dimensions.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np
import os

OUTPUT_DIR = 'diagrams'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_enterprise_bus_matrix():
    """
    Create Enterprise Bus Matrix visualization
    """
    print("="*60)
    print("ENTERPRISE BUS MATRIX GENERATION")
    print("="*60)
    
    # Define Business Processes (Rows)
    business_processes = [
        'P1: Order Processing',
        'P2: Delivery Execution',
        'P3: Agent Performance',
        'P4: Route Optimization',
        'P5: Customer Satisfaction',
        'P6: Weather Impact Analysis',
        'P7: Traffic Pattern Analysis',
        'P8: Product Category Performance'
    ]
    
    # Define Conformed Dimensions (Columns)
    dimensions = [
        'Dim_Agent',
        'Dim_Time',
        'Dim_Location',
        'Dim_Weather',
        'Dim_Vehicle',
        'Dim_Category'
    ]
    
    # Create Matrix (X = used, empty = not used)
    # Rows: Business Processes
    # Columns: Dimensions
    matrix_data = [
        ['X', 'X', 'X', ' ', ' ', 'X'],  # P1: Order Processing
        ['X', 'X', 'X', 'X', 'X', 'X'],  # P2: Delivery Execution
        ['X', 'X', ' ', ' ', 'X', ' '],  # P3: Agent Performance
        [' ', 'X', 'X', 'X', 'X', ' '],  # P4: Route Optimization
        ['X', 'X', 'X', ' ', ' ', 'X'],  # P5: Customer Satisfaction
        [' ', 'X', 'X', 'X', ' ', ' '],  # P6: Weather Impact Analysis
        ['X', 'X', 'X', ' ', 'X', ' '],  # P7: Traffic Pattern Analysis
        [' ', 'X', ' ', ' ', ' ', 'X'],  # P8: Product Category Performance
    ]
    
    print(f"\nMatrix Dimensions:")
    print(f"  - Business Processes: {len(business_processes)}")
    print(f"  - Conformed Dimensions: {len(dimensions)}")
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')
    ax.set_facecolor('white')
    
    # Title
    ax.text(0.5, 0.98, 'ENTERPRISE BUS MATRIX', 
           transform=ax.transAxes, fontsize=20, fontweight='bold',
           ha='center', va='top',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='#2C3E50', edgecolor='none'),
           color='white')
    
    ax.text(0.5, 0.93, 'Mapping Business Processes to Conformed Dimensions',
           transform=ax.transAxes, fontsize=12, ha='center', va='top',
           style='italic', color='#555555')
    
    # Table configuration
    n_rows = len(business_processes) + 1  # +1 for header
    n_cols = len(dimensions) + 1  # +1 for row labels
    
    cell_height = 0.08
    cell_width = 0.12
    start_y = 0.85
    start_x = 0.08
    
    # Color scheme
    header_color = '#34495E'
    row_label_color = '#5D6D7E'
    x_mark_color = '#27AE60'
    empty_cell_color = '#F8F9F9'
    border_color = '#2C3E50'
    
    # Draw column headers (Dimension names)
    for j, dim in enumerate(dimensions):
        x = start_x + (j + 1) * cell_width
        y = start_y
        
        rect = plt.Rectangle((x, y - cell_height), cell_width, cell_height,
                            facecolor=header_color, edgecolor=border_color, linewidth=2)
        ax.add_patch(rect)
        
        # Split dimension name for display
        parts = dim.split('_')
        ax.text(x + cell_width/2, y - cell_height/2, parts[1] if len(parts) > 1 else dim,
               ha='center', va='center', fontsize=9, fontweight='bold', color='white',
               rotation=0)
    
    # Draw row labels and matrix cells
    for i, process in enumerate(business_processes):
        y = start_y - (i + 1) * cell_height
        
        # Row label (Business Process)
        x = start_x
        rect = plt.Rectangle((x, y), cell_width * 1.2, cell_height,
                            facecolor=row_label_color, edgecolor=border_color, linewidth=2)
        ax.add_patch(rect)
        
        # Truncate process name if too long
        display_text = process[:25] + '...' if len(process) > 25 else process
        ax.text(x + cell_width * 0.6, y + cell_height/2, display_text,
               ha='center', va='center', fontsize=7, color='white', fontweight='bold')
        
        # Matrix cells (X marks)
        for j, dim in enumerate(dimensions):
            x = start_x + cell_width * 1.2 + j * cell_width
            
            # Determine cell value
            cell_value = matrix_data[i][j]
            
            # Set color based on value
            if cell_value == 'X':
                bg_color = x_mark_color
                text_color = 'white'
            else:
                bg_color = empty_cell_color
                text_color = '#CCCCCC'
            
            rect = plt.Rectangle((x, y), cell_width, cell_height,
                                facecolor=bg_color, edgecolor=border_color, linewidth=1)
            ax.add_patch(rect)
            
            # Draw X or leave empty
            if cell_value == 'X':
                ax.text(x + cell_width/2, y + cell_height/2, '✓',
                       ha='center', va='center', fontsize=14, color=text_color, fontweight='bold')
    
    # Add Legend
    legend_y = 0.05
    legend_elements = [
        mpatches.Patch(facecolor=x_mark_color, edgecolor=border_color, label='Dimension Used in Process'),
        mpatches.Patch(facecolor=empty_cell_color, edgecolor=border_color, label='Not Used')
    ]
    ax.legend(handles=legend_elements, loc='lower center', 
             bbox_to_anchor=(0.5, legend_y), ncol=2, fontsize=10,
             frameon=True, fancybox=True, shadow=True)
    
    # Add footer with statistics
    total_cells = len(business_processes) * len(dimensions)
    used_cells = sum(row.count('X') for row in matrix_data)
    usage_rate = (used_cells / total_cells) * 100
    
    footer_text = f"Total Business Processes: {len(business_processes)} | " \
                 f"Conformed Dimensions: {len(dimensions)} | " \
                 f"Dimension Usage Rate: {usage_rate:.1f}%"
    
    ax.text(0.5, 0.01, footer_text, transform=ax.transAxes, fontsize=9,
           ha='center', va='bottom', style='italic', color='#666666')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # Save the diagram
    output_path = os.path.join(OUTPUT_DIR, 'enterprise_bus_matrix.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"\n✓ Enterprise Bus Matrix saved to: {output_path}")
    print(f"  - Business Processes: {len(business_processes)}")
    print(f"  - Conformed Dimensions: {len(dimensions)}")
    print(f"  - Usage Rate: {usage_rate:.1f}%")
    
    return output_path

def main():
    """
    Main function to generate Enterprise Bus Matrix
    """
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*12 + "ENTERPRISE BUS MATRIX GENERATOR" + " "*15 + "║")
    print("║" + " "*10 + "Amazon Delivery Data Warehouse" + " "*18 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")
    
    output_path = create_enterprise_bus_matrix()
    
    print("\n" + "="*60)
    print("ENTERPRISE BUS MATRIX GENERATION COMPLETE!")
    print("="*60)
    
    return output_path

if __name__ == "__main__":
    main()
