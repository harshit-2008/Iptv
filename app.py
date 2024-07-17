import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iptv.db'
db = SQLAlchemy(app)

# Define the directory where recordings will be saved
RECORDINGS_DIR = 'recordings'

# Ensure the RECORDINGS_DIR exists
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)

# Define the database model
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    url = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Record {self.title}>'

# Define the routes
@app.route('/add', methods=['POST'])
def add_record():
    data = request.get_json()
    title = data.get('title')
    url = data.get('url')
    
    if not title or not url:
        return jsonify({'error': 'Title and URL are required'}), 400
    
    new_record = Record(title=title, url=url)
    try:
        db.session.add(new_record)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Record with this title or URL already exists'}), 400
    
    return jsonify({'message': 'Record added successfully'}), 201

@app.route('/list', methods=['GET'])
def list_records():
    records = Record.query.all()
    return jsonify([{'id': r.id, 'title': r.title, 'url': r.url, 'created_at': r.created_at} for r in records]), 200

# Define the bot token and updater
BOT_TOKEN = '7439562089:AAGNK5J1avMZLtD-KMOkd3yyiFRiMTBIS48'
updater = Updater(token=BOT_TOKEN, use_context=True)

# Define the /token command handler
def token_command(update: Update, context: CallbackContext):
    update.message.reply_text(f'The bot token is: {BOT_TOKEN}')

# Add the /token command to the dispatcher
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('token', token_command))

# Start the bot
updater.start_polling()

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
