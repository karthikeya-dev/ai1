import streamlit as st
import pandas as pd
from helpers.json_handler import load_json
from components.charts import render_pie_chart, render_line_chart, render_bar_chart, render_area_chart
from modules.utils import load_css, styled_header

def show_analytics():
    """Renders comprehensive campus-wide analytics and graphical views using Plotly."""
    load_css()
    
    if "user" not in st.session_state or not st.session_state.user:
        st.error("Authentication required!")
        return
        
    styled_header("Analytics & Insights", "Deep-dive graphical summaries of campus operations", "analytics")
    
    # Fetch DB files
    students = load_json("students.json")
    placements = load_json("placements.json")
    attendance = load_json("attendance.json")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Student Demographics", "Academic Attendance Trends", "Placement Cell Metrics"])
    
    # ------------------ Tab 1: Student Demographics ------------------
    with tab1:
        st.markdown("### Class strength distribution reports")
        if not students:
            st.info("No student data to display.", icon=":material/database:")
        else:
            df_stu = pd.DataFrame(students)
            
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                # Year-wise Counts
                df_year = df_stu["year"].value_counts().reset_index()
                df_year.columns = ["Year", "Count"]
                fig_year = render_pie_chart(df_year, "Year", "Count", "Students by Academic Year")
                st.plotly_chart(fig_year, width="stretch")
                
            with col_g2:
                # Branch and Section distribution
                df_br_sec = df_stu.groupby(["branch", "section"]).size().reset_index(name="Count")
                fig_br_sec = render_bar_chart(
                    df_br_sec, 
                    x_col="branch", 
                    y_col="Count", 
                    title="Branch & Section Strength Details",
                    x_title="Academic Branch", 
                    y_title="Student Count",
                    color_col="section"
                )
                st.plotly_chart(fig_br_sec, width="stretch")
                
    # ------------------ Tab 2: Attendance Trends ------------------
    with tab2:
        st.markdown("### Campus-wide attendance timeline trends")
        if not attendance:
            st.info("No attendance logs to analyze.", icon=":material/database:")
        else:
            df_att = pd.DataFrame(attendance)
            
            # Group by date and calculate attendance rate
            date_stats = []
            for date_val, group in df_att.groupby("date"):
                total = len(group)
                present_late = len(group[group["status"].isin(["Present", "Late"])])
                rate = (present_late / total) * 100 if total > 0 else 0
                date_stats.append({"Date": date_val, "Attendance Rate (%)": round(rate, 1)})
                
            df_timeline = pd.DataFrame(date_stats).sort_values(by="Date")
            
            if not df_timeline.empty:
                col_timeline = st.columns(1)[0]
                with col_timeline:
                    fig_time = render_line_chart(
                        df_timeline, 
                        x_col="Date", 
                        y_col="Attendance Rate (%)", 
                        title="Daily Attendance Average Trend (%)",
                        x_title="Date", 
                        y_title="Attendance Rate (%)"
                    )
                    st.plotly_chart(fig_time, width="stretch")
            else:
                st.info("Insufficient timeline records.")
                
    # ------------------ Tab 3: Placement Cell Metrics ------------------
    with tab3:
        st.markdown("### Placements Performance Reports")
        if not placements:
            st.info("No placement data available.", icon=":material/database:")
        else:
            df_place = pd.DataFrame(placements)
            
            # Clean package column to get numeric values for chart sorting
            # Package expected format: "32 LPA" -> 32.0
            def clean_package(val):
                try:
                    num_str = "".join([c for c in val if c.isdigit() or c == "."])
                    return float(num_str) if num_str else 0.0
                except Exception:
                    return 0.0
                    
            df_place["Package (Numeric)"] = df_place["package"].apply(clean_package)
            
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                # Salary bar chart
                df_sorted_salary = df_place.sort_values(by="Package (Numeric)", ascending=False)
                fig_sal = render_bar_chart(
                    df_sorted_salary, 
                    x_col="company_name", 
                    y_col="Package (Numeric)", 
                    title="Compensation Package Offered (LPA)",
                    x_title="Recruiting Firm", 
                    y_title="Package (LPA)"
                )
                st.plotly_chart(fig_sal, width="stretch")
                
            with col_p2:
                # Applicants vs Selections
                df_place["Applied Count"] = df_place["applied_students"].apply(lambda x: len(x) if isinstance(x, list) else 0)
                df_place["Hired Count"] = df_place["selected_students"].apply(lambda x: len(x) if isinstance(x, list) else 0)
                
                # Reshape for grouped bar chart
                melt_df = pd.melt(
                    df_place, 
                    id_vars=["company_name"], 
                    value_vars=["Applied Count", "Hired Count"], 
                    var_name="Category", 
                    value_name="Students"
                )
                
                import plotly.express as px
                mode = "dark"
                try:
                    mode = st.context.theme.type
                except Exception:
                    pass
                t_color = "#f3f4f6" if mode == "dark" else "#0f172a"
                
                fig_conversion = px.bar(
                    melt_df, 
                    x="company_name", 
                    y="Students", 
                    color="Category", 
                    barmode="group",
                    color_discrete_map={"Applied Count": "#3b82f6", "Hired Count": "#10b981"}
                )
                fig_conversion.update_layout(
                    title={
                        'text': "Applicant Conversion Analysis",
                        'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top',
                        'font': {'size': 16, 'family': 'Inter, sans-serif', 'weight': 'bold', 'color': t_color}
                    },
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=t_color),
                    margin=dict(l=40, r=20, t=50, b=40)
                )
                st.plotly_chart(fig_conversion, width="stretch")
