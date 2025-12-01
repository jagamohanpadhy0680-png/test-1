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

# --- Callbacks ---
def select_block(block_id, block_label, block_type):
    st.session_state.block_choice = block_id
    st.session_state.block_label = block_label
    st.session_state.block_type_choice = block_type

def select_plant(plant_id, row_index, plant_name):
    st.session_state.plant_choice = plant_id
    st.session_state.row_index = row_index
    st.session_state.plant_name = plant_name

def back_to_blocks():
    st.session_state.block_choice = None
    st.session_state.plant_choice = None

def back_to_section():
    st.session_state.plant_choice = None

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

# --- View 1: Block selection ---
if st.session_state.block_choice is None:
    st.header("Blocks")
    cols = st.columns(len(custom_blocks))
    for i, block in enumerate(custom_blocks):
        cols[i].button(
            block["label"],
            key=f"block_{block['id']}",
            on_click=select_block,
            args=(block["id"], block["label"], block["type"])
        )

# --- View 2: Section view (plant grid) ---
elif st.session_state.plant_choice is None:
    st.button("🔙 Back to Blocks", on_click=back_to_blocks)

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
            row_cols[p].button(
                f"🌱 {plant_name}",
                key=plant_id,
                on_click=select_plant,
                args=(plant_id, r, plant_name)
            )

# --- View 3: Plant details (flowering + harvest only) ---
else:
    st.button("🔙 Back to Section View", on_click=back_to_section)

    st.subheader(f"Details for {st.session_state.plant_choice}")
    plant_data = df[df["plant_id"] == st.session_state.plant_choice]

    with st.form("plant_form"):
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
                "flowering_date": flowering_date,
                "harvest_date": harvest_date
            }
            df = df[df["plant_id"] != st.session_state.plant_choice]
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"Plant {st.session_state.plant_choice} updated! Harvest expected on {harvest_date}")

# --- Reminder system ---
today = datetime.date.today()
if "harvest_date" in df.columns:
    df["harvest_date_str"] = pd.to_datetime(df["harvest_date"], errors="coerce").dt.date.astype(str)
    due_harvest = df[df["harvest_date_str"] == str(today)]
    if not due_harvest.empty:
        st.success(f"Reminder: {len(due_harvest)} plants are ready for harvest today!")
