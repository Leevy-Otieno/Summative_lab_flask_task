from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, CheckConstraint
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

# Naming convention for database constraints
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

db = SQLAlchemy(metadata=metadata)

class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer)
    notes = db.Column(db.Text)

    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='check_duration_positive'),
    )

    # Relationships
    workout_exercises = db.relationship('WorkoutExercise', back_populates='workout', cascade="all, delete-orphan")
    exercises = association_proxy('workout_exercises', 'exercise')

    @validates('notes')
    def validate_notes(self, key, notes):
        if notes and len(notes) < 5:
            raise ValueError("Notes must be at least 5 characters long.")
        return notes


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, default=False)

    __table_args__ = (
        CheckConstraint('length(name) > 0', name='check_name_not_empty'),
    )

    # Relationships
    workout_exercises = db.relationship('WorkoutExercise', back_populates='exercise', cascade="all, delete-orphan")
    workouts = association_proxy('workout_exercises', 'workout')

    @validates('category')
    def validate_category(self, key, category):
        valid_categories = ['Cardio', 'Strength', 'Flexibility', 'Balance']
        if category not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return category


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # Relationships
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')
