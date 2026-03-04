import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from backend.room_service import get_room_stats
from backend.invoice_service import get_monthly_revenue, get_unpaid_count, get_total_revenue_this_month
from backend.contract_service import get_active_contracts
from utils.helpers import format_currency
from datetime import datetime


def render():
    st.markdown('<p class="main-header">📊 Tổng Quan</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Theo dõi tình trạng phòng trọ và doanh thu</p>', unsafe_allow_html=True)

    # KPI Cards
    room_stats = get_room_stats()
    unpaid = get_unpaid_count()
    revenue = get_total_revenue_this_month()
    occupancy = (room_stats["occupied"] / room_stats["total"] * 100) if room_stats["total"] > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏢 Tổng số phòng", room_stats["total"])
    with col2:
        st.metric("📈 Tỷ lệ lấp đầy", f"{occupancy:.0f}%")
    with col3:
        st.metric("💰 Doanh thu tháng này", format_currency(revenue))
    with col4:
        st.metric("📋 Hóa đơn chưa TT", unpaid)

    st.markdown("---")

    # Charts
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🏢 Trạng thái phòng")
        if room_stats["total"] > 0:
            labels = ["Trống", "Đang thuê", "Bảo trì"]
            values = [room_stats["available"], room_stats["occupied"], room_stats["maintenance"]]
            colors = ["#10b981", "#6366f1", "#f59e0b"]

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors, line=dict(color='rgba(0,0,0,0.3)', width=2)),
                textinfo='label+value',
                textposition='outside',
                textfont=dict(size=14, color='#ccccee'),
                pull=[0.02, 0.02, 0.02],
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ccccee'),
                showlegend=True,
                legend=dict(
                    bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#aaaacc', size=13),
                    orientation='h',
                    yanchor='bottom',
                    y=-0.15,
                    xanchor='center',
                    x=0.5,
                ),
                height=380,
                margin=dict(t=20, b=40, l=20, r=20),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu phòng")

    with col_right:
        st.subheader("💰 Doanh thu theo tháng")
        year = datetime.now().year
        monthly_data = get_monthly_revenue(year)

        if monthly_data:
            df = pd.DataFrame(monthly_data)
            month_names = {
                1: "T1", 2: "T2", 3: "T3", 4: "T4", 5: "T5", 6: "T6",
                7: "T7", 8: "T8", 9: "T9", 10: "T10", 11: "T11", 12: "T12"
            }
            df["month_name"] = df["month"].map(month_names)

            fig = go.Figure(data=[go.Bar(
                x=df["month_name"],
                y=df["revenue"],
                marker=dict(
                    color=df["revenue"],
                    colorscale=[[0, '#6366f1'], [0.5, '#8b5cf6'], [1, '#a78bfa']],
                    line=dict(color='rgba(99, 102, 241, 0.8)', width=1),
                ),
                text=[format_currency(r) for r in df["revenue"]],
                textposition='outside',
                textfont=dict(color='#aaaacc', size=11),
                hovertemplate='Tháng %{x}<br>Doanh thu: %{text}<extra></extra>',
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ccccee'),
                xaxis=dict(
                    gridcolor='rgba(99, 102, 241, 0.05)',
                    title="",
                ),
                yaxis=dict(
                    gridcolor='rgba(99, 102, 241, 0.08)',
                    title="",
                    tickformat=',',
                ),
                height=380,
                margin=dict(t=20, b=40, l=60, r=20),
                bargap=0.3,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"Chưa có doanh thu năm {year}")

    # Active contracts table
    st.markdown("---")
    st.subheader("📝 Hợp đồng đang hiệu lực")
    active_contracts = get_active_contracts()
    if active_contracts:
        df = pd.DataFrame(active_contracts)
        display_df = df[["room_number", "tenant_name", "start_date", "end_date", "deposit", "room_price"]].copy()
        display_df.columns = ["Phòng", "Khách thuê", "Ngày bắt đầu", "Ngày kết thúc", "Tiền cọc", "Giá phòng"]
        display_df["Tiền cọc"] = display_df["Tiền cọc"].apply(format_currency)
        display_df["Giá phòng"] = display_df["Giá phòng"].apply(format_currency)
        display_df["Ngày kết thúc"] = display_df["Ngày kết thúc"].replace("", "—")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có hợp đồng nào đang hiệu lực")
