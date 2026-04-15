"""
Lost and Found Item Management System
Subject: NoSQL (GTU)
Technology: Python + MongoDB Atlas + Streamlit
"""

import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from bson.objectid import ObjectId
import certifi
import base64

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Lost & Found System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark theme background */
    .stApp {
        background-color: #0f1117;
        color: #e0e0e0;
    }
    .block-container {
        padding: 2rem 3rem;
    }
    h1 {
        font-family: 'Segoe UI', sans-serif;
        color: #4fc3f7;
        font-size: 2.4rem;
        text-align: left;
    }
    h2, h3 {
        color: #81d4fa;
    }
    /* Button color overrides */
    div.stButton > button:first-child {
        background-color: #1565c0;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.4rem 1.2rem;
    }
    div.stButton > button:hover {
        background-color: #1976d2;
        color: white;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    .stAlert {
        border-radius: 10px;
    }

    /* ─── ITEM CARDS ─── */
    .item-card {
        background: linear-gradient(145deg, #1a1f2e, #161b22);
        border: 1px solid #30363d;
        border-radius: 14px;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .item-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(79, 195, 247, 0.15);
        border-color: #4fc3f7;
    }
    .card-img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        display: block;
    }
    .card-placeholder {
        width: 100%;
        height: 180px;
        background: linear-gradient(135deg, #1e293b, #0f172a);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        color: #4fc3f7;
    }
    .card-body {
        padding: 14px 16px;
    }
    .card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 0 0 6px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-location {
        font-size: 0.82rem;
        color: #94a3b8;
        margin: 0 0 8px 0;
    }
    .card-location::before {
        content: "📍 ";
    }
    .badge-lost {
        background-color: #ef5350;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
    }
    .badge-found {
        background-color: #66bb6a;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
    }
    /* Detail popup styling */
    .detail-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        padding: 8px 0;
    }
    .detail-label {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .detail-value {
        font-size: 0.95rem;
        color: #e2e8f0;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MONGODB CONNECTION
# ─────────────────────────────────────────────
@st.cache_resource
def get_db():
    """Connect to MongoDB Atlas with SSL certificate support."""
    MONGO_URI = st.secrets.get("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000,
    )
    client.list_database_names()
    db = client["lost_found_db"]
    return db

try:
    db = get_db()
    items_col = db["items"]
    CONNECTION_OK = True
except Exception as e:
    CONNECTION_OK = False
    conn_error = str(e)

# ─────────────────────────────────────────────
#  HELPER FUNCTIONS  (CRUD)
# ─────────────────────────────────────────────

# Category → emoji map for placeholder cards
CATEGORY_ICONS = {
    "Electronics": "💻", "Clothing": "👕", "Accessories": "👜",
    "Documents": "📄", "Keys": "🔑", "Bags": "🎒", "Other": "📦",
}


def add_item(title, description, category, location, contact, status, image_data=None):
    """INSERT one document into the items collection."""
    doc = {
        "title":       title,
        "description": description,
        "category":    category,
        "location":    location,
        "contact":     contact,
        "status":      status,
        "date":        datetime.now().strftime("%Y-%m-%d %H:%M"),
        "image":       image_data,      # base64 string or None
    }
    result = items_col.insert_one(doc)
    return result.inserted_id


def get_all_items():
    """READ all documents from the items collection."""
    return list(items_col.find().sort("date", -1))


def search_items(category_filter=None, location_filter=None, keyword=None):
    """READ documents with optional filters."""
    query = {}
    if category_filter and category_filter != "All":
        query["category"] = category_filter
    if location_filter and location_filter.strip():
        query["location"] = {"$regex": location_filter, "$options": "i"}
    if keyword and keyword.strip():
        query["$or"] = [
            {"title":       {"$regex": keyword, "$options": "i"}},
            {"description": {"$regex": keyword, "$options": "i"}},
        ]
    return list(items_col.find(query).sort("date", -1))


def update_status(item_id, new_status):
    """UPDATE status field of a document by _id."""
    items_col.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": {"status": new_status}}
    )


def delete_item(item_id):
    """DELETE a document by _id."""
    items_col.delete_one({"_id": ObjectId(item_id)})


def render_card(doc):
    """Render a single item card with image, title, location, and status badge."""
    img_html = ""
    if doc.get("image"):
        img_html = f'<img class="card-img" src="data:image/png;base64,{doc["image"]}" />'
    else:
        icon = CATEGORY_ICONS.get(doc.get("category", ""), "📦")
        img_html = f'<div class="card-placeholder">{icon}</div>'

    status = doc.get("status", "Lost")
    badge_class = "badge-lost" if status == "Lost" else "badge-found"

    card_html = f"""
    <div class="item-card">
        {img_html}
        <div class="card-body">
            <p class="card-title">{doc.get('title', 'Untitled')}</p>
            <p class="card-location">{doc.get('location', 'Unknown')}</p>
            <span class="{badge_class}">{status}</span>
        </div>
    </div>
    """
    return card_html


def render_detail_popup(doc):
    """Show full item details inside an expander (click-to-view)."""
    with st.expander(f"📄 View Details — {doc.get('title', 'Untitled')}", expanded=False):
        col_img, col_info = st.columns([1, 2])

        with col_img:
            if doc.get("image"):
                try:
                    img_bytes = base64.b64decode(doc["image"])
                    st.image(img_bytes, use_container_width=True, caption="Uploaded Photo")
                except Exception:
                    st.write("⚠️ Image not available")
            else:
                icon = CATEGORY_ICONS.get(doc.get("category", ""), "📦")
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#1e293b,#0f172a);
                     border-radius:12px; height:200px; display:flex;
                     align-items:center; justify-content:center; font-size:4rem;">
                    {icon}
                </div>
                """, unsafe_allow_html=True)

        with col_info:
            status = doc.get("status", "Lost")
            badge = "badge-lost" if status == "Lost" else "badge-found"
            st.markdown(f'<span class="{badge}">{status}</span>', unsafe_allow_html=True)
            st.markdown(f"**Title:** {doc.get('title', '')}")
            st.markdown(f"**Category:** {doc.get('category', '')}")
            st.markdown(f"**Location:** 📍 {doc.get('location', '')}")
            st.markdown(f"**Contact:** 📞 {doc.get('contact', '')}")
            st.markdown(f"**Date:** 🗓️ {doc.get('date', '')}")
            st.markdown("---")
            st.markdown(f"**Description:**")
            st.markdown(f"> {doc.get('description', 'No description provided.')}")


def render_cards_grid(docs, cols_per_row=4):
    """Display items as a grid of cards. Detail expander sits right under each card."""
    rows = [docs[i:i + cols_per_row] for i in range(0, len(docs), cols_per_row)]
    for row_docs in rows:
        cols = st.columns(cols_per_row)
        for i, doc in enumerate(row_docs):
            with cols[i]:
                # Card visual
                st.markdown(render_card(doc), unsafe_allow_html=True)
                # Detail expander right under this card
                with st.expander("View Details"):
                    if doc.get("image"):
                        try:
                            img_bytes = base64.b64decode(doc["image"])
                            st.image(img_bytes, use_container_width=True)
                        except Exception:
                            st.write("⚠️ Image not available")
                    st.markdown(f"**📝 Description:**")
                    st.markdown(f"> {doc.get('description', 'No description')}")
                    st.markdown(f"**📂 Category:** {doc.get('category', '')}")
                    st.markdown(f"**📞 Contact:** {doc.get('contact', '')}")
                    st.markdown(f"**🗓️ Date:** {doc.get('date', '')}")


# ─────────────────────────────────────────────
#  SIDEBAR  NAVIGATION
# ─────────────────────────────────────────────
st.sidebar.markdown("## 🔍 Lost & Found")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Home / Dashboard",
     "➕ Add Item",
     "📋 View All Items",
     "🔎 Search & Filter",
     "✏️ Update Status",
     "🗑️ Delete Item"],
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Subject:** NoSQL (GTU)")
st.sidebar.markdown("**Tech Stack:** Python · MongoDB · Streamlit")

if not CONNECTION_OK:
    st.sidebar.error("❌ MongoDB not connected")
else:
    total = items_col.count_documents({})
    lost  = items_col.count_documents({"status": "Lost"})
    found = items_col.count_documents({"status": "Found"})
    st.sidebar.success("✅ MongoDB Connected")
    st.sidebar.markdown(f"**Total Items:** {total}")
    st.sidebar.markdown(f"🔴 Lost: {lost}  |  🟢 Found: {found}")

# ─────────────────────────────────────────────
#  CONNECTION ERROR GUARD
# ─────────────────────────────────────────────
if not CONNECTION_OK:
    st.error(f"Could not connect to MongoDB: {conn_error}")
    st.info("Make sure MongoDB is running locally OR set your Atlas URI in `.streamlit/secrets.toml`")
    st.stop()

# ═══════════════════════════════════════════════════════════════
#  PAGE 1 — HOME / DASHBOARD
# ═══════════════════════════════════════════════════════════════
if menu == "🏠 Home / Dashboard":
    st.title("Lost and Found Item Management System")
    st.markdown("#### *Powered by Python · MongoDB Atlas · Streamlit*")
    st.markdown("---")

    total = items_col.count_documents({})
    lost  = items_col.count_documents({"status": "Lost"})
    found = items_col.count_documents({"status": "Found"})

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Items", total)
    col2.metric("🔴 Lost Items",  lost)
    col3.metric("🟢 Found Items", found)

    st.markdown("---")
    st.subheader("📌 Recent Items")
    recent = list(items_col.find().sort("date", -1).limit(8))
    if recent:
        render_cards_grid(recent, cols_per_row=4)
    else:
        st.info("No items yet. Use **➕ Add Item** to get started.")

# ═══════════════════════════════════════════════════════════════
#  PAGE 2 — ADD ITEM
# ═══════════════════════════════════════════════════════════════
elif menu == "➕ Add Item":
    st.title("➕ Report a Lost or Found Item")
    st.markdown("Fill in the details below to add an item to the system.")
    st.markdown("---")

    with st.form("add_item_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            title    = st.text_input("🏷️ Item Title *",       placeholder="e.g. Blue Wallet")
            category = st.selectbox("📂 Category *",
                                    ["Electronics", "Clothing", "Accessories",
                                     "Documents", "Keys", "Bags", "Other"])
            location = st.text_input("📍 Location Found/Lost *", placeholder="e.g. Library, Block-B")
            status   = st.radio("📌 Status *", ["Lost", "Found"], horizontal=True)

        with col2:
            description = st.text_area("📝 Description *",
                                       placeholder="Describe the item in detail...",
                                       height=100)
            contact = st.text_input("📞 Contact Info *",
                                    placeholder="Phone number or email")
            uploaded_img = st.file_uploader(
                "📷 Upload Photo (optional)",
                type=["png", "jpg", "jpeg", "webp"],
                help="Upload a photo of the item. Max 2 MB."
            )

        submitted = st.form_submit_button("✅ Submit Item", use_container_width=True)

        if submitted:
            if not title or not description or not location or not contact:
                st.error("⚠️ Please fill in all required fields.")
            else:
                # Convert uploaded image to base64 string
                image_data = None
                if uploaded_img is not None:
                    img_bytes = uploaded_img.read()
                    if len(img_bytes) > 2 * 1024 * 1024:  # 2 MB limit
                        st.error("⚠️ Image too large! Please upload an image under 2 MB.")
                        st.stop()
                    image_data = base64.b64encode(img_bytes).decode("utf-8")

                new_id = add_item(title, description, category, location,
                                  contact, status, image_data)
                st.success(f"✅ Item **'{title}'** added successfully! (ID: `{new_id}`)")
                st.balloons()

# ═══════════════════════════════════════════════════════════════
#  PAGE 3 — VIEW ALL ITEMS
# ═══════════════════════════════════════════════════════════════
elif menu == "📋 View All Items":
    st.title("📋 All Reported Items")
    st.markdown("---")

    docs = get_all_items()
    if docs:
        st.markdown(f"**{len(docs)} item(s) found** — click any item to view full details.")
        st.markdown("")
        render_cards_grid(docs, cols_per_row=4)
    else:
        st.info("No items in the database yet. Add some using **➕ Add Item**.")

# ═══════════════════════════════════════════════════════════════
#  PAGE 4 — SEARCH & FILTER
# ═══════════════════════════════════════════════════════════════
elif menu == "🔎 Search & Filter":
    st.title("🔎 Search and Filter Items")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        cat_filter = st.selectbox("Filter by Category",
                                  ["All", "Electronics", "Clothing", "Accessories",
                                   "Documents", "Keys", "Bags", "Other"])
    with col2:
        loc_filter = st.text_input("Filter by Location", placeholder="e.g. Library")
    with col3:
        keyword    = st.text_input("🔑 Keyword Search", placeholder="Title or description keyword")

    if st.button("🔍 Search", use_container_width=True):
        results = search_items(cat_filter, loc_filter, keyword)
        if results:
            st.success(f"Found **{len(results)}** matching item(s).")
            render_cards_grid(results, cols_per_row=4)
        else:
            st.warning("No items match your search criteria.")

    st.markdown("---")
    st.caption("Tip: Leave filters blank to see all items.")

# ═══════════════════════════════════════════════════════════════
#  PAGE 5 — UPDATE STATUS
# ═══════════════════════════════════════════════════════════════
elif menu == "✏️ Update Status":
    st.title("✏️ Update Item Status")
    st.markdown("Change the status of an item from **Lost → Found** or vice-versa.")
    st.markdown("---")

    docs = get_all_items()
    if not docs:
        st.info("No items available to update.")
    else:
        options = {f"{d['title']}  [{d['status']}]  — ID: {str(d['_id'])}": str(d["_id"])
                   for d in docs}

        selected_label = st.selectbox("Select an item to update:", list(options.keys()))
        selected_id    = options[selected_label]

        current_doc  = next(d for d in docs if str(d["_id"]) == selected_id)
        current_status = current_doc["status"]

        st.info(f"**Current Status:** {current_status}")
        new_status = st.radio("Set new status:", ["Lost", "Found"],
                              index=0 if current_status == "Lost" else 1,
                              horizontal=True)

        if st.button("💾 Save Changes", use_container_width=True):
            if new_status == current_status:
                st.warning("Status is already set to that value.")
            else:
                update_status(selected_id, new_status)
                st.success(f"✅ Status updated to **{new_status}** successfully!")
                st.rerun()

# ═══════════════════════════════════════════════════════════════
#  PAGE 6 — DELETE ITEM
# ═══════════════════════════════════════════════════════════════
elif menu == "🗑️ Delete Item":
    st.title("🗑️ Delete an Item")
    st.markdown("⚠️ This action is **permanent** and cannot be undone.")
    st.markdown("---")

    docs = get_all_items()
    if not docs:
        st.info("No items available to delete.")
    else:
        options = {f"{d['title']}  [{d['status']}]  — ID: {str(d['_id'])}": str(d["_id"])
                   for d in docs}

        selected_label = st.selectbox("Select an item to delete:", list(options.keys()))
        selected_id    = options[selected_label]

        current_doc = next(d for d in docs if str(d["_id"]) == selected_id)

        st.markdown("#### Item Details")
        col1, col2 = st.columns([1, 2])
        with col1:
            if current_doc.get("image"):
                try:
                    img_bytes = base64.b64decode(current_doc["image"])
                    st.image(img_bytes, use_container_width=True)
                except Exception:
                    st.write("⚠️ Image not available")
            else:
                icon = CATEGORY_ICONS.get(current_doc.get("category", ""), "📦")
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#1e293b,#0f172a);
                     border-radius:12px; height:150px; display:flex;
                     align-items:center; justify-content:center; font-size:3rem;">
                    {icon}
                </div>
                """, unsafe_allow_html=True)
        with col2:
            st.write(f"**Title:** {current_doc.get('title','')}")
            st.write(f"**Category:** {current_doc.get('category','')}")
            st.write(f"**Location:** {current_doc.get('location','')}")
            st.write(f"**Status:** {current_doc.get('status','')}")
            st.write(f"**Contact:** {current_doc.get('contact','')}")
            st.write(f"**Date:** {current_doc.get('date','')}")

        confirm = st.checkbox("☑️ Yes, I want to permanently delete this item.")
        if st.button("🗑️ Delete Item", use_container_width=True):
            if confirm:
                delete_item(selected_id)
                st.success("✅ Item deleted successfully!")
                st.rerun()
            else:
                st.error("Please check the confirmation box before deleting.")
