from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Alex")

dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Luna", species="Cat", age=5)

# --- Buddy's tasks — two intentionally at 08:00 (same-pet conflict) ---
dog.add_task(Task(description="Morning walk",      due_time="07:00", category="exercise", frequency="daily"))
dog.add_task(Task(description="Breakfast feeding", due_time="08:00", category="feeding",  frequency="daily"))
dog.add_task(Task(description="Grooming",          due_time="08:00", category="grooming", frequency="weekly"))  # conflicts with Breakfast feeding

# --- Luna's tasks — Medication at 07:00 (cross-pet conflict with Buddy's Morning walk) ---
cat.add_task(Task(description="Medication",        due_time="07:00", category="health",   frequency="daily"))   # same time as Morning walk
cat.add_task(Task(description="Evening feeding",   due_time="18:00", category="feeding",  frequency="daily"))

# --- Register pets ---
owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler(owner)

# --- Daily summary ---
print(scheduler.daily_summary())

# --- Conflict detection ---
print("\n=== Conflict Report ===")
conflicts = scheduler.get_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts detected.")
