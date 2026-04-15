from flask import Flask, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# --- Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key_123' # Used for sessions

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- Auth Routes ---

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    # Hash the password before saving
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password_hash=hashed)
    db.session.add(new_user)
    db.session.commit()
    session['user_id'] = new_user.id
    return {"message": "User created"}, 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        session['user_id'] = user.id
        return {"message": "Logged in!"}, 200
    return {"error": "Unauthorized"}, 401

@app.route('/logout', methods=['DELETE'])
def logout():
    session.pop('user_id', None)
    return {}, 204

# --- Resource Routes (Tasks) ---

@app.route('/tasks', methods=['GET', 'POST'])
def handle_tasks():
    user_id = session.get('user_id')
    if not user_id:
        return {"error": "Please log in"}, 401

    if request.method == 'GET':
        # Pagination: get ?page=1 from URL
        page = request.args.get('page', 1, type=int)
        tasks_data = Task.query.filter_by(user_id=user_id).paginate(page=page, per_page=5)
        return jsonify([{"id": t.id, "title": t.title} for t in tasks_data.items])

    if request.method == 'POST':
        data = request.get_json()
        new_task = Task(title=data['title'], user_id=user_id)
        db.session.add(new_task)
        db.session.commit()
        return {"id": new_task.id, "title": new_task.title}, 201

@app.route('/tasks/<int:id>', methods=['PATCH', 'DELETE'])
def update_task(id):
    user_id = session.get('user_id')
    task = Task.query.filter_by(id=id, user_id=user_id).first()
    
    if not task:
        return {"error": "Task not found"}, 404

    if request.method == 'PATCH':
        data = request.get_json()
        task.title = data.get('title', task.title)
        db.session.commit()
        return {"message": "Updated"}

    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return {}, 204

if __name__ == '__main__':
    app.run(port=5555, debug=True)