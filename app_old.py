import os
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from sqlite3 import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

DATABASE = 'database.db'

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
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blood_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blood_type TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/donors', methods=['GET'])
def get_donors():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM donors')
    rows = cursor.fetchall()
    conn.close()
    donors = []
    for row in rows:
        donors.append({
            'id': row[0],
            'name': row[1],
            'blood_type': row[2],
            'phone': row[3],
            'email': row[4]
        })
    return jsonify(donors)

@app.route('/donors', methods=['POST'])
def add_donor():
    data = request.get_json()
    name = data.get('name')
    blood_type = data.get('blood_type')
    phone = data.get('phone')
    email = data.get('email')
    if not name or not blood_type:
        return jsonify({'error': 'Name and blood type are required'}), 400
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO donors (name, blood_type, phone, email) VALUES (?, ?, ?, ?)',
                   (name, blood_type, phone, email))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Donor added successfully'}), 201

@app.route('/inventory', methods=['GET'])
def get_inventory():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blood_inventory')
    rows = cursor.fetchall()
    conn.close()
    inventory = []
    for row in rows:
        inventory.append({
            'id': row[0],
            'blood_type': row[1],
            'quantity': row[2]
        })
    return jsonify(inventory)

@app.route('/inventory', methods=['POST'])
def add_inventory():
    data = request.get_json()
    blood_type = data.get('blood_type')
    quantity = data.get('quantity')
    if not blood_type or quantity is None:
        return jsonify({'error': 'Blood type and quantity are required'}), 400
    conn = create_connection()
    cursor = conn.cursor()
    # Check if blood type exists
    cursor.execute('SELECT id, quantity FROM blood_inventory WHERE blood_type = ?', (blood_type,))
    row = cursor.fetchone()
    if row:
        new_quantity = row[1] + quantity
        cursor.execute('UPDATE blood_inventory SET quantity = ? WHERE id = ?', (new_quantity, row[0]))
    else:
        cursor.execute('INSERT INTO blood_inventory (blood_type, quantity) VALUES (?, ?)', (blood_type, quantity))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Inventory updated successfully'}), 201

@app.route('/requests', methods=['GET'])
def get_requests():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM requests')
    rows = cursor.fetchall()
    conn.close()
    requests_list = []
    for row in rows:
        requests_list.append({
            'id': row[0],
            'patient_name': row[1],
            'blood_type': row[2],
            'quantity': row[3],
            'status': row[4]
        })
    return jsonify(requests_list)

@app.route('/requests', methods=['POST'])
def add_request():
    data = request.get_json()
    patient_name = data.get('patient_name')
    blood_type = data.get('blood_type')
    quantity = data.get('quantity')
    if not patient_name or not blood_type or quantity is None:
        return jsonify({'error': 'Patient name, blood type, and quantity are required'}), 400
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO requests (patient_name, blood_type, quantity, status) VALUES (?, ?, ?, ?)',
                   (patient_name, blood_type, quantity, 'pending'))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Request added successfully'}), 201

@app.route('/requests/<int:request_id>', methods=['PUT'])
def update_request_status(request_id):
    data = request.get_json()
    status = data.get('status')
    if status not in ['pending', 'approved', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE requests SET status = ? WHERE id = ?', (status, request_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Request status updated successfully'})

@app.route('/')
def home():
    return send_from_directory(os.path.join(os.getcwd(), 'frontend'), 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(os.path.join(os.getcwd(), 'frontend'), path)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='localhost', port=5000)
