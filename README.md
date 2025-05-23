Code Quality Evaluator

An AI-powered tool to analyze C, C++, Python, and Java code for vulnerabilities and maintainability, built with React (Vite) and Flask.

Setup

Backend





Navigate to backend/.



Install dependencies:

pip install flask flask-cors



Run the Flask server:

python app.py

Frontend





Navigate to frontend/.



Install dependencies:

npm install



Start the Vite development server:

npm run dev

Usage





Select a programming language (C, C++, Python, or Java) from the dropdown.



Enter code in the textarea.



Click "Analyze Code" to get vulnerability and maintainability analysis.



View results in the right panel.

Model Details





Mock Model: Simulates CodeBERT with heuristic-based error detection for C/C++ (e.g., gets(), strcpy()), Python (e.g., eval(), os.system()), and Java (e.g., SQL injection, resource leaks).



Real Implementation: Use CodeBERT, fine-tuned on datasets like Juliet Test Suite (C/C++) or custom datasets for Python/Java. Preprocess with tree-sitter (C/C++/Python), javalang (Java), and Joern for CPG.

Notes





This is a simplified implementation with mock analysis.



For production, integrate CodeBERT, fine-tune on labeled datasets, and use proper preprocessing tools (tree-sitter, Joern, javalang).



Vite is used for the frontend, providing a fast development experience.