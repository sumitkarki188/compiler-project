from model_handler import ai_model

def get_ai_suggestions(code, language):
    """Main interface for AI suggestions"""
    suggestions = {}
    
    # Generate code fixes
    suggestions['code_fix'] = ai_model.generate_suggestions(code, language)
    
    # Detect vulnerabilities
    suggestions['security'] = ai_model.detect_vulnerabilities(code)
    
    # AST analysis
    suggestions['ast_analysis'] = ai_model.parse_ast(code, language)
    
    return suggestions