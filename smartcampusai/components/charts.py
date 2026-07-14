import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def _get_theme_mode() -> str:
    """Safely check the current active theme mode (dark or light)."""
    try:
        return st.context.theme.type
    except Exception:
        return "dark"

def _apply_common_layout(fig, title: str):
    """Applies common visual styling parameters to align Plotly charts with the application UI."""
    mode = _get_theme_mode()
    text_color = "#f3f4f6" if mode == "dark" else "#0f172a"
    grid_color = "rgba(255, 255, 255, 0.08)" if mode == "dark" else "rgba(15, 23, 42, 0.08)"
    
    fig.update_layout(
        title={
            'text': title,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16, 'family': 'Inter, sans-serif', 'weight': 'bold', 'color': text_color}
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            size=11,
            color=text_color
        ),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            tickfont=dict(color=text_color),
            title=dict(font=dict(color=text_color))
        ),
        yaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            tickfont=dict(color=text_color),
            title=dict(font=dict(color=text_color))
        ),
        legend=dict(
            font=dict(color=text_color)
        )
    )
    return fig

def render_pie_chart(df: pd.DataFrame, names_col: str, values_col: str, title: str):
    """Generates a professional donut pie chart."""
    colors = ["#00f0ff", "#10b981", "#8b5cf6", "#f43f5e", "#f59e0b", "#3b82f6", "#9ca3af"]
    fig = px.pie(
        df, 
        names=names_col, 
        values=values_col, 
        hole=0.4, 
        color_discrete_sequence=colors
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return _apply_common_layout(fig, title)

def render_line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, x_title: str = "", y_title: str = ""):
    """Generates a sleek, smooth line chart with gradient trace effects."""
    fig = px.line(
        df, 
        x=x_col, 
        y=y_col, 
        color_discrete_sequence=["#00f0ff"]
    )
    fig.update_traces(line=dict(width=3, shape="spline"))
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title)
    return _apply_common_layout(fig, title)

def render_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, x_title: str = "", y_title: str = "", color_col: str = None):
    """Generates a customizable vertical bar chart."""
    colors = ["#00f0ff"] if not color_col else None
    fig = px.bar(
        df, 
        x=x_col, 
        y=y_col, 
        color=color_col,
        color_discrete_sequence=colors if not color_col else px.colors.qualitative.Pastel
    )
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title)
    return _apply_common_layout(fig, title)

def render_area_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, x_title: str = "", y_title: str = ""):
    """Generates a soft gradient-shaded area chart."""
    fig = px.area(
        df, 
        x=x_col, 
        y=y_col, 
        color_discrete_sequence=["#8b5cf6"]
    )
    fig.update_traces(line=dict(width=2, shape="spline"))
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title)
    return _apply_common_layout(fig, title)
