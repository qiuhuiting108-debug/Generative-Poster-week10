# 🎨 Qiu Huiting’s MET Art Explorer
# Data source: The Metropolitan Museum of Art Collection API (public, no key)

import streamlit as st
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Qiu Huiting's MET Art Explorer", page_icon="🎨", layout="wide")

# ----- HEADER -----
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

# ----- SEARCH BOX -----
query = st.text_input("Search for Artworks:", value="flower")

# The Met API (https://collectionapi.metmuseum.org/public/collection/v1/)
def search_objects(keyword):
    url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    params = {"q": keyword, "hasImages": "true"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("objectIDs", [])[:12]  # take first 12 results

def get_object_detail(object_id):
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

if st.button("🔍 Search"):
    if not query:
        st.warning("Please enter a keyword.")
    else:
        with st.spinner("Loading artworks..."):
            ids = search_objects(query)
            if not ids:
                st.info("No artworks found.")
            else:
                cols = st.columns(3)
                for i, oid in enumerate(ids):
                    data = get_object_detail(oid)
                    title = data.get("title", "Untitled")
                    artist = data.get("artistDisplayName", "Unknown Artist")
                    image_url = data.get("primaryImageSmall", "")
                    with cols[i % 3]:
                        with st.container(border=True):
                            if image_url:
                                img = Image.open(BytesIO(requests.get(image_url).content))
                                st.image(img, use_column_width=True)
                            st.markdown(f"**{title}**  \n_{artist}_")
