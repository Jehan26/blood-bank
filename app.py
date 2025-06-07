import os
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from sqlite3 import Error
from flask_cors import CORS

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)  # Enable CORS for frontend-backend communication

DATABASE = 'blood_bank.db'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE, check_same_thread=False)
    except Error as e:
        print(e)
    return conn

def init_db():
    conn = create_connection()
    cursor = conn.cursor()
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Donor (
            donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            blood_group TEXT NOT NULL,
            contact TEXT,
            last_donation_date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Hospital (
            hospital_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            contact TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Request (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospital_id INTEGER NOT NULL,
            blood_group TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            request_date TEXT,
            status TEXT,
            FOREIGN KEY (hospital_id) REFERENCES Hospital(hospital_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Donation (
            donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id INTEGER NOT NULL,
            hospital_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (donor_id) REFERENCES Donor(donor_id),
            FOREIGN KEY (hospital_id) REFERENCES Hospital(hospital_id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/donors', methods=['GET'])
def get_donors():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Donor')
    rows = cursor.fetchall()
    conn.close()
    donors = []
    for row in rows:
        donors.append({
            'donor_id': row[0],
            'name': row[1],
            'age': row[2],
            'gender': row[3],
            'blood_group': row[4],
            'contact': row[5],
            'last_donation_date': row[6]
        })
    return jsonify(donors)

@app.route('/donors', methods=['POST'])
def add_donor():
    data = request.get_json(force=True)
    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')
    blood_group = data.get('blood_group')
    contact = data.get('contact')
    last_donation_date = data.get('last_donation_date')
    if not name or not blood_group:
        return jsonify({'error': 'Name and blood group are required'}), 400
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Donor (name, age, gender, blood_group, contact, last_donation_date) VALUES (?, ?, ?, ?, ?, ?)',
                   (name, age, gender, blood_group, contact, last_donation_date))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Donor added successfully'}), 201

@app.route('/hospitals', methods=['GET'])
def get_hospitals():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Hospital')
    rows = cursor.fetchall()
    conn.close()
    hospitals = []
    for row in rows:
        hospitals.append({
            'hospital_id': row[0],
            'name': row[1],
            'address': row[2],
            'contact': row[3]
        })
    return jsonify(hospitals)

@app.route('/hospitals', methods=['POST'])
def add_hospital():
    data = request.get_json(force=True)
    name = data.get('name')
    address = data.get('address')
    contact = data.get('contact')
    if not name:
        return jsonify({'error': 'Hospital name is required'}), 400
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Hospital (name, address, contact) VALUES (?, ?, ?)', (name, address, contact))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Hospital added successfully'}), 201

@app.route('/requests', methods=['GET'])
def get_requests():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Request')
    rows = cursor.fetchall()
    conn.close()
    requests_list = []
    for row in rows:
        requests_list.append({
            'request_id': row[0],
            'hospital_id': row[1],
            'blood_group': row[2],
            'quantity': row[3],
            'request_date': row[4],
            'status': row[5]
        })
    return jsonify(requests_list)

@app.route('/requests', methods=['POST'])
def add_request():
    data = request.get_json(force=True)
    hospital_id = data.get('hospital_id')
    blood_group = data.get('blood_group')
    quantity = data.get('quantity')
    request_date = data.get('request_date')
    if not hospital_id or not blood_group or quantity is None:
        return jsonify({'error': 'Hospital ID, blood group, and quantity are required'}), 400
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Request (hospital_id, blood_group, quantity, request_date, status) VALUES (?, ?, ?, ?, ?)',
                   (hospital_id, blood_group, quantity, request_date, 'pending'))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Request added successfully'}), 201

@app.route('/donations', methods=['GET'])
def get_donations():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Donation')
    rows = cursor.fetchall()
    conn.close()
    donations = []
    for row in rows:
        donations.append({
            'donation_id': row[0],
            'donor_id': row[1],
            'hospital_id': row[2],
            'date': row[3],
            'quantity': row[4]
        })
    return jsonify(donations)

@app.route('/donations', methods=['POST'])
def add_donation():
    data = request.get_json(force=True)
    donor_id = data.get('donor_id')
    hospital_id = data.get('hospital_id')
    date = data.get('date')
    quantity = data.get('quantity')
    if not donor_id or not hospital_id or not date or quantity is None:
        return jsonify({'error': 'Donor ID, hospital ID, date, and quantity are required'}), 400
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Donation (donor_id, hospital_id, date, quantity) VALUES (?, ?, ?, ?)',
                   (donor_id, hospital_id, date, quantity))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Donation added successfully'}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='localhost', port=5000)
