from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import requests  # For fetching API credits from SerpAPI
import json  # For saving and reading history

# Fix for matplotlib GUI backend error
import matplotlib
matplotlib.use('Agg')

from file_processing import read_file
from text_processing import get_sentences
from plagiarism_checker import check_plagiarism, get_similarity_between_files
from visualization import plot_similarity_graphs, plot_similarity_heatmap

app = Flask(__name__)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# File to store history
HISTORY_FILE = 'history.json'

# Your new SerpAPI key
API_KEY = "452ad616874c729414e8e83a112a68c8c20c4bcd927b5b9f6db24ed45dbc37d1"  # Replace this with your new API key

# Function to get remaining API credits
def get_api_credits():
    url = f"https://serpapi.com/account.json?api_key={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        credits = data.get("remaining_searches", 0)
        return credits
    except Exception as e:
        print(f"Error fetching API credits: {str(e)}")
        return None

# Function to load history from the JSON file
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as file:
            return json.load(file)
    return []

# Function to save history to the JSON file
def save_history(history):
    with open(HISTORY_FILE, 'w') as file:
        json.dump(history, file)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_plagiarism_route():
    option = request.form.get('option')
    text = ""
    files = []
    history = load_history()  # Load current history to add new results

    try:
        if option == 'text':
            text = request.form.get('text')
            if not text:
                return jsonify({"error": "No text provided."}), 400

            sentences = get_sentences(text)
            df = check_plagiarism(sentences, text)

            if df.empty:
                return jsonify({"data": "No plagiarism found."})

            result = df.to_dict(orient="records")
            # Save the result to history
            history.append({'type': 'text', 'result': result})
            save_history(history)

            return jsonify({"data": result})

        elif option == 'file':
            uploaded_file = request.files.get('file')
            if not uploaded_file or not uploaded_file.filename:
                return jsonify({"error": "No file uploaded."}), 400

            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(filepath)

            text = read_file(filepath)
            if not text:
                return jsonify({"error": "Could not extract text from the file."}), 400

            sentences = get_sentences(text)
            df = check_plagiarism(sentences, text)

            if df.empty:
                return jsonify({"data": "No plagiarism found."})

            result = df.to_dict(orient="records")
            # Save the result to history
            history.append({'type': 'file', 'filename': filename, 'result': result})
            save_history(history)

            return jsonify({"data": result})

        elif option == 'similarity':
            uploaded_files = request.files.getlist('files')
            saved_files = []

            for file in uploaded_files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    saved_files.append(filepath)

            if not saved_files:
                return jsonify({"error": "No valid files uploaded for similarity check."}), 400

            files = [read_file(f) for f in saved_files]
            similarity_list = get_similarity_between_files(files)
            heatmap_path = plot_similarity_heatmap(similarity_list, len(files))

            # Save the similarity result to history
            history.append({'type': 'similarity', 'files': [file.filename for file in uploaded_files], 'similarity': similarity_list})
            save_history(history)

            return jsonify({
                "data": similarity_list,
                "heatmap": heatmap_path
            })

        else:
            return jsonify({"error": "Invalid option selected."}), 400

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/history', methods=['GET'])
def get_history():
    history = load_history()  # Load the history from the file
    return jsonify({"history": history})

@app.route('/api/credits', methods=['GET'])
def api_credits():
    credits = get_api_credits()
    if credits is not None:
        return jsonify({"credits": credits})
    else:
        return jsonify({"error": "Unable to fetch API credits."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
