from flask import Flask, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('SLAVE_DB_HOST', 'postgres-slave'),
        port=os.getenv('SLAVE_DB_PORT', 5432),
        dbname=os.getenv('DB_NAME', 'postgres'),
        user=os.getenv('DB_USER', 'admin'),
        password=os.getenv('DB_PASSWORD', 'password')
    )
    return conn


@app.route('/health/<app_name>', methods=['GET'])
def get_health(app_name):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM health_checks WHERE app_name = %s', (app_name,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
