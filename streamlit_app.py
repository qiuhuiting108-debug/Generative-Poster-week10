# 🎨 Qiu Huiting’s MET Art Explorer
# Data source: The Metropolitan Museum of Art Collection API (public, no key)

import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# -------------------- PAGE SETTINGS --------------------
st.set_page_config(page_title="Qiu Huiting's MET Art Explorer", page_icon="🎨", layout="wide")

# Custom CSS for background and rounded image cards
st.markdown("""
<style>
body {
    background-color: #f7f7f7;
}
div[data-testid="stImage"] img {
    border-radius: 16px;
}
h1 {
    font-weight: 800 !important;
}
.stTextInput > div > div > input {
    border-radius: 20px;
    background-color: #fff;
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown(
    """
    <h1 style='text-align:center; font-weight:800;'>
        🎨 Qiu Huiting’s MET Art Explorer
    </h1>
    <p style='text-align:center; color:gray;'>
        Explore beautiful artworks from The Metropolitan Museum of Art API
    </p>
    """,
    unsafe_allow_html=True
)

# -------------------- SEARCH BAR --------------------
query = st.text_input("Search for Artworks:", value="flower")

# -------------------- FUNCTIONS --------------------
def search_objects(keyword):
    """Search object IDs by keyword"""
    url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    params = {"q": keyword, "hasImages": "true"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    return data.get("objectIDs", [])[:12]  # return first 12 IDs

def get_object_detail(object_id):
    """Fetch object detail"""
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

# -------------------- SEARCH BUTTON --------------------
if st.button("🔍 Search"):
    if not query:
        st.warning("Please enter a keyword.")
    else:
        with st.spinner("Loading artworks..."):
            ids = search_objects(query)
            if not ids:
                st.info("No artworks found.")
            else:
                # Create 3 columns layout
                cols = st.columns(3)
                for i, oid in enumerate(ids):
                    try:
                        data = get_object_detail(oid)
                        title = data.get("title", "Untitled")
                        artist = data.get("artistDisplayName", "Unknown Artist")
                        img_url = data.get("primaryImageSmall", "")

                        with cols[i % 3]:
                            with st.container(border=True):
                                if img_url:
                                    response = requests.get(img_url)
                                    img = Image.open(BytesIO(response.content))
                                    st.image(img, use_column_width=True)
                                st.markdown(f"**{title}**  \n_{artist}_")
                    except Exception as e:
                        st.write(f"⚠️ Error loading artwork ID {oid}: {e}")
