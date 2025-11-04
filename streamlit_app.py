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
    "Example project for **Arts & Advanced Big Data (Week 10)**\n\n"
    "Use the sidebar to switch between three demos."
)

page = st.sidebar.radio("Choose a Page", ["🎨 Artwork Explorer", "☁️ Weather", "📈 KOSPI200"])

st.markdown("# Arts & Advanced Big Data — Open API Lab")

# ============ PAGE 1: ARTWORKS ============
if page == "🎨 Artwork Explorer":
    st.subheader("🎨 Artwork Explorer")
    st.write("Search artworks from the Art Institute of Chicago (no API key needed).")

    col1, col2 = st.columns([2,1])
    query = col1.text_input("Search keyword", value="flower")
    limit = col2.selectbox("Results per page", [6, 12, 24], index=1)
    go = st.button("Search")

    if go:
        page_num = st.session_state.get("art_page", 1)
        data = fetch_artworks(query, page=page_num, limit=limit)
        hits = data.get("data", [])
        pages = data.get("pagination", {}).get("total_pages", 1)
        st.session_state["art_page_total"] = pages

        if not hits:
            st.info("No results found.")
        else:
            cols = st.columns(3)
            for i, item in enumerate(hits):
                title = item.get("title") or "Untitled"
                artist = item.get("artist_display") or "Unknown"
                date = item.get("date_display") or ""
                img = build_art_image_url(item.get("image_id"))
                with cols[i % 3]:
                    with st.container(border=True):
                        if img:
                            st.image(img, use_column_width=True)
                        st.markdown(f"**{title}**  \n{artist}  \n*{date}*")

            left, mid, right = st.columns([1,2,1])
            with left:
                if st.button("⬅️ Prev", disabled=page_num <= 1):
                    st.session_state["art_page"] = max(1, page_num - 1)
                    st.rerun()
            with mid:
                st.caption(f"Page {page_num}/{pages}")
            with right:
                if st.button("Next ➡️", disabled=page_num >= pages):
                    st.session_state["art_page"] = min(pages, page_num + 1)
                    st.rerun()

    if not st.session_state.get("art_page"):
        st.session_state["art_page"] = 1
        st.rerun()

# ============ PAGE 2: WEATHER ============
elif page == "☁️ Weather":
    st.subheader("☁️ Weather Forecast (Open-Meteo)")
    city = st.text_input("Enter City", value="Seoul")
    go = st.button("Get Forecast")

    if go:
        info = geocode_city(city)
        if not info:
            st.error("City not found.")
        else:
            st.success(f"Found {info['name']} ({info['country']})")
            data = fetch_weather(info["lat"], info["lon"])
            hourly = data.get("hourly", {})
            df = pd.DataFrame({
                "time": pd.to_datetime(hourly.get("time", [])),
                "temp (°C)": hourly.get("temperature_2m", []),
                "humidity (%)": hourly.get("relative_humidity_2m", [])
            })
            if df.empty:
                st.info("No data available.")
            else:
                st.plotly_chart(px.line(df, x="time", y="temp (°C)", title="Temperature"), use_container_width=True)
                st.plotly_chart(px.line(df, x="time", y="humidity (%)", title="Humidity"), use_container_width=True)
                st.dataframe(df.tail(24))

# ============ PAGE 3: KOSPI200 ============
elif page == "📈 KOSPI200":
    st.subheader("📈 KOSPI200 Daily Chart")
    st.caption("Try to fetch data online from Stooq or upload your own CSV file.")
    col1, col2 = st.columns([1,1])

    with col1:
        if st.button("Fetch Online"):
            try:
                raw = fetch_stooq_csv("^ks200")
                df = pd.read_csv(io.StringIO(raw))
                df["Date"] = pd.to_datetime(df["Date"])
                df = df.sort_values("Date")
                st.success(f"{len(df)} rows loaded.")
                st.plotly_chart(px.line(df, x="Date", y="Close", title="KOSPI200 Close"), use_container_width=True)
                st.dataframe(df.tail(10))
            except Exception as e:
                st.warning(f"Online fetch failed: {e}")

    with col2:
        upload = st.file_uploader("Upload CSV file", type=["csv"])
        if upload:
            try:
                df = pd.read_csv(upload)
                if "Date" in df.columns:
                    df["Date"] = pd.to_datetime(df["Date"])
                    df = df.sort_values("Date")
                ycol = "Close" if "Close" in df.columns else df.columns[-1]
                st.success(f"{len(df)} rows uploaded.")
                st.plotly_chart(px.line(df, x="Date" if "Date" in df.columns else df.index, y=ycol, title=ycol),
                                use_container_width=True)
                st.dataframe(df.tail(10))
            except Exception as e:
                st.error(f"Parse error: {e}")
