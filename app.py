import streamlit as st
import pandas as pd
import datetime

DATA_FILE = "data.csv"

# Load or initialize data
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "plant_id", "block_type", "block_id", "row", "position",
        "planting_date", "fertilizer_date", "irrigation_cycle", "notes"
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

# --- Level 1: Show blocks in custom order ---
st.header("Blocks")
cols = st.columns(len(custom_blocks))
block_choice = None
block_label = None
block_type_choice = None

for i, block in enumerate(custom_blocks):
    if cols[i].button(block["label"], key=f"block_{block['id']}"):
        block_choice = block["id"]
        block_label = block["label"]
        block_type_choice = block["type"]

# --- Define plant arrangement rules ---
def get_plants_per_row(block_id):
    if block_id in [1, 3, 4, 6, 7, 9, 10, 12]:  # sections
        return 8
    elif block_id in [2, 5, 11]:  # roads R1, R2, R4
        return 3
    elif block_id == 8:  # road R3
        return 2
    else:
        return 0

# --- Level 2: Show plants in chosen block ---
if block_choice:
    st.subheader(f"Plants in {block_label}")
    block_plants = df[df["block_id"] == block_choice]

    rows = 22
    plants_per_row = get_plants_per_row(block_choice)
    plant_choice = None

    for r in range(1, rows + 1):
        row_cols = st.columns(plants_per_row)
        for p in range(plants_per_row):
            plant_id = f"{block_label}-R{r}-P{p+1}"
            if row_cols[p].button("🌱", key=plant_id):
                plant_choice = plant_id

    # --- Level 3: Plant details form ---
    if plant_choice:
        st.subheader(f"Details for {plant_choice}")
        plant_data = df[df["plant_id"] == plant_choice]

        with st.form("plant_form"):
            planting_date = st.date_input(
                "Planting Date",
                value=pd.to_datetime(
                    plant_data["planting_date"].iloc[0]
                ).date() if not plant_data.empty else datetime.date.today()
            )
            fertilizer_date = st.date_input(
                "Next Fertilizer Date",
                value=pd.to_datetime(
                    plant_data["fertilizer_date"].iloc[0]
                ).date() if not plant_data.empty else datetime.date.today()
            )
            irrigation_cycle = st.text_input(
                "Irrigation Cycle",
                value=plant_data["irrigation_cycle"].iloc[0] if not plant_data.empty else ""
            )
            notes = st.text_area(
                "Notes",
                value=plant_data["notes"].iloc[0] if not plant_data.empty else ""
            )
            submitted = st.form_submit_button("Save Plant")

            if submitted:
                new_entry = {
                    "plant_id": plant_choice,
                    "block_type": block_type_choice,
                    "block_id": block_choice,
                    "row": int(plant_choice.split("-")[1][1:]),
                    "position": int(plant_choice.split("-")[2][1:]),
                    "planting_date": planting_date,
                    "fertilizer_date": fertilizer_date,
                    "irrigation_cycle": irrigation_cycle,
                    "notes": notes
                }
                df = df[df["plant_id"] != plant_choice]
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success(f"Plant {plant_choice} updated!")

# --- Reminder system ---
today = datetime.date.today()
if "fertilizer_date" in df.columns:
    df["fertilizer_date_str"] = pd.to_datetime(df["fertilizer_date"], errors="coerce").dt.date.astype(str)
    due_fertilizer = df[df["fertilizer_date_str"] == str(today)]
    if not due_fertilizer.empty:
        st.warning(f"Reminder: {len(due_fertilizer)} plants need fertilizer today!")
