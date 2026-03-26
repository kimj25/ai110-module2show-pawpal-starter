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
    # Keep pet_lookup in sync after adding a new pet
    st.session_state.scheduler.pet_lookup[pet_name.lower()] = new_pet
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
        try:
            st.session_state.scheduler.add_task_to_pet(target_pet, new_task)
            st.success(f"Task '{task_title}' added to {target_pet}.")
        except ValueError as e:
            st.error(f"Could not add task: {e}")
else:
    st.info("Add a pet first before scheduling tasks.")

st.divider()

# --- Mark Task Complete ---
st.subheader("Mark Task Complete")

if st.session_state.scheduler:
    pending = st.session_state.scheduler.get_pending_tasks()
    if pending:
        complete_options = [f"{pet} — {task.description} ({task.due_time.strftime('%H:%M')})" for pet, task in pending]
        selected = st.selectbox("Select task to mark complete", complete_options)
        if st.button("Mark Complete"):
            idx = complete_options.index(selected)
            pet_name_sel, task_sel = pending[idx]
            ok = st.session_state.scheduler.complete_task(pet_name_sel, task_sel.description)
            if ok:
                freq_note = " Next occurrence scheduled automatically." if task_sel.frequency.value != "once" else ""
                st.success(f"'{task_sel.description}' marked complete for {pet_name_sel}.{freq_note}")
            else:
                st.error("Could not mark task complete. Please try again.")
    else:
        st.info("No pending tasks to mark complete.")
else:
    st.info("Add a pet and tasks first.")

st.divider()

# --- Daily Schedule ---
st.subheader("Daily Schedule")

if st.button("Generate Schedule"):
    if st.session_state.scheduler is None:
        st.warning("No owner or pets set up yet.")
    else:
        scheduler = st.session_state.scheduler

        # --- Conflict warnings ---
        conflicts = scheduler.get_conflicts()
        if conflicts:
            st.markdown("**Scheduling Issues Found**")
            for msg in conflicts:
                if msg.startswith("CONFLICT"):
                    # Parse: CONFLICT [date time] pet_name has overlapping tasks: "A" & "B"
                    body = msg[len("CONFLICT"):].strip()
                    st.error(
                        f"Same-pet overlap: {body}\n\n"
                        "Your pet can't do two things at once — try shifting one task by 15–30 minutes."
                    )
                elif msg.startswith("WARNING"):
                    body = msg[len("WARNING"):].strip()
                    st.warning(
                        f"You're double-booked: {body}\n\n"
                        "You can only be in one place at a time — consider staggering these tasks."
                    )
        else:
            st.success("No scheduling conflicts — your day looks great!")

        # --- Pending tasks table ---
        pending = scheduler.get_pending_tasks()
        if pending:
            st.markdown(f"**Upcoming tasks ({len(pending)} pending)**")
            rows = [
                {
                    "Time": task.due_time.strftime("%H:%M"),
                    "Pet": pet_name,
                    "Task": task.description,
                    "Category": task.category.capitalize(),
                    "Frequency": task.frequency.value.capitalize(),
                    "Due Date": task.due_date.isoformat(),
                }
                for pet_name, task in pending
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.success("All tasks are complete — nothing left to do today!")

        # --- Per-pet summaries ---
        st.markdown("**Pet summaries**")
        for pet in st.session_state.owner.pets:
            pet_pending = [t for t in pet.tasks if not t.is_completed]
            with st.expander(f"{pet.name} ({pet.species}, age {pet.age}) — {len(pet_pending)} pending"):
                if pet_pending:
                    for task in scheduler.sort_by_time(pet_pending):
                        st.markdown(
                            f"- **{task.due_time.strftime('%H:%M')}** &nbsp; {task.description} "
                            f"&nbsp; `{task.category}` &nbsp; _{task.frequency.value}_"
                        )
                else:
                    st.success("All done for today!")
