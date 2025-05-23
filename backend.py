from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzer_utils import analyze_code
from model import correct_code

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    code = data.get('code')
    language = data.get('language')

    if not code or not language:
        return jsonify({
            "message": "Missing code or language in request",
            "score": 0,
            "issues": []
        }), 400

    static_issues = analyze_code(code, language)
    ml_suggestions = correct_code(code, language)

    issues = static_issues + ml_suggestions
    score = max(0, 100 - len(issues) * 10)

    if not issues:
        return jsonify({
            "message": "Everything is OK. Good to go!",
            "score": 100,
            "issues": []
        })
    else:
        return jsonify({
            "message": "Analysis complete.",
            "score": score,
            "issues": issues
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
