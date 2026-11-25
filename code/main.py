
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------
# 페이지 설정
# --------------------------------
st.set_page_config(
    page_title="기상조건이 항공기 지연에 미치는 영향",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ 기상조건이 항공기 지연에 미치는 영향")
st.caption("강수량과 최대 풍속은 항공기 지연율과 어떤 관계가 있을까?")

# --------------------------------
# 데이터 불러오기
# --------------------------------
DATA_PATH = Path(__file__).parent / "data" / "2024,2025,2026 data.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    numeric_columns = [
        "일 강수량 (mm)",
        "최대 풍속 (m/s)",
        "총 운항편",
        "지연편",
        "지연율 (%)"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 지연율이 비어 있으면 지연편 / 총 운항편으로 계산
    calculated_rate = (
        df["지연편"] / df["총 운항편"] * 100
    )

    df["지연율 (%)"] = df["지연율 (%)"].fillna(calculated_rate)

    df = df.dropna(
        subset=[
            "날짜",
            "일 강수량 (mm)",
            "최대 풍속 (m/s)",
            "총 운항편",
            "지연편",
            "지연율 (%)"
        ]
    )

    df = df.sort_values("날짜")

    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "데이터 파일을 찾을 수 없습니다. "
        "data/airline_weather.csv 파일을 확인해 주세요."
    )
    st.stop()
except Exception as e:
    st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()

# --------------------------------
# 데이터 요약
# --------------------------------
st.header("1. 데이터 살펴보기")

col1, col2, col3, col4 = st.columns(4)

col1.metric("전체 관측일", f"{len(df)}일")
col2.metric(
    "평균 강수량",
    f"{df['일 강수량 (mm)'].mean():.1f} mm"
)
col3.metric(
    "평균 최대 풍속",
    f"{df['최대 풍속 (m/s)'].mean():.1f} m/s"
)
col4.metric(
    "평균 지연율",
    f"{df['지연율 (%)'].mean():.1f}%"
)

st.caption(
    f"분석 기간: {df['날짜'].min():%Y-%m-%d} "
    f"~ {df['날짜'].max():%Y-%m-%d}"
)

with st.expander("원본 데이터 표 보기"):
    st.dataframe(df, use_container_width=True)

# --------------------------------
# 상관계수 계산 함수
# --------------------------------
def correlation_text(x, y):
    corr = df[x].corr(df[y])

    if pd.isna(corr):
        return None, "계산할 수 없음"

    if corr >= 0.7:
        level = "강한 양의 상관관계"
    elif corr >= 0.3:
        level = "약한 양의 상관관계"
    elif corr > -0.3:
        level = "뚜렷한 선형 상관관계가 약함"
    elif corr > -0.7:
        level = "약한 음의 상관관계"
    else:
        level = "강한 음의 상관관계"

    return corr, level


def make_scatter(x, y, title, x_label, y_label):
    fig = px.scatter(
        df,
        x=x,
        y=y,
        hover_data=[
            "날짜",
            "날씨 특징",
            "주된 지연 사유"
        ],
        trendline="ols",
        title=title,
        labels={
            x: x_label,
            y: y_label
        }
    )

    fig.update_layout(
        height=480,
        hovermode="closest"
    )

    return fig


# --------------------------------
# 2. 강수량과 지연율
# --------------------------------
st.header("2. 강수량과 항공기 지연율의 관계")

corr_rain, level_rain = correlation_text(
    "일 강수량 (mm)",
    "지연율 (%)"
)

if corr_rain is not None:
    a, b = st.columns(2)
    a.metric("상관계수", f"{corr_rain:.3f}")
    b.metric("관계의 정도", level_rain)

fig1 = make_scatter(
    "일 강수량 (mm)",
    "지연율 (%)",
    "일 강수량과 항공기 지연율",
    "일 강수량 (mm)",
    "항공기 지연율 (%)"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것**  \n"
    "강수량이 많아질수록 항공기 지연율이 높아지는 경향이 있는지 확인한다."
)

# --------------------------------
# 3. 풍속과 지연율
# --------------------------------
st.header("3. 최대 풍속과 항공기 지연율의 관계")

corr_wind, level_wind = correlation_text(
    "최대 풍속 (m/s)",
    "지연율 (%)"
)

if corr_wind is not None:
    a, b = st.columns(2)
    a.metric("상관계수", f"{corr_wind:.3f}")
    b.metric("관계의 정도", level_wind)

fig2 = make_scatter(
    "최대 풍속 (m/s)",
    "지연율 (%)",
    "최대 풍속과 항공기 지연율",
    "최대 풍속 (m/s)",
    "항공기 지연율 (%)"
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것**  \n"
    "최대 풍속이 강해질수록 항공기 지연율이 높아지는 경향이 있는지 확인한다."
)

# --------------------------------
# 4. 날짜별 강수량과 지연율
# --------------------------------
st.header("4. 날짜별 강수량과 지연율 변화")

fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(
        x=df["날짜"],
        y=df["일 강수량 (mm)"],
        mode="lines+markers",
        name="일 강수량",
        yaxis="y"
    )
)

fig3.add_trace(
    go.Scatter(
        x=df["날짜"],
        y=df["지연율 (%)"],
        mode="lines+markers",
        name="지연율",
        yaxis="y2"
    )
)

fig3.update_layout(
    title="날짜별 강수량과 지연율 변화",
    xaxis_title="날짜",
    yaxis=dict(
        title="일 강수량 (mm)"
    ),
    yaxis2=dict(
        title="지연율 (%)",
        overlaying="y",
        side="right"
    ),
    height=500,
    hovermode="x unified"
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것**  \n"
    "비가 많이 내린 날짜에 항공기 지연율도 함께 높아졌는지 살펴본다."
)

# --------------------------------
# 5. 날짜별 풍속과 지연율
# --------------------------------
st.header("5. 날짜별 최대 풍속과 지연율 변화")

fig4 = go.Figure()

fig4.add_trace(
    go.Scatter(
        x=df["날짜"],
        y=df["최대 풍속 (m/s)"],
        mode="lines+markers",
        name="최대 풍속",
        yaxis="y"
    )
)

fig4.add_trace(
    go.Scatter(
        x=df["날짜"],
        y=df["지연율 (%)"],
        mode="lines+markers",
        name="지연율",
        yaxis="y2"
    )
)

fig4.update_layout(
    title="날짜별 최대 풍속과 지연율 변화",
    xaxis_title="날짜",
    yaxis=dict(
        title="최대 풍속 (m/s)"
    ),
    yaxis2=dict(
        title="지연율 (%)",
        overlaying="y",
        side="right"
    ),
    height=500,
    hovermode="x unified"
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것**  \n"
    "바람이 강했던 날짜와 항공기 지연율이 높았던 날짜가 겹치는지 살펴본다."
)

# --------------------------------
# 6. 지연율 상위 날짜
# --------------------------------
st.header("6. 지연율이 높았던 날짜")

top_delay = df.sort_values(
    "지연율 (%)",
    ascending=False
).head(10)

fig5 = px.bar(
    top_delay,
    x="지연율 (%)",
    y="날짜",
    orientation="h",
    hover_data=[
        "일 강수량 (mm)",
        "최대 풍속 (m/s)",
        "주된 지연 사유"
    ],
    title="지연율이 높은 날짜 TOP 10"
)

fig5.update_layout(
    yaxis=dict(autorange="reversed"),
    height=450
)

st.plotly_chart(fig5, use_container_width=True)

# --------------------------------
# 7. 분석 시 주의사항
# --------------------------------
st.header("7. 분석 결과를 해석할 때 주의할 점")

st.info(
    """
    - 항공기 지연에는 강수량과 풍속 외에도 눈, 안개, 항공 교통량, 기체 문제,
      공항 시설 문제 등이 영향을 줄 수 있습니다.
    - 이 데이터는 45개의 관측 날짜를 대상으로 하므로 전체 날짜의 운항 상황을
      대표한다고 보기 어렵습니다.
    - 산점도의 추세선과 상관계수는 관계를 살펴보는 참고 자료로 해석해야 합니다.
    """
)

st.caption("항공기 지연과 기상조건 탐구 프로젝트")
