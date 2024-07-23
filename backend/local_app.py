from flask import Flask, jsonify, request
import requests
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# URL of the model API hosted on the VM
MODEL_API_URL = 'http://213.180.0.67:20037/api/query'

# Database connection configuration
DB_CONFIG = {
    'user': 'root',
    'password': 'abcd1234',
    'host': 'localhost',
    'database': 'Hackathon'
}

def get_table_context(table_name):
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    rows = cursor.fetchall()
    context = f"CREATE TABLE {table_name} ("
    context += ', '.join([f"{row[0]} {row[1]}" for row in rows])
    context += ");"
    cursor.close()
    connection.close()
    return context

# @app.route('/generate_sql', methods=['POST'])
# def generate_sql():
#     try:
#         natural_language_query = request.json.get('query', '')
#         context = request.json.get('context', '')
#         response = requests.post(MODEL_API_URL, json={'query': natural_language_query, 'context': context})
#         if response.status_code == 200:
#             sql_query = response.json().get('sql_query', 'No SQL query generated')
#             connection = mysql.connector.connect(**DB_CONFIG)
#             cursor = connection.cursor()
#             cursor.execute(sql_query)
#             results = cursor.fetchall()
#             cursor.close()
#             connection.close()
#             return jsonify({'sql_query': sql_query, 'results': results})
#         else:
#             return jsonify({'error': 'Error in generating SQL query'}), 500
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@app.route('/generate_sql', methods=['POST'])
def generate_sql():
    try:
        natural_language_query = request.json.get('query', '')
        context = request.json.get('context', '')
        response = requests.post(MODEL_API_URL, json={'query': natural_language_query, 'context': context})
        if response.status_code == 200:
            sql_query = response.json().get('sql_query', 'No SQL query generated')
            
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute(sql_query)
            
            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            
            # Fetch results and format them
            rows = cursor.fetchall()
            results = [dict(zip(column_names, row)) for row in rows]
            
            cursor.close()
            connection.close()
            
            return jsonify({'sql_query': sql_query, 'results': results})
        else:
            return jsonify({'error': 'Error in generating SQL query'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/get_table_context', methods=['POST'])
def get_table_context_route():
    table_name = request.json.get('table_name', '')
    context = get_table_context(table_name)
    return jsonify({'context': context})

@app.route('/get_table_list', methods=['GET'])
def get_table_list():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return jsonify({'tables': tables})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
