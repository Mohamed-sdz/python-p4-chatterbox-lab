from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# GET /messages: Returns an array of all messages as JSON, ordered by created_at in ascending order.
@app.route('/messages', methods=['GET'])
def get_all_messages():
    # Query the messages from the database and order them by created_at
    messages = Message.query.order_by(Message.created_at.asc()).all()
    
    # Serialize the messages to JSON format
    messages_json = [{"id": message.id, "body": message.body, "username": message.username, "created_at": message.created_at, "updated_at": message.updated_at} for message in messages]

    return jsonify(messages_json)

# POST /messages: Creates a new message with a body and username from params, and returns the newly created post as JSON.
@app.route('/messages', methods=['POST'])
def create_message():
    # Get JSON data from the request
    data = request.get_json()

    # Extract body and username from the JSON data
    body = data.get("body")
    username = data.get("username")

    # Check if both 'body' and 'username' are present
    if not body or not username:
        return jsonify({"error": "Both 'body' and 'username' are required"}), 400

    # Create a new message
    new_message = Message(body=body, username=username)

    # Add the message to the database
    db.session.add(new_message)
    db.session.commit()

    # Return the newly created message as JSON
    response = jsonify({
        "id": new_message.id,
        "body": new_message.body,
        "username": new_message.username,
        "created_at": new_message.created_at,
        "updated_at": new_message.updated_at
    })

    return response, 201  # 201 indicates "Created" status code

# PATCH /messages/<int:id>: Updates the body of the message using params, and returns the updated message as JSON.
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    # Get the message by ID from the database
    message = Message.query.get(id)


    if not message:
        return jsonify({"error": "Message not found"}), 404

    # Get JSON data from the request
    data = request.get_json()

    # Update the 'body' attribute if it's present in the JSON data
    new_body = data.get("body")
    if new_body:
        message.body = new_body

    # Commit the changes to the database
    db.session.commit()

    # Return the updated message as JSON
    return jsonify({"message": "Message updated successfully", "id": message.id, "body": message.body})

# DELETE /messages/<int:id>: Deletes the message from the database.
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    # Get the message by ID from the database
    message = db.session.query(Message).get(id)

    if not message:
        return jsonify({"error": "Message not found"}), 404

    # Delete the message from the database
    db.session.delete(message)
    db.session.commit()

    return jsonify({"message": "Message deleted successfully"})

if __name__ == '__main__':
    app.run(port=5555)
