from app import app, db, User, Task, bcrypt

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Create one test user
    h_password = bcrypt.generate_password_hash('1234').decode('utf-8')
    u1 = User(username="coder123", password_hash=h_password)
    db.session.add(u1)
    db.session.commit()

    # Add 5 sample tasks
    for i in range(1, 6):
        t = Task(title=f"Sample Task {i}", user_id=u1.id)
        db.session.add(t)
    
    db.session.commit()
    print("Database seeded! Username: coder123, Password: 1234")