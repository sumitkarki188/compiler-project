import React, { useState } from 'react';
import './App.css';

function App() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('cpp');
  const [result, setResult] = useState(null);
  const [theme, setTheme] = useState('light');

  const analyzeCode = async () => {
    try {
      const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error analyzing code:', error);
      setResult({ fixed_code: '', issues: [{ message: 'Error processing the request. Please try again.' }] });
    }
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <div className={`app ${theme}`}>
      <header>
        <h1>CodeIQ Analyzer</h1>
        <button onClick={toggleTheme}>
          {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
        </button>
      </header>
      <select value={language} onChange={(e) => setLanguage(e.target.value)}>
        <option value="python">Python</option>
        <option value="cpp">C++</option>
        <option value="java">Java</option>
      </select>
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Paste your code here..."
      />
      <button onClick={analyzeCode}>Analyze</button>

      {result && (
        <div className="output">
          <h2>Fixed Code:</h2>
          <pre className="code-output">{typeof result.fixed_code === 'string' ? result.fixed_code : JSON.stringify(result.fixed_code, null, 2)}</pre>

          <h3>Issues:</h3>
          {Array.isArray(result.issues) && result.issues.length > 0 ? (
            <ul>
              {result.issues.map((issue, index) => (
                <li key={index} className="issue">
                  <strong>{issue.message || 'Unknown issue'}</strong>
                </li>
              ))}
            </ul>
          ) : (
            <p>No issues found.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
