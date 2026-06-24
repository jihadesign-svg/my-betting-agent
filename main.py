import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIGURATION & UI THEMING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pro Betting Analytics Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean, premium dashboard feel
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #e9ecef; }
    div[data-testid="stExpander"] { border: 1px solid #e9ecef; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CORE ANALYTICAL FUNCTIONS
# ---------------------------------------------------------

def calculate_momentum_factor(recent_scores, weights=None):
    """
    Calculates an exponentially or linearly weighted momentum factor based on recent performance.
    Returns a multiplier/modifier to adjust the baseline mean.
    """
    if not recent_scores:
        return 0.0
    
    n = len(recent_scores)
    if weights is None:
        # Linear decay weights favoring the most recent matches
        weights = np.arange(1, n + 1) / sum(np.arange(1, n + 1))
        
    weighted_avg = np.dot(recent_scores, weights)
    baseline = np.mean(recent_scores)
    
    # Normalize momentum shift between -15% and +15% adjustment
    momentum_shift = (weighted_avg - baseline) / (baseline if baseline != 0 else 1)
    return np.clip(momentum_shift, -0.15, 0.15)

def run_monte_carlo(team_a_base, team_a_std, team_b_base, team_b_std, momentum_a, momentum_b, iterations=10000, draw_tolerance=0.25, seed=None):
    """
    Executes high-speed Monte Carlo simulation adjusting baseline performance with momentum factors.

    Parameters:
    - draw_tolerance: float, if > 0 counts outcomes with |diff| <= draw_tolerance as draws
    - seed: optional int for reproducibility
    """
    # Apply momentum multipliers to the base expected ratings/scores
    adj_mean_a = team_a_base * (1 + momentum_a)
    adj_mean_b = team_b_base * (1 + momentum_b)

    # Use a Generator for reproducible, modern RNG
    rng = np.random.default_rng(seed)

    # Generate normal distributions for simulated outcomes
    sim_a = rng.normal(adj_mean_a, team_a_std, iterations)
    sim_b = rng.normal(adj_mean_b, team_b_std, iterations)

    # Ensure no negative scores or points possible in sports modeling
    sim_a = np.clip(sim_a, 0, None)
    sim_b = np.clip(sim_b, 0, None)

    # Matrix operations for lightning-fast metrics calculation
    diff = sim_a - sim_b

    wins_a = np.sum(diff > 0)
    wins_b = np.sum(diff < 0)
    # Count draws using tolerance rather than exact float equality
    if draw_tolerance and draw_tolerance > 0:
        draws = np.sum(np.abs(diff) <= draw_tolerance)
    else:
        draws = np.sum(np.isclose(diff, 0, atol=1e-9))

    prob_a = wins_a / iterations
    prob_b = wins_b / iterations
    prob_draw = draws / iterations

    return sim_a, sim_b, diff, prob_a, prob_b, prob_draw

# ---------------------------------------------------------
# SIDEBAR CONTROL PANEL
# ---------------------------------------------------------
st.sidebar.header("🕹️ Simulation Control Panel")

with st.sidebar.expander("Team Profiles", expanded=True):
    team_a_name = st.text_input("Home Team Name", "Team Alpha")
    team_b_name = st.text_input("Away Team Name", "Team Beta")

with st.sidebar.expander("Model Hyperparameters", expanded=True):
    sim_iterations = st.slider("Monte Carlo Iterations", min_value=1000, max_value=50000, value=10000, step=1000)
    
    st.markdown("### **Baseline Ratings / Expected Scores**")
    t_a_base = st.number_input(f"{team_a_name} Base Expected", value=2.50, step=0.1)
    t_a_std = st.number_input(f"{team_a_name} Volatility (Std Dev)", value=1.10, step=0.05)
    
    st.markdown("---")
    t_b_base = st.number_input(f"{team_b_name} Base Expected", value=1.80, step=0.1)
    t_b_std = st.number_input(f"{team_b_name} Volatility (Std Dev)", value=0.95, step=0.05)

    # Draw tolerance controls
    st.markdown("---")
    draw_tolerance = st.number_input("Draw tolerance (abs spread considered a draw)", value=0.25, step=0.05, min_value=0.0)

    # Optional reproducible RNG seed
    use_seed = st.checkbox("Use fixed RNG seed", value=False)
    if use_seed:
        seed = int(st.number_input("RNG Seed (integer)", value=42, step=1))
    else:
        seed = None

# ---------------------------------------------------------
# MAIN DASHBOARD INTERFACE
# ---------------------------------------------------------
st.title("📊 Advanced Sports Betting Analytics Dashboard")
st.markdown("Quant-based prediction engine leveraging momentum tracking and statistical distributions.")

# Tabs for structured workflow
tab1, tab2, tab3 = st.tabs(["🔥 Momentum Analysis", "🎲 Monte Carlo Engine", "💰 Value & Bankroll Allocation"])

# --- TAB 1: MOMENTUM ANALYSIS ---
with tab1:
    st.subheader("Form & Momentum Analytics")
    st.markdown("Input recent sequence scores (most recent match *last*) to adjust baseline probability profiles.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"##### {team_a_name} Recent Form Trend")
        raw_inputs_a = st.text_input(f"{team_a_name} Last 5 Matches (Comma separated)", "2,3,1,4,3")
        scores_a = []
        for x in raw_inputs_a.split(","):
            s = x.strip()
            if not s:
                continue
            try:
                scores_a.append(float(s))
            except ValueError:
                # skip non-numeric tokens
                continue
        mom_factor_a = calculate_momentum_factor(scores_a)
        
        # UI Visual Feedback
        arrow_a = "📈" if mom_factor_a >= 0 else "📉"
        st.metric(label=f"{team_a_name} Calculated Momentum Modifier", value=f"{mom_factor_a:+.2%}", delta=f"{arrow_a} Effect")
        
    with col2:
        st.markdown(f"##### {team_b_name} Recent Form Trend")
        raw_inputs_b = st.text_input(f"{team_b_name} Last 5 Matches (Comma separated)", "1,1,2,0,2")
        scores_b = []
        for x in raw_inputs_b.split(","):
            s = x.strip()
            if not s:
                continue
            try:
                scores_b.append(float(s))
            except ValueError:
                continue
        mom_factor_b = calculate_momentum_factor(scores_b)
        
        arrow_b = "📈" if mom_factor_b >= 0 else "📉"
        st.metric(label=f"{team_b_name} Calculated Momentum Modifier", value=f"{mom_factor_b:+.2%}", delta=f"{arrow_b} Effect")

    # Form Trend Visualizer
    st.markdown("### Form Velocity Trendlines")
    max_len = max(len(scores_a), len(scores_b))
    if max_len == 0:
        trend_df = pd.DataFrame({'Match Index': []})
    else:
        trend_df = pd.DataFrame({'Match Index': np.arange(1, max_len + 1)})
        trend_df[f'{team_a_name} Performance'] = pd.Series(scores_a + [np.nan] * (max_len - len(scores_a)))
        trend_df[f'{team_b_name} Performance'] = pd.Series(scores_b + [np.nan] * (max_len - len(scores_b)))
    fig_trend = px.line(trend_df, x='Match Index', y=[f'{team_a_name} Performance', f'{team_b_name} Performance'],
                        markers=True, line_shape='spline', title="Recent Match Score Progression")
    fig_trend.update_layout(yaxis_title="Output Metric / Goals / Points", template="plotly_white")
    st.plotly_chart(fig_trend, use_container_width=True)

# --- TAB 2: MONTE CARLO SIMULATION ---
with tab2:
    st.subheader("Stochastic Match Simulation Engine")
    
    # Execute backend simulations
    sim_a, sim_b, diff, p_a, p_b, p_draw = run_monte_carlo(
        t_a_base, t_a_std, t_b_base, t_b_std, mom_factor_a, mom_factor_b,
        sim_iterations, draw_tolerance=draw_tolerance, seed=seed
    )
    
    # Summary Metrics Cards
    m1, m2, m3 = st.columns(3)
    m1.metric(label=f"Projected {team_a_name} Implied Win Probability", value=f"{p_a:.2%}")
    m2.metric(label=f"Projected {team_b_name} Implied Win Probability", value=f"{p_b:.2%}")
    m3.metric(label="Projected Draw Probability", value=f"{p_draw:.2%}")
    
    st.markdown("---")
    
    # Distribution Visualizations
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("##### Simulated Score Distributions")
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(x=sim_a, name=team_a_name, opacity=0.6, marker_color='#1f77b4', nbinsx=30))
        fig_dist.add_trace(go.Histogram(x=sim_b, name=team_b_name, opacity=0.6, marker_color='#ff7f0e', nbinsx=30))
        fig_dist.update_layout(barmode='overlay', template="plotly_white", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_dist, use_container_width=True)
        
    with col_chart2:
        st.markdown("##### Margin of Victory / Goal Spread Distribution")
        fig_diff = px.histogram(pd.DataFrame({'Spread': diff}), x='Spread', color_discrete_sequence=['#2ca02c'], nbinsx=40)
        fig_diff.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Draw Threshold")
        fig_diff.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_diff, use_container_width=True)

# --- TAB 3: VALUE BETTING & BANKROLL ALLOCATION ---
with tab3:
    st.subheader("Value Assessment & Kelly Criterion Management")
    
    col_bet1, col_bet2 = st.columns(2)
    
    with col_bet1:
        st.markdown("##### Bookmaker Line Input")
        market_odds_a = st.number_input(f"Market Odds for {team_a_name} Win (Decimal)", value=2.10, min_value=1.01, step=0.05)
        bankroll = st.number_input("Total Working Capital / Bankroll ($)", value=10000, step=500)
        kelly_fraction = st.slider("Kelly Criterion Multiplier (Fractional Kelly)", min_value=0.1, max_value=1.0, value=0.5, step=0.05)
        
    with col_bet2:
        st.markdown("##### Expected Value & Risk Output")
        
        # Analytical Edge Calculation
        implied_market_prob = 1 / market_odds_a
        edge = p_a - implied_market_prob
        
        # Kelly Formula Calculation: f* = (bp - q) / b = (edge * odds + prob_loss) / odds... simplified:
        if edge > 0:
            b = market_odds_a - 1
            p = p_a
            q = 1 - p
            raw_kelly = (b * p - q) / b
            suggested_stake_pct = raw_kelly * kelly_fraction
            suggested_cash = bankroll * suggested_stake_pct
            
            st.success(f"➕ **Positive Edge Detected! Value Found.**\n\nYour edge over the market is **{edge:+.2%}**.")
            st.metric("Suggested Stake %", f"{suggested_stake_pct:.2%}")
            st.metric("Suggested Bet Size", f"${suggested_cash:,.2f}")
        else:
            st.error(f"❌ **No Market Edge.**\n\nYour model's implied probability ({p_a:.2%}) is lower than or equal to the bookmaker's price ({implied_market_prob:.2%}). **Pass on this market.**")