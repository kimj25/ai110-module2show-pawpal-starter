import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.divider()

# --- Session state init ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# --- Add a Pet ---
st.subheader("Add a Pet")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add Pet"):
    if st.session_state.owner is None:
        st.session_state.owner = Owner(name=owner_name)
        st.session_state.scheduler = Scheduler(st.session_state.owner)
    new_pet = Pet(name=pet_name, species=species, age=age)
    st.session_state.owner.add_pet(new_pet)
    st.success(f"Added {pet_name} ({species}) to {owner_name}'s pets.")

if st.session_state.owner:
    pet_names = [p.name for p in st.session_state.owner.pets]
    st.caption(f"Current pets: {', '.join(pet_names) if pet_names else 'none'}")

st.divider()

# --- Schedule a Task ---
st.subheader("Schedule a Task")
st.caption("Select a pet and fill in task details.")

if st.session_state.owner and st.session_state.owner.pets:
    pet_options = [p.name for p in st.session_state.owner.pets]
    target_pet = st.selectbox("Assign to pet", pet_options)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        due_time = st.text_input("Due time (HH:MM)", value="08:00")
    with col3:
        category = st.selectbox("Category", ["exercise", "feeding", "health", "hygiene", "other"])

    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

    if st.button("Add Task"):
        new_task = Task(
            description=task_title,
            due_time=due_time,
            category=category,
            frequency=frequency,
        )
        st.session_state.scheduler.add_task_to_pet(target_pet, new_task)
        st.success(f"Task '{task_title}' added to {target_pet}.")
else:
    st.info("Add a pet first before scheduling tasks.")

st.divider()

# --- Generate Schedule ---
st.subheader("Daily Schedule")

if st.button("Generate Schedule"):
    if st.session_state.scheduler is None:
        st.warning("No owner or pets set up yet.")
    else:
        summary = st.session_state.scheduler.daily_summary()
        st.text(summary)
