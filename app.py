from flask import Flask, render_template, request, jsonify
from backend.agents.Project_sorter import func  # Assuming this returns your final data

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    topic = request.form.get('topic')

    if not topic:
        return jsonify({"error": "No topic provided"}), 400

    try:
        result = func(topic)  
        result = result.replace("```html", "").replace("```", "").strip()
        return render_template("index.html", result=result)
    except Exception as e:
        print("❌ Error during processing:", e)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True)
