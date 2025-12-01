import streamlit as st
import pandas as pd
import datetime
import string

DATA_FILE = "data.csv"

# Load or initialize data
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "plant_id", "block_type", "block_id", "row", "position",
        "planting_date", "fertilizer_date", "irrigation_cycle", "notes",
        "flowering_date", "harvest_date"
    ])
    df.to_csv(DATA_FILE, index=False)

st.title("🍌 Banana Field Management Tool")

# --- Define custom block layout ---
custom_blocks = [
    {"label": "S1", "id": 1, "type": "section"},
    {"label": "R1", "id": 2, "type": "road"},
    {"label": "S2", "id": 3, "type": "section"},
    {"label": "S3", "id": 4, "type": "section"},
    {"label": "R2", "id": 5, "type": "road"},
    {"label": "S4", "id": 6, "type": "section"},
    {"label": "S5", "id": 7, "type": "section"},
    {"label": "R3", "id": 8, "type": "road"},
    {"label": "S6", "id": 9, "type": "section"},
    {"label": "S7", "id": 10, "type": "section"},
    {"label": "R4", "id": 11, "type": "road"},
    {"label": "S8", "id": 12, "type": "section"},
]

# --- Session state setup ---
if "block_choice" not in st.session_state:
    st.session_state.block_choice = None
if "plant_choice" not in st.session_state:
    st.session_state.plant_choice = None
if "row_index" not in st.session_state:
    st.session_state.row_index = None
if "plant_name" not in st.session_state:
    st.session_state.plant_name = None

# --- Level 1: Show blocks ---
if not st.session_state.block_choice:
    st.header("Blocks")
    cols = st.columns(len(custom_blocks))
    for i, block in enumerate(custom_blocks):
        if cols[i].button(block["label"], key=f"block_{block['id']}"):
            st.session_state.block_choice = block["id"]
            st.session_state.block_label = block["label"]
            st.session_state.block_type_choice = block["type"]

# --- Plant arrangement rules ---
def get_plants_per_row(block_id):
    if block_id in [1, 3, 4, 6, 7, 9, 10, 12]:
        return 8
    elif block_id in [2, 5, 11]:
        return 3
    elif block_id == 8:
        return 2
    else:
        return 0

# --- Level 2: Section view (grid of plants) ---
if st.session_state.block_choice and not st.session_state.plant_choice:
    st.subheader(f"Plants in {st.session_state.block_label}")
    rows = 22
    plants_per_row = get_plants_per_row(st.session_state.block_choice)
    row_letters = list(string.ascii_uppercase)[:rows]

    for r in range(rows):
        row_cols = st.columns(plants_per_row)
        row_letter = row_letters[r]
        for p in range(plants_per_row):
            plant_name = f"{row_letter}{p+1}"
            plant_id = f"{st.session_state.block_label}-Row{r+1}-{plant_name}"
            if row_cols[p].button(f"🌱 {plant_name}", key=plant_id):
                st.session_state.plant_choice = plant_id
                st.session_state.row_index = r
                st.session_state.plant_name = plant_name

# --- Level 3: Plant view (only selected plant details) ---
if st.session_state.plant_choice:
    st.subheader(f"Details for {st.session_state.plant_choice}")
    plant_data = df[df["plant_id"] == st.session_state.plant_choice]

    with st.form("plant_form"):
        planting_date = st.date_input(
            "Planting Date",
            value=pd.to_datetime(plant_data["planting_date"].iloc[0]).date()
            if not plant_data.empty and pd.notnull(plant_data["planting_date"].iloc[0])
            else datetime.date.today()
        )
        fertilizer_date = st.date_input(
            "Next Fertilizer Date",
            value=pd.to_datetime(plant_data["fertilizer_date"].iloc[0]).date()
            if not plant_data.empty and pd.notnull(plant_data["fertilizer_date"].iloc[0])
            else datetime.date.today()
        )
        irrigation_cycle = st.text_input(
            "Irrigation Cycle",
            value=plant_data["irrigation_cycle"].iloc[0] if not plant_data.empty else ""
        )
        notes = st.text_area(
            "Notes",
            value=plant_data["notes"].iloc[0] if not plant_data.empty else ""
        )
        flowering_date = st.date_input(
            "Flowering Date",
            value=pd.to_datetime(plant_data["flowering_date"].iloc[0]).date()
            if not plant_data.empty and pd.notnull(plant_data["flowering_date"].iloc[0])
            else datetime.date.today()
        )
        harvest_date = flowering_date + datetime.timedelta(days=90)
        st.info(f"Expected Harvest Date: {harvest_date}")

        submitted = st.form_submit_button("Save Plant")
        if submitted:
            new_entry = {
                "plant_id": st.session_state.plant_choice,
                "block_type": st.session_state.block_type_choice,
                "block_id": st.session_state.block_choice,
                "row": st.session_state.row_index + 1,
                "position": st.session_state.plant_name,
                "planting_date": planting_date,
                "fertilizer_date": fertilizer_date,
                "irrigation_cycle": irrigation_cycle,
                "notes": notes,
                "flowering_date": flowering_date,
                "harvest_date": harvest_date
            }
            df = df[df["plant_id"] != st.session_state.plant_choice]
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"Plant {st.session_state.plant_choice} updated! Harvest expected on {harvest_date}")

    if st.button("🔙 Back to Section View"):
        st.session_state.plant_choice = None

# --- Reminder system ---
today = datetime.date.today()
if "fertilizer_date" in df.columns:
    df["fertilizer_date_str"] = pd.to_datetime(df["fertilizer_date"], errors="coerce").dt.date.astype(str)
    due_fertilizer = df[df["fertilizer_date_str"] == str(today)]
    if not due_fertilizer.empty:
        st.warning(f"Reminder: {len(due_fertilizer)} plants need fertilizer today!")

if "harvest_date" in df.columns:
    df["harvest_date_str"] = pd.to_datetime(df["harvest_date"], errors="coerce").dt.date.astype(str)
    due_harvest = df[df["harvest_date_str"] == str(today)]
    if not due_harvest.empty:
        st.success(f"Reminder: {len(due_harvest)} plants are ready for harvest today!")
