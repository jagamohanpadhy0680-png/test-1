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

# --- Define mapping for roads ---
road_map = {2: "R1", 5: "R2", 8: "R3", 11: "R4"}

# --- Level 1: Show all blocks in a single row ---
st.header("Blocks (Sections + Roads)")
cols = st.columns(12)
block_choice = None
block_label = None

for i in range(12):
    if i+1 in road_map:
        label = road_map[i+1]   # R1, R2, R3, R4
        block_type = "road"
    else:
        label = f"S{i+1}"       # S1, S3, S4, etc.
        block_type = "section"

    if cols[i].button(label, key=f"block_{i+1}"):
        block_choice = i+1
        block_label = label
        block_type_choice = block_type

# --- Define plant arrangement rules ---
def get_plants_per_row(block_num):
    if block_num in [1, 3, 4, 6, 7, 9, 10, 12]:  # main sections
        return 8
    elif block_num in [2, 5, 11]:  # roads R1, R2, R4
        return 3
    elif block_num == 8:  # road R3
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
                # Remove old record if exists
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