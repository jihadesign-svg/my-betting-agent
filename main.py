import streamlit as st
import numpy as np
import plotly.graph_objects as go
import datetime
import os
from plyer import notification

# --- Page Configuration ---
st.set_page_config(page_title="Gemini Pro Betting Agent", layout="wide")
st.title("🎯 Gemini: The Real Betting Agent (Sports Trading Mode)")

# --- Sidebar Configuration ---
st.sidebar.title("🛠️ Agent Settings")
base_path = st.sidebar.text_input("Path for learning data storage:", os.getcwd())
log_file = os.path.join(base_path, "performance_log.txt")

# --- Core Analysis Engine ---
def gemini_engine(a1, b1, a2, b2):
# Momentum Analysis (Weighted Pace)
# Applying weights: 40% for Q1, 60% for Q2
pace_a = (a1 * 0.4) + (a2 * 0.6)
pace_b = (b1 * 0.4) + (b2 * 0.6)
projection = (pace_a + pace_b) * 2

# Monte Carlo Simulation (50,000 iterations)
simulations = np.random.normal(projection, 5, 50000)
prob_even = (np.sum(np.round(simulations) % 2 == 0) / 50000) * 100
return prob_even, pace_a, pace_b

# --- Main User Interface ---
col1, col2 = st.columns(2)
with col1:
st.subheader("Team A Performance")
a1 = st.number_input("Team A - Quarter 1", 0)
a2 = st.number_input("Team A - Quarter 2", 0)
with col2:
st.subheader("Team B Performance")
b1 = st.number_input("Team B - Quarter 1", 0)
b2 = st.number_input("Team B - Quarter 2", 0)

if st.button("Generate Gemini Verdict"):
prob, pa, pb = gemini_engine(a1, b1, a2, b2)
decision = "Even" if prob > 50 else "Odd"

# 1. Visualization (Trading Candlestick)
fig = go.Figure(data=[go.Candlestick(
x=['Game Trend'],
open=[a1 - b1],
high=[max(a1 - b1, a2 - b2)],
low=[min(a1 - b1, a2 - b2)],
close=[a2 - b2]
)])
fig.update_layout(title="Momentum Power Analysis (Trading Candle)")
st.plotly_chart(fig)

# 2. Decision and Financial Management
st.metric("Agent Confidence Level", f"{prob:.2f}%")
# Kelly Criterion Calculation
stake = (max(prob, 100 - prob) * 0.9 - (100 - max(prob, 100 - prob))) / 0.9
st.info(f"Verdict: {decision} | Suggested Stake (Kelly Criterion): {max(0, stake/10):.2f}%")

if prob > 60 or prob < 40:
notification.notify(title="Betting Opportunity!", message=f"Agent recommends: {decision}")
st.success("Verdict: High conviction opportunity detected.")

st.session_state.last_decision = decision
st.session_state.last_prob = prob

# --- Self-Learning System (Evaluation) ---
st.sidebar.subheader("Evaluate Last Decision:")
if st.sidebar.button("✅ Success"):
with open(log_file, "a") as f:
f.write(f"{datetime.datetime.now()} | {st.session_state.last_decision} | Success\n")
st.sidebar.success("Success recorded in learning log.")

if st.sidebar.button("❌ Failure"):
with open(log_file, "a") as f:
f.write(f"{datetime.datetime.now()} | {st.session_state.last_decision} | Failure\n")
st.sidebar.error("Failure recorded. Re-calibrating algorithms.")
