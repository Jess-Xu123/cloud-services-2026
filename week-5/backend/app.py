import os
import json
import requests
import mysql.connector
import redis
from flask import Flask, jsonify, request


app = Flask(__name__)
def get_db_connection():
 return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'mysql-service'),
        user=os.getenv('DB_USER', 'appuser'),
        password=os.getenv('DB_PASSWORD', 'changeme'),
        database=os.getenv('DB_NAME', 'appdb'))

redis_client = redis.Redis(

        host=os.getenv('REDIS_HOST', 'cache'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True 
)
    

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task VARCHAR(255) NOT NULL,
                image_url VARCHAR(1024) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("SHOW COLUMNS FROM todos LIKE 'image_url'")
        if cur.fetchone() is None:
            cur.execute("ALTER TABLE todos ADD COLUMN image_url VARCHAR(1024) NULL")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")


def fetch_unsplash_image(query="todo"):
    access_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
    fallback_image = "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b"
    if not access_key:
        return fallback_image

    try:
        response = requests.get(
            "https://api.unsplash.com/photos/random",
            params={"query": query},
            headers={"Authorization": f"Client-ID {access_key}"},
            timeout=5,
        )
        response.raise_for_status()
        return response.json().get("urls", {}).get("regular") or fallback_image
    except (requests.RequestException, ValueError) as e:
        print(f"Unsplash API Error: {e}")
        return fallback_image

@app.get('/api/health')
def health():
    return {'status': 'ok'}
        

@app.get('/api/todos')
def get_todos():
    try:
        try:
            cached_data = redis_client.get('todo_list')
        except redis.RedisError as e:
            print(f"Redis cache read error: {e}")
            cached_data = None
        if cached_data:
            return jsonify(json.loads(cached_data))


        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, task, image_url, created_at FROM todos ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        for r in rows:
            r['created_at'] = str(r['created_at'])


        try:
            redis_client.setex('todo_list', 60, json.dumps(rows))
        except redis.RedisError as e:
            print(f"Redis cache write error: {e}")
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

        # 获取 Unsplash 图片
        image_url = fetch_unsplash_image(task)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO todos (task, image_url) VALUES (%s, %s)", (task, image_url))
        conn.commit()
        cur.close()
        conn.close()

        try:
            redis_client.delete('todo_list')
        except redis.RedisError as e:
            print(f"Redis cache invalidation error: {e}")

        return jsonify(message="Todo added successfully!"), 201
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
 init_db()
 # Dev-only fallback
 app.run(host='0.0.0.0', port=8000, debug=True)

 