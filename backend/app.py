from flask import Flask, jsonify, request
from flask_cors import CORS
import cx_Oracle

app = Flask(__name__)
app.config['DEBUG'] = True  # Ativa o modo de depuração
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})  # Permite o acesso do frontend e todos os métodos HTTP

db_config = {
    'user': 'rm557808',
    'password': '021093',
    'dsn': 'oracle.fiap.com.br:1521/orcl'
}

def connect_db():
    """Função para conectar ao banco de dados Oracle."""
    try:
        connection = cx_Oracle.connect(**db_config)
        print("Conexão bem-sucedida com o banco de dados!")
        return connection
    except cx_Oracle.DatabaseError as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None

@app.route('/api/oficinas', methods=['GET'])
def get_oficinas():
    """Endpoint para buscar todas as oficinas."""
    connection = connect_db()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM oficinas_credenciadas")
        rows = cursor.fetchall()
        oficinas = [
            {
                "id": row[0],
                "empresa": row[1],
                "contato": row[2],
                "telefone": row[3],
                "email": row[4],
                "cidade": row[5]
            }
            for row in rows
        ]
        return jsonify(oficinas)
    except Exception as e:
        print("Erro ao buscar oficinas:", e)
        return jsonify({'error': 'Failed to fetch oficinas'}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/oficinas', methods=['POST'])
def create_oficina():
    """Endpoint para criar uma nova oficina."""
    data = request.json
    required_fields = ["empresa", "contato", "telefone", "email", "cidade"]
    missing_fields = [field for field in required_fields if field not in data]
    
    # Verificação de campos obrigatórios
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    connection = connect_db()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO oficinas_credenciadas (empresa, contato, telefone, email, cidade) "
            "VALUES (:empresa, :contato, :telefone, :email, :cidade)",
            empresa=data['empresa'], contato=data['contato'],
            telefone=data['telefone'], email=data['email'], cidade=data['cidade']
        )
        connection.commit()
        return jsonify({'message': 'Oficina created successfully'}), 201
    except cx_Oracle.DatabaseError as e:
        print("Erro ao criar oficina:", e)
        return jsonify({'error': 'Failed to create oficina'}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/oficinas/<int:id>', methods=['PUT'])
def update_oficina(id):
    """Atualiza uma oficina existente pelo ID."""
    data = request.json
    connection = connect_db()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE oficinas_credenciadas SET empresa=:empresa, contato=:contato, telefone=:telefone, email=:email, cidade=:cidade WHERE id=:id",
            empresa=data['empresa'], contato=data['contato'],
            telefone=data['telefone'], email=data['email'], cidade=data['cidade'], id=id
        )
        connection.commit()
        return jsonify({'message': 'Oficina updated successfully'}), 200
    except Exception as e:
        print("Erro ao atualizar oficina:", e)
        return jsonify({'error': 'Failed to update oficina'}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/oficinas/<int:id>', methods=['DELETE'])
def delete_oficina(id):
    """Exclui uma oficina pelo ID."""
    connection = connect_db()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM oficinas_credenciadas WHERE id=:id", id=id)
        connection.commit()
        return jsonify({'message': 'Oficina deleted successfully'}), 200
    except Exception as e:
        print("Erro ao excluir oficina:", e)
        return jsonify({'error': 'Failed to delete oficina'}), 500
    finally:
        if connection:
            connection.close()

# Manipulador de erros gerais
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(port=5003)
