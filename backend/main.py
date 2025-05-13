from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzers.python_analyzer import analyze_python
from analyzers.java_analyzer import analyze_java
from analyzers.c_cpp_analyzer import analyze_cpp
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return "AI Code Analyzer API"

@app.route('/analyze', methods=['POST'])
def analyze_code():
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', '').lower()
        
        if not code or not language:
            return jsonify({'error': 'Missing code or language parameter'}), 400
            
        if language == 'python':
            result = analyze_python(code)
        elif language == 'java':
            result = analyze_java(code)
        elif language in ['c', 'cpp']:
            result = analyze_cpp(code)
        else:
            return jsonify({'error': 'Unsupported language'}), 400
            
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        return jsonify({'error': 'Server error during analysis'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)