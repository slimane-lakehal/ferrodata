"""Reusable chart and visualization utilities."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_time_series_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str = None,
    title: str = None,
    y_label: str = None
):
    """
    Create a time series line chart.

    Args:
        data: DataFrame with time series data
        x_col: Column name for x-axis (date)
        y_col: Column name for y-axis (metric)
        color_col: Optional column for color grouping
        title: Chart title
        y_label: Y-axis label

    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        labels={y_col: y_label or y_col}
    )

    fig.update_layout(
        hovermode='x unified',
        xaxis_title="Date",
        template="plotly_white"
    )

    return fig


def create_performance_gauge(value: float, title: str, thresholds: dict = None):
    """
    Create a gauge chart for performance metrics.

    Args:
        value: The metric value (0-100)
        title: Chart title
        thresholds: Dict with 'excellent', 'good', 'fair' thresholds

    Returns:
        plotly.graph_objects.Figure
    """
    if thresholds is None:
        thresholds = {'excellent': 95, 'good': 90, 'fair': 80}

    # Determine color based on value
    if value >= thresholds['excellent']:
        color = "green"
    elif value >= thresholds['good']:
        color = "lightgreen"
    elif value >= thresholds['fair']:
        color = "orange"
    else:
        color = "red"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, thresholds['fair']], 'color': "lightgray"},
                {'range': [thresholds['fair'], thresholds['good']], 'color': "lightyellow"},
                {'range': [thresholds['good'], 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': thresholds['excellent']
            }
        }
    ))

    fig.update_layout(height=250)

    return fig


def create_bar_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str = None,
    title: str = None,
    orientation: str = 'v'
):
    """
    Create a bar chart.

    Args:
        data: DataFrame
        x_col: X-axis column
        y_col: Y-axis column
        color_col: Optional color grouping column
        title: Chart title
        orientation: 'v' for vertical, 'h' for horizontal

    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        orientation=orientation
    )

    fig.update_layout(template="plotly_white")

    return fig


def create_sunburst_chart(
    data: pd.DataFrame,
    path_cols: list,
    values_col: str,
    title: str = None
):
    """
    Create a sunburst chart for hierarchical data.

    Args:
        data: DataFrame
        path_cols: List of columns defining hierarchy
        values_col: Column with values
        title: Chart title

    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.sunburst(
        data,
        path=path_cols,
        values=values_col,
        title=title
    )

    fig.update_layout(template="plotly_white")

    return fig


def create_scatter_map(
    data: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    size_col: str = None,
    color_col: str = None,
    hover_name: str = None,
    title: str = None
):
    """
    Create a scatter map.

    Args:
        data: DataFrame with location data
        lat_col: Latitude column
        lon_col: Longitude column
        size_col: Optional column for marker size
        color_col: Optional column for marker color
        hover_name: Column to show on hover
        title: Map title

    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.scatter_mapbox(
        data,
        lat=lat_col,
        lon=lon_col,
        size=size_col,
        color=color_col,
        hover_name=hover_name,
        title=title,
        mapbox_style="open-street-map",
        zoom=5,
        center={"lat": 46.5, "lon": 2.5}  # Center on France
    )

    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 30, "l": 0, "b": 0}
    )

    return fig
