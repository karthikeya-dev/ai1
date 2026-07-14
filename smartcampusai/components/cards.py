import streamlit as st

def render_kpi_card(title: str, value: str, delta: str = None, icon: str = None, color: str = "#00f0ff"):
    """
    Renders a premium glassmorphic KPI card with an icon, main value, and delta.
    Designed to fit inside Streamlit columns.
    """
    delta_html = ""
    if delta:
        if delta.startswith("+"):
            delta_html = f"<div style='color: #10b981; font-size: 0.8rem; font-weight: 600; margin-top: 4px;'>:material/arrow_upward: {delta} vs last month</div>"
        elif delta.startswith("-"):
            delta_html = f"<div style='color: #f43f5e; font-size: 0.8rem; font-weight: 600; margin-top: 4px;'>:material/arrow_downward: {delta} vs last month</div>"
        else:
            delta_html = f"<div style='color: #f59e0b; font-size: 0.8rem; font-weight: 600; margin-top: 4px;'>{delta}</div>"
            
    icon_html = ""
    if icon:
        icon_html = f"""
        <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); 
                    border-radius: 8px; width: 44px; height: 44px; display: flex; 
                    align-items: center; justify-content: center; font-size: 1.5rem; color: {color};'>
            :material/{icon}:
        </div>
        """
        
    st.markdown(
        f"""
        <div class="glass-card" style="margin-bottom: 12px; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
                <div style="flex-grow: 1;">
                    <div style="font-size: 0.75rem; opacity: 0.7; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                        {title}
                    </div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: var(--text-color); margin-bottom: 2px;">
                        {value}
                    </div>
                    {delta_html}
                </div>
                {icon_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
