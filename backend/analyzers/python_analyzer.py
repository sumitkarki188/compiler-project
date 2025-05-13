import ast
import autopep8
from ai_suggester import get_ai_suggestions

def analyze_python(code):
    result = {
        'static_analysis': {'issues': [], 'fixed_code': ''},
        'ai_analysis': {}
    }
    
    # Static analysis
    try:
        ast.parse(code)
    except SyntaxError as e:
        result['static_analysis']['issues'].append({
            'line': e.lineno,
            'message': e.msg,
            'type': 'SyntaxError'
        })
    
    # AutoPEP8 formatting
    try:
        result['static_analysis']['fixed_code'] = autopep8.fix_code(code)
    except Exception as e:
        result['static_analysis']['fixed_code'] = code
    
    # AI-powered analysis
    try:
        result['ai_analysis'] = get_ai_suggestions(code, 'python')
    except Exception as e:
        result['ai_analysis']['error'] = str(e)
    
    return result