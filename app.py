from shiny import App, ui, render, reactive
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import plotly.express as px
from shinywidgets import output_widget, render_widget
from performance import calculate_predictions, get_race_pace_history, get_pace_string

# Load data
csv_path = Path(__file__).parent / "daily_load.csv"
df_load = pd.read_csv(csv_path)
df_load["date"] = pd.to_datetime(df_load["date"])

app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.style("""
            body { background-color: #f8f9fa; font-family: 'Inter', -apple-system, sans-serif; }
            .sidebar { background-color: white !important; border-right: 1px solid #e0e0e0 !important; }
            .panel-title { font-weight: 700; color: #333; margin-bottom: 20px; }
            .card { border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        """)
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.div(
                {"class": "card p-3 mb-3"},
                ui.output_ui("latest_values"),
                
            ),
             
                 ui.output_ui("performance_metrics"),
            
           
            ui.markdown("""
            **Metrics Guide:**
            - **Fitness (CTL):** Chronic Training Load
            - **Fatigue (ATL):** Acute Training Load
            - **Form (TSB):** Fitness - Fatigue
            """),
            position="right",
            width=300
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
        
        ctl_tc = 42  # Fitness (CTL) Days
        atl_tc = 7   # Fatigue (ATL) Days
        
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
        
        # 7-day Ramp Rate: CTL(t) - CTL(t-7)
        df["ramp"] = df["ctl"].diff(7).fillna(0)
        
        return df

    @render_widget
    def plot():
        df = calculate_trends()
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.08,
            subplot_titles=("Daily Training Load", "Form (TSB) & PMC", "Ramp Rate (7d)", "Estimated Race Pace"),
            row_heights=[0.2, 0.4, 0.2, 0.2]
        )
        
        # --- Row 1: Daily Load ---
        load_fig = px.line(df, x="date", y="load")
        load_trace = load_fig.data[0]
        load_trace.name = "Daily Load"
        load_trace.line = dict(color="rgba(142, 142, 147, 0.6)", width=2)
        fig.add_trace(load_trace, row=1, col=1)
        
        # --- Row 2: Form (TSB), Fitness (CTL), Fatigue (ATL) ---
        # Fitness (CTL)
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["ctl"], 
            name="Fitness (CTL)", 
            line=dict(color="rgba(0, 191, 255, 0.6)", width=2.5)
        ), row=2, col=1)
        
        # Fatigue (ATL)
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["atl"], 
            name="Fatigue (ATL)", 
            line=dict(color="rgba(186, 85, 211, 0.6)", width=1.5)
        ), row=2, col=1)
        
        # Form (TSB)
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["tsb"], 
            name="Form (TSB)", 
            line=dict(color="rgba(76, 187, 23, 0.6)", width=2.5)
        ), row=2, col=1)

        # Add Training Zones to Row 2
        # Risk Zone: Below -30
        fig.add_hrect(y0=-100, y1=-30, fillcolor="rgba(255, 45, 85, 0.1)", line_width=0, layer="below", annotation_text="Risk", annotation_position="top left", row=2, col=1)
        # Optimal Zone: -30 to -10
        fig.add_hrect(y0=-30, y1=-10, fillcolor="rgba(76, 217, 100, 0.1)", line_width=0, layer="below", annotation_text="Optimal", annotation_position="top left", row=2, col=1)
        # Grey Zone: -10 to 5
        fig.add_hrect(y0=-10, y1=5, fillcolor="rgba(142, 142, 147, 0.1)", line_width=0, layer="below", row=2, col=1)
        # Fresh Zone: Above 5
        fig.add_hrect(y0=5, y1=100, fillcolor="rgba(0, 174, 239, 0.1)", line_width=0, layer="below", annotation_text="Fresh", annotation_position="top left", row=2, col=1)

        # --- Row 3: Ramp Rate ---
        # Positive ramp (green) - ramping up
        ramp_positive = df["ramp"].clip(lower=0)
        fig.add_trace(go.Scatter(
            x=df["date"], y=ramp_positive, 
            name="Ramp Up", 
            line=dict(color="rgba(76, 187, 23, 0.6)", width=2),
            fill='tozeroy',
            fillcolor="rgba(76, 187, 23, 0.1)"
        ), row=3, col=1)
        
        # Negative ramp (blue) - ramping down
        ramp_negative = df["ramp"].clip(upper=0)
        fig.add_trace(go.Scatter(
            x=df["date"], y=ramp_negative, 
            name="Ramp Down", 
            line=dict(color="rgba(100, 149, 237, 0.6)", width=2),
            fill='tozeroy',
            fillcolor="rgba(100, 149, 237, 0.1)"
        ), row=3, col=1)
        
        # --- Row 4: Race Pace ---
        pace_history = get_race_pace_history()
        if pace_history:
            df_pace = pd.DataFrame(pace_history)
            # Convert m/s to min/km (float minutes) for plotting
            df_pace["pace_min"] = (1000 / df_pace["speed_mps"]) / 60
            
            fig.add_trace(go.Scatter(
                x=df_pace["date"], y=df_pace["pace_min"],
                name="Est. Race Pace",
                mode='lines+markers',
                line=dict(color="rgba(255, 149, 0, 0.8)", width=2),
                marker=dict(size=4),
                hovertemplate="%{y:.2f} min/km<extra></extra>"
            ), row=4, col=1)
            
            fig.update_yaxes(autorange="reversed", row=4, col=1) 

        fig.update_layout(
            template="plotly_white",
            height=900,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="x unified",
            margin=dict(l=60, r=40, t=100, b=60),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Inter"
            ),
            legend_traceorder="normal"
        )

        # Sync axes and add spikelines for "same line" effect across all subplots
        fig.update_xaxes(
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikethickness=1,
            spikedash="solid",
            spikecolor="#666"
        )
        
        fig.update_yaxes(
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikethickness=1,
            spikedash="solid",
            spikecolor="#666"
        )
        
        # Update axis titles
        fig.update_yaxes(title_text="Load", row=1, col=1)
        fig.update_yaxes(title_text="Stress / Balance", row=2, col=1)
        fig.update_yaxes(title_text="Ramp", row=3, col=1)
        fig.update_yaxes(title_text="Pace (min/km)", row=4, col=1)
        fig.update_xaxes(title_text="Date", row=4, col=1)
        
        # Grid lines
        fig.update_xaxes(showgrid=True, gridcolor="rgba(235, 235, 235, 1)")
        fig.update_yaxes(showgrid=True, gridcolor="rgba(235, 235, 235, 1)")
        
        return fig

    @render.ui
    def latest_values():
        df = calculate_trends()
        last_row = df.iloc[-1]
        
        date_str = last_row["date"].strftime("%b %d")
        fitness = round(last_row["ctl"])
        fatigue = round(last_row["atl"])
        form = round(last_row["tsb"])
        
        # Determine training zone
        zone = "Neutral"
        zone_color = "#999"
        if form < -30:
            zone = "Risk"
            zone_color = "#FF2D55"
        elif -30 <= form < -10:
            zone = "Optimal Training Zone"
            zone_color = "#4CD964"
        elif form > 5:
            zone = "Freshness"
            zone_color = "#00AEEF"
            
        return ui.div(
            ui.h4(date_str, style="margin-top:0; color:#666;"),
            ui.div(
                ui.p("Fitness", style="margin-bottom:0; font-size: 0.9em; color: #888;"),
                ui.h2(str(fitness), style="margin-top:0; color: #00AEEF;"),
                
                ui.p("Fatigue", style="margin-bottom:0; font-size: 0.9em; color: #888;"),
                ui.h2(str(fatigue), style="margin-top:0; color: #FF2D55;"),
                
                ui.p("Form", style="margin-bottom:0; font-size: 0.9em; color: #888;"),
                ui.h2(str(form), style=f"margin-top:0; color: {zone_color};"),
                
                ui.p(zone, style=f"font-weight: bold; color: {zone_color}; padding: 5px 10px; border-radius: 4px; background: {zone_color}1a; display: inline-block;")
            )
            )


    @render.ui
    def performance_metrics():
        preds = calculate_predictions()
        return ui.div(
             {"class": "card p-3 mb-3"},
            ui.h5("Predicted Paces", style="font-weight: 700; margin-bottom: 15px; color: #333;"),
            ui.div(
                ui.div(
                    ui.p("Reference Race Pace", style="margin-bottom:2px; font-size: 0.85em; color: #888; text-transform: uppercase; letter-spacing: 0.5px;"),
                    ui.h3(preds["race_pace"], style="margin-top:0; margin-bottom: 12px; color: #007AFF; font-weight: 600;"),
                ),
                ui.div(
                    ui.p("Zone 2 (Endurance)", style="margin-bottom:2px; font-size: 0.85em; color: #888; text-transform: uppercase; letter-spacing: 0.5px;"),
                    ui.h4(preds["zone2_pace"], style="margin-top:0; margin-bottom: 12px; color: #333; font-weight: 500;"),
                ),
                ui.div(
                    ui.p("Easy Run", style="margin-bottom:2px; font-size: 0.85em; color: #888; text-transform: uppercase; letter-spacing: 0.5px;"),
                    ui.h4(preds["easy_pace"], style="margin-top:0; margin-bottom: 0px; color: #333; font-weight: 500;"),
                )
            )
        )

app = App(app_ui, server)
