import io
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
from utils import (
    geocode_city, fetch_weather,
    fetch_artworks, build_art_image_url,
    fetch_stooq_csv
)

st.set_page_config(page_title="Open API Lab", page_icon="🎨", layout="wide")

st.sidebar.title("Open API Playground")
st.sidebar.markdown(
    "课程主题：Open API + Streamlit（示例：艺术品、天气、指数）\n\n"
    "Tips: 输入关键词/城市后点击按钮即可请求真实在线数据。"
)

page = st.sidebar.radio("选择页面", ["🎨 Artwork Explorer", "☁️ Weather", "📈 KOSPI200"])

st.markdown("""
# Arts & Advanced Big Data — Open API Lab
*Built with Streamlit × Public APIs*
""")

if page == "🎨 Artwork Explorer":
    st.subheader("🎨 Artwork Explorer")
    with st.expander("说明", True):
        st.write("基于 **Art Institute of Chicago API** 的公开数据，搜索并展示艺术品卡片，无需密钥。")
        st.caption("Try keywords: *Monet*, *Van Gogh*, *flower*, *portrait* …")

    colq, coll = st.columns([2,1], vertical_alignment="bottom")
    with colq:
        query = st.text_input("Search query", value="flower")
    with coll:
        limit = st.selectbox("Batch size", [6, 12, 24], index=1)

    go = st.button("Search")
    if go:
        page_num = st.session_state.get("art_page", 1)
        data = fetch_artworks(query, page=page_num, limit=limit)
        hits = data.get("data", [])
        pagination = data.get("pagination", {})
        st.session_state["art_page_total"] = pagination.get("total_pages", 1)

        if not hits:
            st.info("No results.")
        else:
            cols = st.columns(3)
            for i, item in enumerate(hits):
                title = item.get("title") or "Untitled"
                artist = item.get("artist_display") or "Unknown artist"
                date = item.get("date_display") or ""
                img_url = build_art_image_url(item.get("image_id"))
                with cols[i % 3]:
                    with st.container(border=True):
                        if img_url:
                            st.image(img_url, use_column_width=True)
                        st.markdown(f"**{title}**  \n{artist}  \n*{date}*")

            left, mid, right = st.columns([1,2,1])
            with left:
                if st.button("⬅️ Prev", disabled=page_num <= 1):
                    st.session_state["art_page"] = max(1, page_num - 1)
                    st.rerun()
            with mid:
                st.caption(f"Page {page_num} / {st.session_state['art_page_total']}")
            with right:
                if st.button("Next ➡️", disabled=page_num >= st.session_state["art_page_total"]):
                    st.session_state["art_page"] = min(st.session_state["art_page_total"], page_num + 1)
                    st.rerun()

    if not st.session_state.get("art_page"):
        st.session_state["art_page"] = 1
        st.rerun()

elif page == "☁️ Weather":
    st.subheader("☁️ Weather (Open-Meteo)")
    with st.expander("说明", True):
        st.write("使用 **Open-Meteo**：先地理编码城市→获取未来72小时温湿度→折线图展示。无需密钥。")
        st.caption("例：Seoul, Busan, Tokyo, New York, London …")

    c1, c2 = st.columns([2,1])
    with c1:
        city = st.text_input("City", value="Seoul")
    with c2:
        go = st.button("Get Forecast")

    if go:
        info = geocode_city(city)
        if not info:
            st.error("City not found. Try another name.")
        else:
            st.success(f"Found: {info['name']} ({info['country']})  —  lat: {info['lat']}, lon: {info['lon']}")
            data = fetch_weather(info["lat"], info["lon"])
            hourly = data.get("hourly") or {}
            times = hourly.get("time") or []
            temps = hourly.get("temperature_2m") or []
            hums  = hourly.get("relative_humidity_2m") or []
            if not times:
                st.info("No hourly data.")
            else:
                df = pd.DataFrame({"time": pd.to_datetime(times),
                                   "temp(°C)": temps,
                                   "humidity(%)": hums})
                fig1 = px.line(df, x="time", y="temp(°C)", title="Temperature (Next ~72h)")
                fig2 = px.line(df, x="time", y="humidity(%)", title="Humidity (Next ~72h)")
                st.plotly_chart(fig1, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)
                st.dataframe(df.tail(24), use_container_width=True)

elif page == "📈 KOSPI200":
    st.subheader("📈 KOSPI200 (Daily)")
    with st.expander("说明", True):
        st.write("尝试从 **Stooq** 获取 KOSPI200 日线CSV（免密钥）。若网络限制，可上传本地CSV作为回退。")
        st.caption("CSV 需包含列：Date, Open, High, Low, Close, Volume（常见行情CSV格式）")

    c1, c2 = st.columns([1,1])
    with c1:
        st.caption("在线拉取（默认尝试 ^ks200）")
        if st.button("Fetch Online CSV"):
            try:
                raw = fetch_stooq_csv("^ks200")
                df = pd.read_csv(io.StringIO(raw))
                df["Date"] = pd.to_datetime(df["Date"])
                df = df.sort_values("Date")
                st.success(f"Loaded {len(df)} rows.")
                fig = px.line(df, x="Date", y="Close", title="KOSPI200 — Close")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df.tail(10), use_container_width=True)
            except Exception as e:
                st.warning(f"在线获取失败：{e}")

    with c2:
        st.caption("本地上传回退")
        up = st.file_uploader("Upload CSV", type=["csv"])
        if up is not None:
            try:
                df = pd.read_csv(up)
                if "Date" in df.columns:
                    df["Date"] = pd.to_datetime(df["Date"])
                    df = df.sort_values("Date")
                st.success(f"Loaded {len(df)} rows from upload.")
                ycol = "Close" if "Close" in df.columns else df.columns[-1]
                fig = px.line(df, x="Date" if "Date" in df.columns else df.index, y=ycol, title=f"Uploaded — {ycol}")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df.tail(10), use_container_width=True)
            except Exception as e:
                st.error(f"解析失败：{e}")
