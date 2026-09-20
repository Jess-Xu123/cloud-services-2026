import os
import mysql.connector
from flask import Flask, jsonify, request


app = Flask(__name__)
def get_db_connection():
 return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'mysql-service'),
        user=os.getenv('DB_USER', 'appuser'),
        password=os.getenv('DB_PASSWORD', 'changeme'),
        database=os.getenv('DB_NAME', 'appdb')
    )

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")


@app.before_request
def ensure_db_schema():
    init_db()


@app.get('/api/health')
def health():
 return {'status': 'ok'}

@app.get('/api/time')
def get_time():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW()")
        row = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify(time=str(row[0]))
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.get('/api/todos')
def get_todos():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, task, created_at FROM todos ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        for r in rows:
            r['created_at'] = str(r['created_at'])
        return jsonify(rows)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.post('/api/todos')
def add_todo():
    try:
        data = request.get_json() or {}
        task = data.get('task')
        if not task:
            return jsonify(error="Task title is required"), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO todos (task) VALUES (%s)", (task,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(message="Todo added successfully!"), 201
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
 init_db()
 # Dev-only fallback
 app.run(host='0.0.0.0', port=8000, debug=True)

 