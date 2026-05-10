from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)

# ==========================================
# APP CONFIGURATION
# ==========================================

app.secret_key = "hospital-secret-key"

# MYSQL DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/hospital_hci'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# FILE UPLOADS
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

# ==========================================
# DATABASE MODELS
# ==========================================

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(300),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        nullable=False
    )

    department = db.Column(
        db.String(100),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)

    patient = db.Column(
        db.String(150),
        nullable=False
    )

    doctor = db.Column(
        db.String(150),
        nullable=False
    )

    appointment_date = db.Column(
        db.String(100),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default='Pending'
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)

    patient = db.Column(
        db.String(150),
        nullable=False
    )

    amount = db.Column(
        db.String(50),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default='Completed'
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)

    patient_name = db.Column(
        db.String(150),
        nullable=False
    )

    filename = db.Column(
        db.String(300),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# ==========================================
# CREATE DATABASE TABLES
# ==========================================

with app.app_context():
    db.create_all()

# ==========================================
# HOME PAGE
# ==========================================

@app.route('/')
def home():
    return render_template('index.html')

# ==========================================
# LOGIN
# ==========================================

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login-user', methods=['POST'])
def login_user():

    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    if user:

        if check_password_hash(user.password, password):

            session['user_id'] = user.id
            session['username'] = user.fullname
            session['role'] = user.role

            flash('Login successful')

            # ROLE REDIRECTION
            if user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))

            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))

            else:
                return redirect(url_for('patient_dashboard'))

    flash('Invalid email or password')
    return redirect(url_for('login'))

# ==========================================
# REGISTER
# ==========================================

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register-user', methods=['POST'])
def register_user():

    fullname = request.form['fullname']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
    department = request.form.get('department')

    # CHECK EXISTING USER
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        flash('Email already exists')
        return redirect(url_for('register'))

    # HASH PASSWORD
    hashed_password = generate_password_hash(password)

    # CREATE USER
    user = User(
        fullname=fullname,
        email=email,
        password=hashed_password,
        role=role,
        department=department
    )

    db.session.add(user)
    db.session.commit()

    flash('Registration successful')

    return redirect(url_for('login'))

# ==========================================
# PATIENT DASHBOARD
# ==========================================

@app.route('/patient-dashboard')
def patient_dashboard():

    appointments = Appointment.query.all()

    payments = Payment.query.all()

    records = MedicalRecord.query.all()

    return render_template(
        'patient_dashboard.html',
        appointments=appointments,
        payments=payments,
        records=records
    )

# ==========================================
# DOCTOR DASHBOARD
# ==========================================

@app.route('/doctor-dashboard')
def doctor_dashboard():

    appointments = Appointment.query.all()

    return render_template(
        'doctor_dashboard.html',
        appointments=appointments
    )

# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route('/admin-dashboard')
def admin_dashboard():

    users = User.query.all()

    appointments = Appointment.query.all()

    payments = Payment.query.all()

    return render_template(
        'admin_dashboard.html',
        users=users,
        appointments=appointments,
        payments=payments
    )

# ==========================================
# BOOK APPOINTMENT
# ==========================================

@app.route('/book-appointment', methods=['POST'])
def book_appointment():

    patient = request.form['patient']

    doctor = request.form['doctor']

    appointment_date = request.form['appointment_date']

    appointment = Appointment(
        patient=patient,
        doctor=doctor,
        appointment_date=appointment_date,
        status='Booked'
    )

    db.session.add(appointment)

    db.session.commit()

    flash('Appointment booked successfully')

    return redirect(url_for('patient_dashboard'))

# ==========================================
# PAYMENT SYSTEM
# ==========================================

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/make-payment', methods=['POST'])
def make_payment():

    patient = request.form['patient']

    amount = request.form['amount']

    payment = Payment(
        patient=patient,
        amount=amount,
        status='Completed'
    )

    db.session.add(payment)

    db.session.commit()

    flash('Payment successful')

    return redirect(url_for('patient_dashboard'))

# ==========================================
# MEDICAL RECORD UPLOAD
# ==========================================

@app.route('/upload-record', methods=['POST'])
def upload_record():

    patient_name = request.form['patient_name']

    file = request.files['record']

    if file:

        # CREATE FOLDER IF MISSING
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )

        file.save(filepath)

        record = MedicalRecord(
            patient_name=patient_name,
            filename=filename
        )

        db.session.add(record)

        db.session.commit()

        flash('Medical record uploaded successfully')

    return redirect(url_for('patient_dashboard'))

# ==========================================
# LOGOUT
# ==========================================

@app.route('/logout')
def logout():

    session.clear()

    flash('Logged out successfully')

    return redirect(url_for('home'))

# ==========================================
# RUN APP
# ==========================================

if __name__ == '__main__':
    app.run(debug=True)