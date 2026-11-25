
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =====================================
# 페이지 설정
# =====================================
st.set_page_config(
    page_title="기상조건이 항공기 지연에 미치는 영향",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ 기상조건이 항공기 지연에 미치는 영향")
st.markdown(
    "### 강수량과 최대 풍속은 항공기 지연율에 어떤 영향을 미칠까?"
)

st.divider()

# =====================================
# 데이터 불러오기
# =====================================
DATA_PATH = (
    Path(__file__).parent
    / "data"
    / "2024.2025.2026 data.csv"
)

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

    # 열 이름 앞뒤 공백 제거
    df.columns = df.columns.str.strip()

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "일 강수량 (mm)",
        "최대 풍속 (m/s)",
        "총 운항편",
        "지연편",
        "지연율 (%)"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 지연율 재계산
    calculated_rate = (
        df["지연편"] / df["총 운항편"] * 100
    )

    df["지연율 (%)"] = df["지연율 (%)"].fillna(
        calculated_rate
    )

    # 분석에 필요한 숫자와 날짜가 없는 행 제거
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

    return df.sort_values("날짜")


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "data/2024.2025.2026 data.csv 경로를 확인해 주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()

# =====================================
# 1. 데이터 기본 정보
# =====================================
st.header("1. 데이터 기본 정보")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "전체 관측일",
    f"{len(df)}일"
)

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

st.write(
    f"**분석 기간:** "
    f"{df['날짜'].min():%Y-%m-%d} ~ "
    f"{df['날짜'].max():%Y-%m-%d}"
)

with st.expander("원본 데이터 확인하기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# =====================================
# 상관계수 설명 함수
# =====================================
def get_correlation(x, y):
    corr = df[x].corr(df[y])

    if pd.isna(corr):
        return corr, "계산할 수 없음"

    if corr >= 0.7:
        level = "강한 양의 상관관계"
    elif corr >= 0.3:
        level = "약한 양의 상관관계"
    elif corr > -0.3:
        level = "뚜렷한 선형 관계가 약함"
    elif corr > -0.7:
        level = "약한 음의 상관관계"
    else:
        level = "강한 음의 상관관계"

    return corr, level


# =====================================
# 2. 강수량과 지연율 산점도
# =====================================
st.header("2. 강수량과 항공기 지연율의 관계")

corr_rain, level_rain = get_correlation(
    "일 강수량 (mm)",
    "지연율 (%)"
)

c1, c2 = st.columns(2)

c1.metric(
    "강수량과 지연율의 상관계수",
    f"{corr_rain:.3f}" if pd.notna(corr_rain) else "계산 불가"
)

c2.metric(
    "상관관계 해석",
    level_rain
)

fig1 = px.scatter(
    df,
    x="일 강수량 (mm)",
    y="지연율 (%)",
    trendline="ols",
    hover_data=[
        "날짜",
        "최대 풍속 (m/s)",
        "날씨 특징",
        "주된 지연 사유"
    ],
    title="일 강수량과 항공기 지연율"
)

fig1.update_layout(height=500)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.markdown(
    "**이 그래프로 알 수 있는 것**  \n"
    "강수량이 많아질수록 항공기 지연율이 높아지는 경향이 있는지 알아본다."
)

st.divider()

# =====================================
# 3. 풍속과 지연율 산점도
# =====================================
st.header("3. 최대 풍속과 항공기 지연율의 관계")

corr_wind, level_wind = get_correlation(
    "최대 풍속 (m/s)",
    "지연율 (%)"
)

c1, c2 = st.columns(2)

c1.metric(
    "풍속과 지연율의 상관계수",
    f"{corr_wind:.3f}" if pd.notna(corr_wind) else "계산 불가"
)

c2.metric(
    "상관관계 해석",
    level_wind
)

fig2 = px.scatter(
    df,
    x="최대 풍속 (m/s)",
    y="지연율 (%)",
    trendline="ols",
    hover_data=[
        "날짜",
        "일 강수량 (mm)",
        "날씨 특징",
        "주된 지연 사유"
    ],
    title="최대 풍속과 항공기 지연율"
)

fig2.update_layout(height=500)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown(
    "**이 그래프로 알 수 있는 것**  \n"
    "바람이 강해질수록 항공기 지연율이 높아지는 경향이 있는지 알아본다."
)

st.divider()

# =====================================
# 4. 날짜별 강수량과 지연율
# =====================================
st.header("4. 날짜별 강수량과 지연율 변화")

fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(
        x=df["날짜"],
        y=df["일 강수량 (mm)"],
        name="일 강수량",
        mode="lines+markers",
        yaxis="y"
    )
)

fig3.add_trace(
    go.Scatter(
        x=df["날짜"],
        y=df["지연율 (%)"],
        name="지연율",
        mode="lines+markers",
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

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.markdown(
    "**이 그래프로 알 수 있는 것**  \n"
    "비가 많이 내린 날짜에 항공기 지연율도 함께 높아졌는지 확인한다."
)

st.divider()

# =====================================
# 5. 날짜별 풍속과 지연율
# =====================================
st.header("5. 날짜별 최대 풍속과 지연율 변화")

fig4 = go.Figure()

fig4.add_trace(
    go.Scatter(
        x=df["날짜"],
        y=df["최대 풍속 (m/s)"],
        name="최대 풍속",
        mode="lines+markers",
        yaxis="y"
    )
)

fig4.add_trace(
    go.Scatter(
        x=df["날짜"],
        y=df["지연율 (%)"],
        name="지연율",
        mode="lines+markers",
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

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.markdown(
    "**이 그래프로 알 수 있는 것**  \n"
    "바람이 강했던 날짜와 지연율이 높았던 날짜가 겹치는지 확인한다."
)

st.divider()

# =====================================
# 6. 지연율 상위 10개 날짜
# =====================================
st.header("6. 항공기 지연율 TOP 10")

top10 = df.sort_values(
    "지연율 (%)",
    ascending=False
).head(10)

fig5 = px.bar(
    top10,
    x="지연율 (%)",
    y="날짜",
    orientation="h",
    hover_data=[
        "일 강수량 (mm)",
        "최대 풍속 (m/s)",
        "총 운항편",
        "지연편",
        "주된 지연 사유"
    ],
    title="지연율이 가장 높았던 날짜 TOP 10"
)

fig5.update_layout(
    yaxis=dict(autorange="reversed"),
    height=500
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.markdown(
    "**이 그래프로 알 수 있는 것**  \n"
    "지연율이 높았던 날의 기상조건과 주요 지연 사유를 비교한다."
)

st.divider()

# =====================================
# 7. 기상조건에 따른 지연율 비교
# =====================================
st.header("7. 기상조건별 지연율 비교")

rain_group = pd.cut(
    df["일 강수량 (mm)"],
    bins=[-0.001, 0, 10, 30, 80, float("inf")],
    labels=["비 없음", "0 초과~10mm", "10~30mm", "30~80mm", "80mm 초과"]
)

rain_summary = (
    df.assign(강수량_구간=rain_group)
    .groupby("강수량_구간", observed=False)
    .agg(
        평균_지연율=("지연율 (%)", "mean"),
        관측일수=("날짜", "count")
    )
    .reset_index()
    .dropna()
)

fig6 = px.bar(
    rain_summary,
    x="강수량_구간",
    y="평균_지연율",
    text_auto=".1f",
    title="강수량 구간별 평균 지연율",
    labels={
        "강수량_구간": "강수량 구간",
        "평균_지연율": "평균 지연율 (%)"
    }
)

fig6.update_layout(height=450)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.dataframe(
    rain_summary,
    use_container_width=True
)

st.markdown(
    "**이 그래프로 알 수 있는 것**  \n"
    "강수량이 많은 구간에서 평균 지연율이 높아지는지 비교한다."
)

st.divider()

# =====================================
# 8. 분석 시 주의사항
# =====================================
st.header("8. 분석 결과 해석 시 주의사항")

st.info(
    """
    1. 상관관계가 있다고 해서 기상조건이 지연의 직접적인 원인이라고 단정할 수 없다.
    2. 항공기 지연에는 강수량과 풍속 외에도 눈, 안개, 항공 교통량,
       기체 문제, 공항 시설 문제 등이 영향을 줄 수 있다.
    3. 이 데이터는 45개의 특정 날짜를 대상으로 하므로 전체 날짜의
       항공 운항 상황을 대표한다고 보기 어렵다.
    4. 산점도의 추세선과 상관계수는 관계를 살펴보는 참고 자료로 해석해야 한다.
    """
)

st.caption(
    "기상조건과 항공기 지연의 관계 탐구 프로젝트"
)
