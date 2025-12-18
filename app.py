from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, template_folder='templates')
CORS(app)

# Database Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['ExamRadarDB']
collection = db['Questions']

print("✅ EXAM-RADAR SERVER STARTED!")

@app.route('/')
def home():
    return render_template('index.html')

# 1. Add Data (Admin)
@app.route('/add', methods=['POST'])
def add_question():
    data = request.json
    collection.insert_one({
        "subject": data['subject'],
        "topic": data['topic'], 
        "year": int(data['year']),
        "marks": int(data['marks'])
    })
    return jsonify({"message": "Saved!"})

# 2. Analyze (Winning Logic)
@app.route('/analyze', methods=['GET'])
def analyze():
    subject = request.args.get('subject')
    pipeline = [
        {"$match": {"subject": subject}}, 
        {"$group": {
            "_id": "$topic", 
            "count": {"$sum": 1},
        }},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    results = list(collection.aggregate(pipeline))
    return jsonify(results)

# 3. Get Subjects
@app.route('/subjects', methods=['GET'])
def get_subjects():
    subjects = collection.distinct("subject")
    return jsonify(subjects)

if __name__ == '__main__':
    app.run(port=5000)