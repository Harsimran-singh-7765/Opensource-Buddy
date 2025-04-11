from flask import Flask, render_template, request, jsonify
#from backend.crew_controller import run_crew_flow  # Will build this soon

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    topic = data.get('topic')
    
    from backend.agents.Git_collector import run_project_hunter

    result = run_project_hunter(topic) 

    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
