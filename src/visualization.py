"""
Visualization Module
Functions for visualizing air quality data
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import ee

logger = logging.getLogger(__name__)


class AirQualityVisualizer:
    """Visualize air quality data on maps"""
    
    def __init__(self):
        """Initialize visualizer with default colormaps"""
        self.colormaps = self._setup_colormaps()
    
    def _setup_colormaps(self):
        """Setup custom colormaps for different pollutants"""
        return {
            'no2': LinearSegmentedColormap.from_list(
                'no2', ['black', 'blue', 'purple', 'red']
            ),
            'co': LinearSegmentedColormap.from_list(
                'co', ['black', 'green', 'yellow', 'red']
            ),
            'aod': LinearSegmentedColormap.from_list(
                'aod', ['white', 'yellow', 'orange', 'red']
            )
        }
    
    def get_map_visualization_params(self, pollutant):
        """
        Get visualization parameters for map display
        
        Args:
            pollutant: Type of pollutant ('no2', 'co', 'aod')
        
        Returns:
            dict: Visualization parameters
        """
        params = {
            'no2': {
                'min': 0,
                'max': 2e16,
                'palette': ['black', 'blue', 'purple', 'red']
            },
            'co': {
                'min': 0,
                'max': 2e18,
                'palette': ['black', 'green', 'yellow', 'red']
            },
            'aod': {
                'min': 0,
                'max': 0.5,
                'palette': ['white', 'yellow', 'orange', 'red']
            }
        }
        return params.get(pollutant, {})
    
    def plot_timeseries(self, timeseries_data, title="Air Quality Time Series", 
                       ylabel="Concentration", save_path=None):
        """
        Plot air quality time series
        
        Args:
            timeseries_data: Time series data with dates
            title: Plot title
            ylabel: Y-axis label
            save_path: Path to save figure (if None, displays plot)
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot data
        ax.plot(timeseries_data['date'], timeseries_data['value'], 
                linewidth=2, marker='o', markersize=4)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot to {save_path}")
        else:
            plt.show()
        
        return fig
    
    def plot_comparison(self, data_dict, title="Air Quality Comparison", 
                       save_path=None):
        """
        Plot multiple air quality metrics for comparison
        
        Args:
            data_dict: Dictionary with {metric_name: data}
            title: Plot title
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(len(data_dict), 1, figsize=(12, 4*len(data_dict)))
        
        if len(data_dict) == 1:
            axes = [axes]
        
        for ax, (label, data) in zip(axes, data_dict.items()):
            ax.plot(data['date'], data['value'], linewidth=2, marker='o')
            ax.set_ylabel(label, fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.set_title(label, fontweight='bold')
        
        axes[-1].set_xlabel('Date', fontsize=12)
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved comparison plot to {save_path}")
        else:
            plt.show()
        
        return fig


def initialize_visualizer():
    """Initialize visualization module"""
    return AirQualityVisualizer()
