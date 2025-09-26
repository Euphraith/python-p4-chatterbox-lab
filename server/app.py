from flask import Flask, request, make_response
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource # <-- NEW IMPORTS
from sqlalchemy.exc import IntegrityError # For robust error handling

from models import db, Message # Assuming models.py now has the correct Message model

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app) # <-- INITIALIZE API

# --- Helper Function for Validation Errors (often required by labs) ---
def make_validation_response(e):
    # Flask-RESTful style: return data dictionary and status code
    return {'errors': [str(e)]}, 422 
# -------------------------------------------------------------------


class MessageList(Resource):
    def get(self):
        """GET /messages: returns all messages, ordered by created_at."""
        messages = Message.query.order_by(Message.created_at.asc()).all()
        # Flask-RESTful style: return list and status code
        return [message.to_dict() for message in messages], 200

    def post(self):
        """POST /messages: creates a new message."""
        data = request.get_json()
        try:
            message = Message(body=data['body'], username=data['username'])
            db.session.add(message)
            db.session.commit()
            
            # Flask-RESTful style: return dictionary and 201 Created
            return message.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return make_validation_response(e)


class MessageById(Resource):
    def patch(self, id):
        """PATCH /messages/<int:id>: updates the body."""
        
        message = db.session.get(Message, id) # Use session.get for SQLAlchemy 2.0 style
        
        if not message:
            return {'error': 'Message not found'}, 404
        
        data = request.get_json()
        
        try:
            # Update the body
            message.body = data['body']
            db.session.commit()
            
            # Flask-RESTful style: return updated dictionary and 200 OK
            return message.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return make_validation_response(e)


    def delete(self, id):
        """DELETE /messages/<int:id>: deletes the message."""
        
        message = db.session.get(Message, id)
        
        if not message:
            return {'error': 'Message not found'}, 404

        db.session.delete(message)
        db.session.commit()
        
        # Flask-RESTful style: return empty body and 204 No Content
        return '', 204

# --- API Route Registration ---
api.add_resource(MessageList, '/messages')
api.add_resource(MessageById, '/messages/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)