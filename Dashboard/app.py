import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0f1117; color: #e2e8f0; }
[data-testid="stSidebar"] { background: #161b27 !important; border-right: 1px solid #1e2a3a; }
[data-testid="stSidebar"] label { color: #94a3b8 !important; font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; }

.kpi-card {
    background: linear-gradient(135deg, #161b27 0%, #1a2035 100%);
    border: 1px solid #1e2a3a;
    border-radius: 12px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; border-radius: 12px 0 0 12px; }
.kpi-card.blue::before   { background: #3b82f6; }
.kpi-card.green::before  { background: #10b981; }
.kpi-card.purple::before { background: #8b5cf6; }
.kpi-card.orange::before { background: #f59e0b; }
.kpi-label { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #475569; margin-bottom: 8px; }
.kpi-value { font-size: 1.85rem; font-weight: 700; color: #f1f5f9; line-height: 1; margin-bottom: 5px; }
.kpi-sub   { font-size: 0.72rem; color: #475569; }
.kpi-icon  { position: absolute; top: 16px; right: 18px; font-size: 1.6rem; opacity: 0.13; }

.section-header { font-size: 0.67rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #3b82f6; margin-bottom: 2px; }
.section-title  { font-size: 1.15rem; font-weight: 600; color: #e2e8f0; margin-bottom: 14px; }

.chart-card { background: #161b27; border: 1px solid #1e2a3a; border-radius: 12px; padding: 20px; }
.insight-box {
    background: #0d1520;
    border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 9px 13px;
    margin-top: 10px;
    font-size: 0.77rem;
    color: #94a3b8;
    line-height: 1.5;
}
hr { border-color: #1e2a3a !important; }
.stMultiSelect [data-baseweb="tag"] { background-color: #1e3a5f !important; color: #93c5fd !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA LOADER
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    file_path = "D:/E-Commerce Sales & Customer Insights/Data/master_orders.csv"
    df = pd.read_csv(
        file_path,
        sep=";",
        quotechar='"',
        na_values=["NULL"],
        engine="python",
    )
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"], errors="coerce"
    )
    df["order_delivered_customer_date"] = pd.to_datetime(
        df["order_delivered_customer_date"], errors="coerce"
    )
    return df


# ─────────────────────────────────────────────
#  PLOTLY DARK THEME HELPER
# ─────────────────────────────────────────────
CHART_BG   = "#161b27"
PAPER_BG   = "#161b27"
GRID_COLOR = "#1e2a3a"
TEXT_COLOR = "#94a3b8"
ACCENT     = "#3b82f6"
PALETTE    = ["#3b82f6","#10b981","#8b5cf6","#f59e0b","#ef4444","#06b6d4","#f97316","#ec4899","#a3e635","#fb923c"]

def dark_theme(fig, height=360):
    fig.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=CHART_BG,
        font=dict(family="Inter", color=TEXT_COLOR, size=11),
        height=height, margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID_COLOR, font=dict(size=11, color=TEXT_COLOR)),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR)),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR)),
    )
    return fig


# ─────────────────────────────────────────────
#  LOAD & PREP
# ─────────────────────────────────────────────
with st.spinner("Loading data…"):
    df = load_data()

df_delivered = df[df["order_status"] == "delivered"].copy()
df_delivered["year_month"]    = df_delivered["order_purchase_timestamp"].dt.to_period("M")
df_delivered["delivery_days"] = (
    df_delivered["order_delivered_customer_date"] - df_delivered["order_purchase_timestamp"]
).dt.days


# ─────────────────────────────────────────────
#  SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 E-Commerce Intel")
    st.markdown("<hr style='margin:8px 0 18px'>", unsafe_allow_html=True)

    st.markdown("**DATE RANGE**")
    min_date = df_delivered["order_purchase_timestamp"].min().date()
    max_date = df_delivered["order_purchase_timestamp"].max().date()
    date_from, date_to = st.date_input(
        "Range", value=(min_date, max_date),
        min_value=min_date, max_value=max_date, label_visibility="collapsed",
    )

    st.markdown("<br>**STATES**", unsafe_allow_html=True)
    all_states = sorted(df_delivered["customer_state"].dropna().unique())
    sel_states = st.multiselect("States", all_states, default=all_states, label_visibility="collapsed")

    st.markdown("<br>**PAYMENT TYPE**", unsafe_allow_html=True)
    all_pay = sorted(df_delivered["payment_type"].dropna().unique())
    sel_pay = st.multiselect("Payments", all_pay, default=all_pay, label_visibility="collapsed")

    st.markdown("<br>**PRODUCT CATEGORIES**", unsafe_allow_html=True)
    all_cats = sorted(df_delivered["product_category_name"].dropna().unique())
    sel_cats = st.multiselect("Categories", all_cats, default=all_cats, label_visibility="collapsed")

    st.markdown("---")
    st.caption("Olist E-Commerce Dataset")


# ─────────────────────────────────────────────
#  APPLY FILTERS
# ─────────────────────────────────────────────
mask = (
    (df_delivered["order_purchase_timestamp"].dt.date >= date_from) &
    (df_delivered["order_purchase_timestamp"].dt.date <= date_to)   &
    (df_delivered["customer_state"].isin(sel_states))               &
    (df_delivered["payment_type"].isin(sel_pay))                    &
    (df_delivered["product_category_name"].isin(sel_cats))
)
fdf = df_delivered[mask].copy()


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style="padding:24px 0 14px">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#3b82f6;margin-bottom:4px">ANALYTICS DASHBOARD</div>
  <div style="font-size:1.95rem;font-weight:700;color:#f1f5f9;line-height:1.2">E-Commerce Sales &amp; Customer Insights</div>
  <div style="font-size:0.85rem;color:#475569;margin-top:5px">Delivered orders · Revenue trends · Customer behavior · Regional performance</div>
</div>
<hr style="border-color:#1e2a3a;margin-bottom:24px">
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  KPI CARDS
# ─────────────────────────────────────────────
total_revenue = fdf["payment_value"].sum()
total_orders  = fdf["order_id"].nunique()
aov           = total_revenue / total_orders if total_orders else 0
avg_review    = fdf["review_score"].mean()
avg_freight   = fdf["freight_value"].mean()
avg_delivery  = fdf["delivery_days"].mean()

k1, k2, k3, k4 = st.columns(4)
for col, label, value, sub, color, icon in [
    (k1, "Total Revenue",     f"${total_revenue:,.0f}",    f"{total_orders:,} delivered orders", "blue",   "💰"),
    (k2, "Avg Order Value",   f"${aov:,.2f}",              f"Avg freight: ${avg_freight:.2f}",   "green",  "🛒"),
    (k3, "Avg Review Score",  f"{avg_review:.2f} / 5.00",  "Customer satisfaction rating",       "purple", "⭐"),
    (k4, "Avg Delivery Time", f"{avg_delivery:.1f} days",  "From purchase to delivery",          "orange", "🚚"),
]:
    col.markdown(f"""
    <div class="kpi-card {color}">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ROW 1 — Monthly Trend + Order Status Donut
# ─────────────────────────────────────────────
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown('<div class="section-header">REVENUE TREND</div><div class="section-title">Monthly Sales Performance</div>', unsafe_allow_html=True)
    monthly = fdf.groupby("year_month")["payment_value"].sum().reset_index().sort_values("year_month")
    monthly["month_str"] = monthly["year_month"].astype(str)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=monthly["month_str"], y=monthly["payment_value"],
        mode="lines+markers",
        line=dict(color=ACCENT, width=2.5),
        marker=dict(size=6, color=ACCENT, line=dict(width=1.5, color="#0f1117")),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
    ))
    fig1 = dark_theme(fig1, 340)
    fig1.update_xaxes(tickangle=45)
    st.plotly_chart(fig1, width='stretch')
    st.markdown('<div class="insight-box">📌 <b>Insight:</b> Revenue shows consistent seasonal peaks — align inventory replenishment and campaigns to high-demand months.</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="section-header">OPERATIONS</div><div class="section-title">Order Status Breakdown</div>', unsafe_allow_html=True)
    STATUS_COLORS = {"delivered":"#10b981","canceled":"#ef4444","shipped":"#3b82f6",
                     "unavailable":"#64748b","processing":"#f59e0b","invoiced":"#8b5cf6",
                     "created":"#06b6d4","approved":"#ec4899"}
    status_df = df["order_status"].value_counts().reset_index()
    status_df.columns = ["status", "count"]

    fig2 = go.Figure(go.Pie(
        labels=status_df["status"], values=status_df["count"],
        hole=0.62,
        marker_colors=[STATUS_COLORS.get(s, "#475569") for s in status_df["status"]],
        textinfo="percent", textfont=dict(size=11, color="#e2e8f0"),
        hovertemplate="<b>%{label}</b><br>%{value:,} orders<br>%{percent}<extra></extra>",
    ))
    fig2.add_annotation(text=f"<b>{total_orders:,}</b><br>Delivered",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=15, color="#f1f5f9"), align="center")
    fig2 = dark_theme(fig2, 340)
    fig2.update_layout(showlegend=True, legend=dict(orientation="v", x=0, y=0, font=dict(size=10)), margin=dict(l=5,r=5,t=30,b=5))
    st.plotly_chart(fig2, width='stretch')
    st.markdown('<div class="insight-box">📌 <b>Insight:</b> Cancellation rate signals checkout or logistics friction worth investigating.</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ROW 2 — Top Categories + Top States
# ─────────────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="section-header">PRODUCTS</div><div class="section-title">Top 10 Categories by Revenue</div>', unsafe_allow_html=True)
    cat_rev = fdf.groupby("product_category_name")["payment_value"].sum().sort_values(ascending=False).head(10).reset_index()
    cat_rev.columns = ["category", "revenue"]
    cat_rev = cat_rev.sort_values("revenue")

    fig3 = go.Figure(go.Bar(
        x=cat_rev["revenue"], y=cat_rev["category"], orientation="h",
        marker=dict(color=cat_rev["revenue"], colorscale=[[0,"#1e3a5f"],[1,"#3b82f6"]], showscale=False),
        hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>",
    ))
    fig3 = dark_theme(fig3, 380)
    fig3.update_xaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig3, width='stretch')
    st.markdown('<div class="insight-box">📌 <b>Insight:</b> Top categories deserve priority stocking, supplier partnerships, and promotional budget allocation.</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="section-header">GEOGRAPHY</div><div class="section-title">Top 10 States by Revenue</div>', unsafe_allow_html=True)
    state_rev = fdf.groupby("customer_state")["payment_value"].sum().sort_values(ascending=False).head(10).reset_index()
    state_rev.columns = ["state", "revenue"]

    fig4 = go.Figure(go.Bar(
        x=state_rev["state"], y=state_rev["revenue"],
        marker=dict(color=state_rev["revenue"], colorscale=[[0,"#134e2a"],[1,"#10b981"]], showscale=False),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))
    fig4 = dark_theme(fig4, 380)
    fig4.update_yaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig4, width='stretch')
    st.markdown('<div class="insight-box">📌 <b>Insight:</b> High-revenue states are prime candidates for localized logistics investment and regional campaigns.</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ROW 3 — Payment Types + Review Scores
# ─────────────────────────────────────────────
c5, c6 = st.columns(2)

with c5:
    st.markdown('<div class="section-header">PAYMENTS</div><div class="section-title">Payment Method Distribution</div>', unsafe_allow_html=True)
    pay_df = fdf["payment_type"].value_counts().reset_index()
    pay_df.columns = ["payment", "count"]

    fig5 = go.Figure(go.Bar(
        x=pay_df["payment"], y=pay_df["count"],
        marker=dict(color=PALETTE[:len(pay_df)]),
        hovertemplate="<b>%{x}</b><br>%{y:,} orders<extra></extra>",
    ))
    fig5 = dark_theme(fig5, 320)
    fig5.update_yaxes(tickformat=",")
    st.plotly_chart(fig5, width='stretch')
    st.markdown('<div class="insight-box">📌 <b>Insight:</b> Dominant payment methods reveal customer trust — optimize checkout UX around these preferences.</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="section-header">SATISFACTION</div><div class="section-title">Review Score Distribution</div>', unsafe_allow_html=True)
    review_df = fdf["review_score"].value_counts().sort_index().reset_index()
    review_df.columns = ["score", "count"]
    score_colors = ["#ef4444","#f97316","#f59e0b","#84cc16","#10b981"]

    fig6 = go.Figure(go.Bar(
        x=review_df["score"].astype(str), y=review_df["count"],
        marker=dict(color=score_colors[:len(review_df)]),
        hovertemplate="Score <b>%{x}</b><br>%{y:,} orders<extra></extra>",
    ))
    fig6 = dark_theme(fig6, 320)
    fig6.update_xaxes(title_text="Review Score (1–5)")
    fig6.update_yaxes(tickformat=",")
    st.plotly_chart(fig6, width='stretch')
    st.markdown('<div class="insight-box">📌 <b>Insight:</b> Majority of 5-star reviews signals strong satisfaction; lower scores reveal targeted improvement areas.</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ROW 4 — Price Histogram + Avg Review by Category
# ─────────────────────────────────────────────
c7, c8 = st.columns(2)

with c7:
    st.markdown('<div class="section-header">PRICING</div><div class="section-title">Order Payment Value Distribution</div>', unsafe_allow_html=True)
    price_cap = fdf["payment_value"].quantile(0.98)

    fig7 = go.Figure(go.Histogram(
        x=fdf["payment_value"].clip(upper=price_cap), nbinsx=60,
        marker=dict(color=ACCENT, opacity=0.85, line=dict(color="#0f1117", width=0.3)),
        hovertemplate="Payment Value: %{x}<br>Count: %{y}<extra></extra>",
    ))
    fig7 = dark_theme(fig7, 320)
    fig7.update_xaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig7, width='stretch')
    st.markdown('<div class="insight-box">📌 <b>Insight:</b> Right-skewed distribution — most orders are low-to-mid value, revealing upselling and bundling opportunities.</div>', unsafe_allow_html=True)

with c8:
    st.markdown('<div class="section-header">QUALITY</div><div class="section-title">Top 10 Categories by Avg Review Score</div>', unsafe_allow_html=True)
    avg_cat = fdf.groupby("product_category_name")["review_score"].mean().sort_values(ascending=False).head(10).reset_index()
    avg_cat.columns = ["category", "avg_score"]
    avg_cat = avg_cat.sort_values("avg_score")

    fig8 = go.Figure(go.Bar(
        x=avg_cat["avg_score"], y=avg_cat["category"], orientation="h",
        marker=dict(color=avg_cat["avg_score"], colorscale=[[0,"#312e81"],[1,"#8b5cf6"]], showscale=False),
        hovertemplate="<b>%{y}</b><br>Avg Score: %{x:.2f}<extra></extra>",
    ))
    fig8 = dark_theme(fig8, 320)
    fig8.update_xaxes(range=[0, 5])
    st.plotly_chart(fig8, width='stretch')
    st.markdown('<div class="insight-box">📌 <b>Insight:</b> Top-rated categories are prime for promotional spotlights and supplier partnerships.</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  EXECUTIVE SUMMARY
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">EXECUTIVE SUMMARY</div><div class="section-title">Key Business Findings</div>', unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
for col, emoji, title, body in [
    (s1, "📦", "Revenue Structure",    "A handful of categories generate the majority of revenue — a concentrated model with clear priority areas for investment."),
    (s2, "📈", "Seasonal Patterns",    "Monthly peaks reveal predictable demand cycles — align campaigns and inventory to these high-value windows."),
    (s3, "🗺️", "Regional Demand",     "Certain states dominate revenue, pointing to strong regional markets and logistics optimization opportunities."),
    (s4, "⭐", "Customer Satisfaction","High review scores confirm strong product-market fit; lower-rated segments show where to focus quality improvements."),
]:
    col.markdown(f"""
    <div class="chart-card" style="min-height:150px">
      <div style="font-size:1.5rem;margin-bottom:10px">{emoji}</div>
      <div style="font-size:0.85rem;font-weight:600;color:#e2e8f0;margin-bottom:6px">{title}</div>
      <div style="font-size:0.76rem;color:#64748b;line-height:1.6">{body}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center;font-size:0.7rem;color:#334155;padding:12px">E-Commerce Intelligence Dashboard · Olist Dataset · Built with Streamlit & Plotly</div>', unsafe_allow_html=True)