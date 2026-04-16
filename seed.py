from app import app
from models import db, Exercise, Workout, WorkoutExercise
from datetime import date

def seed_database():
    
    with app.app_context():
        print("Starting database seed...")

        # 2. Delete existing data
       
        print("Clearing existing data...")
        db.session.query(WorkoutExercise).delete()
        db.session.query(Exercise).delete()
        db.session.query(Workout).delete()
        db.session.commit()

        # 3. Create Exercises
        print("Creating exercises...")
        e1 = Exercise(name="Pushups", category="Strength", equipment_needed=False)
        e2 = Exercise(name="Running", category="Cardio", equipment_needed=False)
        e3 = Exercise(name="Deadlift", category="Strength", equipment_needed=True)
        
        db.session.add_all([e1, e2, e3])
       
        db.session.commit()

        # 4. Create Workouts
        print("Creating workouts...")
        w1 = Workout(date=date.today(), duration_minutes=45, notes="Morning strength session")
        w2 = Workout(date=date.today(), duration_minutes=30, notes="Evening cardio burn")

        db.session.add_all([w1, w2])
        db.session.commit()

        # 5. Create Relationships (WorkoutExercise)
        print("Linking exercises to workouts...")
       
        we1 = WorkoutExercise(workout_id=w1.id, exercise_id=e1.id, reps=20, sets=3)
        we2 = WorkoutExercise(workout_id=w1.id, exercise_id=e3.id, reps=5, sets=5)
        
        db.session.add_all([we1, we2])
        db.session.commit()
        
        print(" Database successfully seeded!")

if __name__ == "__main__":
    seed_database()