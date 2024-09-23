from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        response_data = jsonify([message.to_dict() for message in messages])
        response = make_response(response_data, 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    elif request.method == 'POST':
        data = request.json
        if not data or 'body' not in data or 'username' not in data:
            error_response = make_response(jsonify({"error": "Missing required fields"}), 400)
            return error_response
        
        new_message = Message(body=data['body'], username=data['username'])
        db.session.add(new_message)
        try:
            db.session.commit()
            response_data = jsonify(new_message.to_dict())
            response = make_response(response_data, 201)
            response.headers['Content-Type'] = 'application/json'
            return response
        except IntegrityError:
            db.session.rollback()
            error_response = make_response(jsonify({"error": "Failed to create message"}), 400)
            return error_response

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)
    if not message:
        error_response = make_response(jsonify({"error": "Message not found"}), 404)
        return error_response

    if request.method == 'PATCH':
        data = request.json
        if not data or 'body' not in data:
            error_response = make_response(jsonify({"error": "Missing body field"}), 400)
            return error_response
        
        message.body = data['body']
        db.session.commit()
        response_data = jsonify(message.to_dict())
        response = make_response(response_data, 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        response = make_response('', 204)
        return response

if __name__ == '__main__':
    app.run(port=5555)
