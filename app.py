from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from models import db, User, Workout, Exercise, WorkoutExercise

app = Flask(__name__)

# --- Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key_123'

# --- Extensions ---
CORS(app)
bcrypt = Bcrypt(app)
db.init_app(app)
migrate = Migrate(app, db)

# --- Auth Routes ---

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    try:
        hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], password_hash=hashed)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return {"message": "User created", "id": new_user.id}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 422

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and bcrypt.check_password_hash(user.password_hash, data.get('password')):
        session['user_id'] = user.id
        return {"message": "Logged in!", "id": user.id}, 200
    return {"error": "Invalid credentials"}, 401

@app.route('/logout', methods=['DELETE'])
def logout():
    session.pop('user_id', None)
    return {}, 204

@app.route('/check_session', methods=['GET'])
def check_session():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return {"id": user.id, "username": user.username}, 200
    return {"error": "Not logged in"}, 401

# --- Task/Workout Routes ---

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return jsonify([{"id": w.id, "notes": w.notes} for w in workouts]), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)