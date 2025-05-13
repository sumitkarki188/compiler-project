from transformers import AutoTokenizer, T5ForConditionalGeneration, pipeline
import torch
from tree_sitter import Language, Parser
import os

class CodeAIModel:
    def __init__(self):
        # Ensure 'build' directory exists
        if not os.path.exists('build'):
            os.makedirs('build')
        
        # Build Tree-sitter language parsers
        if not os.path.exists('build/lang.so'):
            from tree_sitter import Language
            Language.build_library(
                'build/lang.so',
                [
                    'vendor/tree-sitter-python',
                    'vendor/tree-sitter-java',
                    'vendor/tree-sitter-cpp'
                ]
            )
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_models()
        self.setup_parsers()
        
    def load_models(self):
        """Load all required ML models"""
        self.tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-base")
        self.code_t5 = T5ForConditionalGeneration.from_pretrained("Salesforce/codet5-base").to(self.device)
        self.codebert_clf = pipeline(
            "text-classification",
            model="microsoft/codebert-base",
            tokenizer="microsoft/codebert-base",
            device=0 if torch.cuda.is_available() else -1
        )
        
    def setup_parsers(self):

        if not os.path.exists('build'):
            os.makedirs('build')

        if not os.path.exists('build/lang.so'):
            from tree_sitter import Language
            Language.build_library(
                'build/lang.so',
                [
                    'vendor/tree-sitter-python',
                    'vendor/tree-sitter-java',
                    'vendor/tree-sitter-cpp'
                ]
            )

    # Initialize parsers
    self.parsers = {
        'python': Parser(),
        'java': Parser(),
        'cpp': Parser()
    }
    self.parsers['python'].set_language(Language('build/lang.so', 'python'))
    self.parsers['java'].set_language(Language('build/lang.so', 'java'))
    self.parsers['cpp'].set_language(Language('build/lang.so', 'cpp'))

    def parse_ast(self, code, lang):
        """Generate AST representation using Tree-sitter"""
        try:
            tree = self.parsers[lang].parse(bytes(code, "utf8"))
            return tree.root_node.sexp()
        except Exception as e:
            return f"AST parsing failed: {str(e)}"

    def generate_suggestions(self, code, lang):
        """Generate code suggestions using CodeT5"""
        try:
            ast_context = self.parse_ast(code, lang)
            prompt = f"Fix {lang} code with AST: {ast_context}\nCode: {code}\nFixed:"
            
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            ).to(self.device)
            
            outputs = self.code_t5.generate(
                inputs.input_ids,
                max_length=512,
                temperature=0.7,
                num_return_sequences=1
            )
            
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            return f"Suggestion generation failed: {str(e)}"

    def detect_vulnerabilities(self, code):
        """Detect security issues using CodeBERT"""
        try:
            results = self.codebert_clf(code[:512])
            return {
                'label': results[0]['label'],
                'score': float(results[0]['score'])
            }
        except Exception as e:
            return {'error': str(e)}

# Singleton instance
ai_model = CodeAIModel()