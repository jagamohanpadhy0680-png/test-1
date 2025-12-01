# --- Level 1: Show blocks if none selected ---
if st.session_state.block_choice is None:
    st.header("Blocks")
    cols = st.columns(len(custom_blocks))
    for i, block in enumerate(custom_blocks):
        if cols[i].button(block["label"], key=f"block_{block['id']}"):
            st.session_state.block_choice = block["id"]
            st.session_state.block_label = block["label"]
            st.session_state.block_type_choice = block["type"]

# --- Level 2: Show plants if block selected but no plant yet ---
elif st.session_state.plant_choice is None:
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

# --- Level 3: Show plant details if plant selected ---
else:
    st.subheader(f"Details for {st.session_state.plant_choice}")
    plant_data = df[df["plant_id"] == st.session_state.plant_choice]

    with st.form("plant_form"):
        planting_date = st.date_input("Planting Date", value=(
            pd.to_datetime(plant_data["planting_date"].iloc[0]).date()
            if not plant_data.empty and pd.notnull(plant_data["planting_date"].iloc[0])
            else datetime.date.today()
        ))
        fertilizer_date = st.date_input("Next Fertilizer Date", value=(
            pd.to_datetime(plant_data["fertilizer_date"].iloc[0]).date()
            if not plant_data.empty and pd.notnull(plant_data["fertilizer_date"].iloc[0])
            else datetime.date.today()
        ))
        irrigation_cycle = st.text_input("Irrigation Cycle",
            value=plant_data["irrigation_cycle"].iloc[0] if not plant_data.empty else "")
        notes = st.text_area("Notes",
            value=plant_data["notes"].iloc[0] if not plant_data.empty else "")
        flowering_date = st.date_input("Flowering Date", value=(
            pd.to_datetime(plant_data["flowering_date"].iloc[0]).date()
            if not plant_data.empty and pd.notnull(plant_data["flowering_date"].iloc[0])
            else datetime.date.today()
        ))
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
