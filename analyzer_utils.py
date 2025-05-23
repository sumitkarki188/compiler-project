import os
import re
import json
import shutil
import tempfile
import subprocess

def get_file_extension(lang):
    return {
        'python': '.py',
        'c': '.c',
        'cpp': '.cpp',
        'java': '.java'
    }.get(lang, '.txt')

def detect_language(code):
    if re.search(r'#include\s*<[^>]+>', code):
        return 'cpp' if re.search(r'\bstd::|using namespace std\b', code) else 'c'
    if re.search(r'\bSystem\.out\.println\b|\bpublic\s+(class|interface|enum)\b|\bpackage\s+\w+', code):
        return 'java'
    if re.search(r'\bdef\b|\bimport\b|\bprint\b', code):
        return 'python'
    return 'unknown'

def map_pylint_type(pylint_type):
    return {
        'error': 'error',
        'fatal': 'error',
        'warning': 'warning'
    }.get(pylint_type, 'info')

def generate_suggestion(issue):
    message = issue.get('message', '').lower()
    if 'unused' in message:
        return "Consider removing unused variables or imports."
    elif 'undefined' in message:
        return "Check if the variable or function is declared before use."
    elif 'missing' in message or 'expected' in message:
        return "Verify syntax and ensure required elements are present."
    elif 'deprecated' in message:
        return "Update to a modern alternative as this is deprecated."
    elif 'syntax' in message or 'invalid' in message:
        return "Fix syntax errors or ensure proper formatting."
    return "Review this line for possible improvements."

def parse_output(output, lang):
    issues = []
    if lang == 'python':
        try:
            data = json.loads(output)
            for item in data:
                msg_type = map_pylint_type(item.get('type', 'info'))
                if msg_type == 'info':
                    continue
                issues.append({
                    "line": item.get('line', 0),
                    "type": msg_type,
                    "message": item.get('message', ''),
                    "code": item.get('symbol', ''),
                    "suggestion": generate_suggestion(item)
                })
        except Exception:
            issues.append({
                "line": 0,
                "type": "error",
                "message": "Failed to parse pylint output",
                "code": "parse-error",
                "suggestion": "Check code syntax."
            })

    elif lang == 'java':
        for line in output.splitlines():
            m = re.match(r'^\[(ERROR|WARN|INFO)\]\s+.*:(\d+):\s+(.*)$', line, re.I)
            if m:
                level, line_num, msg = m.groups()
                level = level.lower()
                if level == 'info':
                    continue
                issues.append({
                    "line": int(line_num),
                    "type": "error" if level == 'error' else "warning",
                    "message": msg,
                    "code": "checkstyle",
                    "suggestion": generate_suggestion({"message": msg})
                })

    else:  # C/C++
        for line in output.splitlines():
            if any(x in line.lower() for x in ['information:', 'note:', 'style:', 'performance:', 'checkers', '--checkers-report']):
                continue

            m = re.match(r'^.*:(\d+):(?:\d+:)?\s*(error|warning|note):\s*(.*)$', line, re.I)
            if m:
                line_num, level, msg = m.groups()[0], m.groups()[2], m.groups()[3]
                level = level.lower()
                if level == 'note':
                    continue
                issues.append({
                    "line": int(line_num),
                    "type": level,
                    "message": msg,
                    "code": f"compiler-{level}",
                    "suggestion": generate_suggestion({"message": msg})
                })

    return issues

def calculate_score(issues, max_deductible_issues=10):
    score = 100
    error_count = 0
    warning_count = 0
    total_deducted = 0

    for issue in issues:
        if total_deducted >= max_deductible_issues:
            break
        typ = issue.get("type", "info").lower()
        if typ == "error":
            score -= 10
            error_count += 1
        elif typ == "warning":
            score -= 5
            warning_count += 1
        else:
            score -= 1
        total_deducted += 1

    if error_count == 0 and warning_count == 0:
        score += 5

    return max(0, min(score, 100))

def get_public_class_name(java_code):
    match = re.search(r'public\s+class\s+(\w+)', java_code)
    return match.group(1) if match else "MainClass"

def parse_gcc_errors(output):
    issues = []
    for line in output.splitlines():
        m = re.match(r'^.*:(\d+):(?:\d+:)?\s*(error|warning|note):\s*(.*)$', line, re.I)
        if m:
            line_num, level, msg = m.group(1), m.group(2).lower(), m.group(3)
            if level != "note":
                issues.append({
                    "line": int(line_num),
                    "type": level,
                    "message": msg,
                    "code": f"gcc-{level}",
                    "suggestion": "Fix the reported compiler issue."
                })
    return issues

def analyze_code(code, language):
    detected_language = detect_language(code)
    if detected_language != language:
        return [{
            "line": 0,
            "type": "error",
            "message": f"Code appears to be {detected_language}, but you selected {language}.",
            "code": "language-mismatch",
            "suggestion": f"Please choose the correct language: {detected_language}."
        }]

    if language == 'java':
        tmp_dir = tempfile.mkdtemp()
        try:
            class_name = get_public_class_name(code)
            file_path = os.path.join(tmp_dir, f"{class_name}.java")

            with open(file_path, 'w') as f:
                f.write(code)

            result = subprocess.run(['javac', file_path], capture_output=True, text=True)
            issues = []
            if result.returncode != 0:
                for line in result.stderr.splitlines():
                    m = re.match(r'^.*?:(\d+):(?:\d+:)?\s*error:\s*(.*)$', line)
                    if m:
                        line_num, msg = m.groups()
                        issues.append({
                            "line": int(line_num),
                            "type": "error",
                            "message": msg,
                            "code": "syntax-error",
                            "suggestion": "Fix the syntax error reported by the compiler."
                        })
                if not issues:
                    issues.append({
                        "line": 0,
                        "type": "error",
                        "message": "Compilation failed with errors.",
                        "code": "compile-failed",
                        "suggestion": "Fix the syntax errors in your code."
                    })
                return issues

            checkstyle_jar = 'checkstyle.jar'
            google_checks = 'google_checks.xml'
            if os.path.exists(checkstyle_jar) and os.path.exists(google_checks):
                checkstyle_result = subprocess.run(
                    ['java', '-jar', checkstyle_jar, '-c', google_checks, file_path],
                    capture_output=True, text=True
                )
                issues.extend(parse_output(checkstyle_result.stdout, language))
            else:
                issues.append({
                    "line": 0,
                    "type": "warning",
                    "message": "Checkstyle not found. Skipping style checks.",
                    "code": "style-skip",
                    "suggestion": "Include checkstyle.jar and google_checks.xml for full analysis."
                })

            if not issues:
                issues.append({
                    "line": 0,
                    "type": "info",
                    "message": "No errors found. Good to go!",
                    "code": "clean",
                    "suggestion": ""
                })
            return issues

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=get_file_extension(language)) as temp:
            temp.write(code.encode())
            temp_path = temp.name

        try:
            if language == 'python':
                result = subprocess.run(['pylint', temp_path, '--output-format=json'], capture_output=True, text=True)
                issues = parse_output(result.stdout, language)

            elif language in ('c', 'cpp'):
                compiler = 'gcc' if language == 'c' else 'g++'
                result = subprocess.run([compiler, '-fsyntax-only', temp_path], capture_output=True, text=True)
                if result.returncode != 0:
                    return parse_gcc_errors(result.stderr)

                result = subprocess.run(
                    ['cppcheck', temp_path, '--enable=all', '--template=gcc', '--inline-suppr'],
                    capture_output=True, text=True
                )
                issues = parse_output(result.stdout + "\n" + result.stderr, language)

            else:
                return [{
                    "line": 0,
                    "type": "error",
                    "message": "Unsupported language",
                    "code": "unsupported",
                    "suggestion": "Use Python, C, C++, or Java."
                }]

            if not issues:
                issues.append({
                    "line": 0,
                    "type": "info",
                    "message": "No errors found. Good to go!",
                    "code": "clean",
                    "suggestion": ""
                })
            return issues

        except Exception as e:
            return [{
                "line": 0,
                "type": "error",
                "message": f"Static analysis failed: {str(e)}",
                "code": "execution-error",
                "suggestion": "Check tool installation and file permissions."
            }]
        finally:
            os.remove(temp_path)

# Optional test
if __name__ == "__main__":
    sample_code = """public class Main { public static void main(String[] args) { System.out.println("Hello") } }"""
    language = "java"
    results = analyze_code(sample_code, language)
    for r in results:
        print(f"[{r['type'].upper()}] Line {r['line']}: {r['message']} → {r['suggestion']}")
    print("Score:", calculate_score(results))
