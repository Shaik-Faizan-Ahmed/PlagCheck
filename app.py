from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os

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

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/check', methods=['POST'])
def check_plagiarism_route():
    option = request.form.get('option')
    text = ""
    files = []

    try:
        if option == 'text':
            text = request.form.get('text')
            if not text:
                return jsonify({"error": "No text provided."}), 400

            sentences = get_sentences(text)
            df = check_plagiarism(sentences, text)

            if df.empty:
                return jsonify({"data": "No plagiarism found."})
            return jsonify({"data": df.to_dict(orient="records")})

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
            return jsonify({"data": df.to_dict(orient="records")})

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

            return jsonify({
                "data": similarity_list,
                "heatmap": heatmap_path
            })

        else:
            return jsonify({"error": "Invalid option selected."}), 400

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
