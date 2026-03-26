from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Alex")

dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Luna", species="Cat", age=5)

# --- Tasks for Buddy ---
dog.add_task(Task(description="Morning walk",      due_time="07:00", category="exercise",  frequency="daily"))
dog.add_task(Task(description="Breakfast feeding", due_time="08:00", category="feeding",   frequency="daily"))

# --- Tasks for Luna ---
cat.add_task(Task(description="Medication",        due_time="09:30", category="health",    frequency="daily"))
cat.add_task(Task(description="Evening feeding",   due_time="18:00", category="feeding",   frequency="daily"))

# --- Register pets with owner ---
owner.add_pet(dog)
owner.add_pet(cat)

# --- Scheduler ---
scheduler = Scheduler(owner)

print(scheduler.daily_summary())
