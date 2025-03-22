import os
import logging
from flask import Flask, request, jsonify, render_template

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "wheel-of-fortune-secret")

# In-memory storage for scores
scores = []

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@app.route('/submit-score', methods=['POST'])
def submit_score():
    """Submit and store a player's score"""
    global scores
    try:
        data = request.get_json()
        
        # Validate input data
        if not data or 'player' not in data or 'score' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        player = data['player']
        score = data['score']
        
        # Validate score is a number
        try:
            score = int(score)
        except ValueError:
            return jsonify({'error': 'Score must be a number'}), 400
        
        # Add score to the list
        scores.append({'player': player, 'score': score})
        
        # Sort scores by score (highest first)
        sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        
        # Keep only top 10 scores
        if len(sorted_scores) > 10:
            sorted_scores = sorted_scores[:10]
        
        scores = sorted_scores
        
        return jsonify(scores)
    except Exception as e:
        logging.error(f"Error submitting score: {str(e)}")
        return jsonify({'error': 'Failed to submit score'}), 500

@app.route('/scores', methods=['GET'])
def get_scores():
    """Get all scores"""
    global scores
    return jsonify(scores)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
