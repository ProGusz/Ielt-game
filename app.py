import random
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)
Session(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# IELTS vocabulary words with difficulty levels
ielts_words = {
    'easy': ["cat", "dog", "house", "car", "book", "tree", "sun", "moon", "star", "fish"],
    'medium': ["abundant", "adapt", "adjacent", "annual", "apparent", "approximate", "assist", "attain"],
    'hard': ["ubiquitous", "euphemism", "paradigm", "enigmatic", "anomaly", "paradox", "ambiguous", "empirical"]
}

def get_word_definition(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data and isinstance(data, list) and len(data) > 0:
            meanings = data[0].get('meanings', [])
            if meanings:
                return meanings[0].get('definitions', [{}])[0].get('definition', 'Definition not found.')
    return "Definition not available."

def get_word_options(correct_word, difficulty):
    options = [correct_word]
    word_list = ielts_words[difficulty]
    while len(options) < 4:
        random_word = random.choice(word_list)
        if random_word not in options:
            options.append(random_word)
    random.shuffle(options)
    return options

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify({'success': True, 'message': 'Logged in successfully'}), 200
    
    return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

@app.route('/start_game', methods=['POST'])
def start_game():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    difficulty = request.json['difficulty']
    session['player'] = {
        'level': 1,
        'exp': 0,
        'health': 100,
        'max_health': 100,
        'damage': 10
    }
    session['enemy'] = generate_enemy()
    session['difficulty'] = difficulty
    return jsonify(session['player'])

@app.route('/get_word', methods=['GET'])
def get_word():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    difficulty = session.get('difficulty', 'medium')
    word = random.choice(ielts_words[difficulty])
    definition = get_word_definition(word)
    options = get_word_options(word, difficulty)
    return jsonify({'word': word, 'definition': definition, 'options': options})

@app.route('/check_answer', methods=['POST'])
def check_answer():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    user_word = request.json['word']
    correct_word = request.json['correct_word']
    is_correct = user_word.lower() == correct_word.lower()
    
    if is_correct:
        damage = session['player']['damage']
        session['enemy']['health'] -= damage
        session['player']['exp'] += 10
        if session['player']['exp'] >= 100:
            level_up()
    else:
        session['player']['health'] -= 5

    game_over = session['player']['health'] <= 0
    enemy_defeated = session['enemy']['health'] <= 0

    if enemy_defeated:
        session['enemy'] = generate_enemy()

    return jsonify({
        'is_correct': is_correct,
        'player': session['player'],
        'enemy': session['enemy'],
        'game_over': game_over,
        'enemy_defeated': enemy_defeated
    })

def generate_enemy():
    return {
        'name': random.choice(['Goblin', 'Orc', 'Troll', 'Dragon']),
        'health': random.randint(50, 100),
        'max_health': 100
    }

def level_up():
    session['player']['level'] += 1
    session['player']['exp'] = 0
    session['player']['max_health'] += 20
    session['player']['health'] = session['player']['max_health']
    session['player']['damage'] += 5

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)