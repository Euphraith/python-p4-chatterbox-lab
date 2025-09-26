# In testing/app_test.py (Simplified for Pytest)

from datetime import datetime
from app import app
from models import db, Message

class TestApp:
    '''Flask application in app.py'''

    # NEW: Define a method that runs before every test
    def setup_method(self, method):
        with app.app_context():
            # 1. Ensure the table is completely clean before starting a test
            Message.query.delete() 
            
            # 2. Seed the data required for tests that need an existing record
            m1 = Message(body='Base Message', username='Seeder')
            db.session.add(m1)
            db.session.commit()
            
    
    def teardown_method(self, method):
        
        with app.app_context():
            db.session.rollback()


    
    def test_updates_body_of_message_in_database(self):
        '''updates the body of a message in the database.'''
        with app.app_context():
            # This now reliably fetches the 'Base Message' created in setup_method
            m = Message.query.first()
            id = m.id
            body = m.body

            app.test_client().patch(
                f'/messages/{id}',
                json={
                    "body":"Goodbye 👋",
                }
            )

            g = Message.query.filter_by(body="Goodbye 👋").first()
            assert(g)

            # Cleanup is handled by the start of the next setup_method
            # The original cleanup logic here is complex and can be removed
            # g.body = body
            # db.session.add(g)
            # db.session.commit()