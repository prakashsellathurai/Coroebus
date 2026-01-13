from shiny import App, ui, render, reactive
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from shinywidgets import output_widget, render_widget

# Load data
csv_path = Path(__file__).parent / "daily_load.csv"
df_load = pd.read_csv(csv_path)
df_load["date"] = pd.to_datetime(df_load["date"])

app_ui = ui.page_fluid(
    ui.panel_title("Fatigue, Fitness & Training Load Trends"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.markdown("""
            **Metrics Guide:**
            - **Fitness (CTL):** Chronic Training Load (Long-term)
            - **Fatigue (ATL):** Acute Training Load (Short-term)
            - **Form (TSB):** Fitness - Fatigue (Readiness)
            """),
            ui.input_slider("ctl_tc", "Fitness (CTL) Days", 7, 100, 42),
            ui.input_slider("atl_tc", "Fatigue (ATL) Days", 1, 30, 7),
        ),
        
        output_widget("plot"),
    )
)

def server(input, output, session):
    
    @reactive.Calc
    def calculate_trends():
        df = df_load.copy()
        
        # Banister Model: 
        # CTL_now = CTL_prev * e^(-1/CTL_tc) + Load * (1 - e^(-1/CTL_tc))
        
        ctl_tc = input.ctl_tc()
        atl_tc = input.atl_tc()
        
        ctl = [0.0]
        atl = [0.0]
        
        alpha_ctl = np.exp(-1.0 / ctl_tc)
        alpha_atl = np.exp(-1.0 / atl_tc)
        
        loads = df["load"].values
        
        for i in range(len(loads)):
            ctl.append(ctl[i] * alpha_ctl + loads[i] * (1 - alpha_ctl))
            atl.append(atl[i] * alpha_atl + loads[i] * (1 - alpha_atl))
            
        df["ctl"] = ctl[1:]
        df["atl"] = atl[1:]
        df["tsb"] = df["ctl"] - df["atl"]
        
        return df

    @render_widget
    def plot():
        df = calculate_trends()
        
        fig = go.Figure()
        
        # Load as bars
        fig.add_trace(go.Bar(
            x=df["date"], y=df["load"], 
            name="Daily Load", 
            marker_color="rgba(100, 100, 100, 0.3)",
            yaxis="y2"
        ))
        
        # Fitness (CTL)
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["ctl"], 
            name="Fitness (CTL)", 
            line=dict(color="#2ecc71", width=3)
        ))
        
        # Fatigue (ATL)
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["atl"], 
            name="Fatigue (ATL)", 
            line=dict(color="#e74c3c", width=2, dash="dot")
        ))
        
        # Form (TSB)
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["tsb"], 
            name="Form (TSB)", 
            fill='tozeroy',
            line=dict(color="#3498db", width=1)
        ))

        # Add Training Zones
        # High Risk: Below -30
        fig.add_hrect(y0=-100, y1=-30, fillcolor="rgba(231, 76, 60, 0.1)", line_width=0, layer="below", annotation_text="High Risk", annotation_position="left")
        # Optimal: -30 to -10
        fig.add_hrect(y0=-30, y1=-10, fillcolor="rgba(46, 204, 113, 0.1)", line_width=0, layer="below", annotation_text="Optimal", annotation_position="left")
        # Others/Neutral/Overload: Above -10
        fig.add_hrect(y0=-10, y1=100, fillcolor="rgba(149, 165, 166, 0.1)", line_width=0, layer="below", annotation_text="Other", annotation_position="left")
        
        fig.update_layout(
            template="plotly_white",
            height=600,
            xaxis_title="Date",
            yaxis_title="Load / Stress Metrics",
            yaxis2=dict(
                title="Daily Load",
                overlaying="y",
                side="right"
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified"
        )
        
        return fig

app = App(app_ui, server)
