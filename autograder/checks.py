import json, os, re, subprocess, sys
from typing import Dict, List, Tuple

class CheckError(Exception):
    pass


def run_cmd(cmd: List[str], cwd: str = '.', timeout: int = 20) -> Tuple[int, str, str]:
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        raise CheckError(f"Timed out running: {' '.join(cmd)}")
    return p.returncode, out, err


def exists(path: str) -> bool:
    return os.path.exists(path)


def load_json(path: str) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def approx(a: float, b: float, tol: float) -> bool:
    return abs(float(a) - float(b)) <= tol


def detect_python_files() -> bool:
    return any(exists(p) for p in [
        'process_orders.py', 'models.py'
    ])


def detect_java_files() -> bool:
    return any(exists(p) for p in [
        'Order.java', 'OrderProcessor.java'
    ])


def static_checks_python() -> Dict[str, bool]:
    ok = {
        'functions': False,
        'control_flow': False,
        'oop': False
    }
    try:
        with open('process_orders.py', 'r', encoding='utf-8') as f:
            s = f.read()
        ok['functions'] = bool(re.search(r"def\s+(aggregate|filter_high_value|parse_args)\(", s))
        ok['control_flow'] = bool(re.search(r"for\s|while\s|if\s", s))
    except FileNotFoundError:
        pass
    try:
        with open('models.py', 'r', encoding='utf-8') as f:
            m = f.read()
        ok['oop'] = 'class Order' in m and 'def total' in m
    except FileNotFoundError:
        pass
    return ok


def static_checks_java() -> Dict[str, bool]:
    ok = {'functions': True, 'control_flow': False, 'oop': False}
    try:
        with open('OrderProcessor.java', 'r', encoding='utf-8') as f:
            s = f.read()
        ok['control_flow'] = bool(re.search(r"for\\s*\\(|while\\s*\\(|if\\s*\\(", s))
    except FileNotFoundError:
        pass
    try:
        with open('Order.java', 'r', encoding='utf-8') as f:
            s = f.read()
        ok['oop'] = 'class Order' in s and 'total(' in s
    except FileNotFoundError:
        pass
    return ok


def run_unit_tests(lang: str, timeout: int) -> Tuple[bool, str]:
    if lang == 'python' and exists('tests'):
        code, out, err = run_cmd([sys.executable, '-m', 'unittest', '-q'], timeout=timeout)
        return code == 0, out + err
    if lang == 'java':
        # Optional: project may include JUnit setup; try to run if present
        if any(n.lower().endswith('test.java') for n in os.listdir('.')):
            # naive compile & run (expects junit on classpath in the environment)
            try:
                run_cmd(['javac', '-cp', '.:junit-4.13.2.jar:hamcrest-core-1.3.jar'] +
                        [n for n in os.listdir('.') if n.endswith('.java')], timeout=timeout)
                code, out, err = run_cmd(['java', '-cp', '.:junit-4.13.2.jar:hamcrest-core-1.3.jar', 'org.junit.runner.JUnitCore', 'OrderTest'], timeout=timeout)
                return code == 0, out + err
            except Exception as e:
                return False, f"JUnit run failed: {e}"
    return True, ''  # not required


def run_program(lang: str, timeout: int, threshold: str = '100') -> Tuple[bool, str]:
    # clean outputs if any
    for p in ['summary.json', 'high_value_orders.csv']:
        if exists(p):
            try: os.remove(p)
            except: pass
    if lang == 'python':
        if not exists('process_orders.py'):
            raise CheckError('process_orders.py not found')
        code, out, err = run_cmd([sys.executable, 'process_orders.py', '--input', 'autograder/fixtures/orders.csv', '--threshold', threshold], timeout=timeout)
        return code == 0, out + err
    else:
        # Java
        if not exists('OrderProcessor.java'):
            raise CheckError('OrderProcessor.java not found')
        code, out, err = run_cmd(['javac'] + [n for n in os.listdir('.') if n.endswith('.java')], timeout=timeout)
        if code != 0:
            return False, out + err
        code, out, err = run_cmd(['java', 'OrderProcessor', '--input', 'autograder/fixtures/orders.csv', '--threshold', threshold], timeout=timeout)
        return code == 0, out + err


def validate_outputs(tol: float) -> Dict[str, str]:
    issues = {}
    if not exists('summary.json'):
        issues['summary.json'] = 'missing'
        return issues
    try:
        s = load_json('summary.json')
    except Exception as e:
        issues['summary.json'] = f'not valid JSON: {e}'
        return issues
    for key in ['total_revenue','average_order_value','orders_per_category','top_category_by_revenue']:
        if key not in s:
            issues[f'summary.json:{key}'] = 'missing key'
    # Expected values from fixture
    if 'total_revenue' in s and not approx(s['total_revenue'], 303.47, tol):
        issues['total_revenue'] = f"expected ≈303.47, got {s['total_revenue']}"
    if 'average_order_value' in s and not approx(s['average_order_value'], 75.87, tol):
        issues['average_order_value'] = f"expected ≈75.87, got {s['average_order_value']}"
    if 'orders_per_category' in s:
        opc = s['orders_per_category']
        expected = {'Books': 2, 'Electronics': 1, 'Toys': 1}
        if any(opc.get(k) != v for k, v in expected.items()):
            issues['orders_per_category'] = f"expected {expected}, got {opc}"
    if 'top_category_by_revenue' in s and s['top_category_by_revenue'] != 'Electronics':
        issues['top_category_by_revenue'] = f"expected 'Electronics', got {s['top_category_by_revenue']}"

    if not exists('high_value_orders.csv'):
        issues['high_value_orders.csv'] = 'missing'
    else:
        with open('high_value_orders.csv', 'r', encoding='utf-8') as f:
            header = f.readline().strip()
        expected_header = 'order_id,customer_id,category,unit_price,quantity,timestamp'
        if header != expected_header:
            issues['high_value_orders.csv:header'] = f"expected '{expected_header}', got '{header}'"
    return issues


def error_path_check(lang: str, timeout: int) -> bool:
    # Program should exit non‑zero on missing file
    if lang == 'python':
        code, out, err = run_cmd([sys.executable, 'process_orders.py', '--input', 'nope.csv'], timeout=timeout)
    else:
        run_cmd(['javac'] + [n for n in os.listdir('.') if n.endswith('.java')], timeout=timeout)
        code, out, err = run_cmd(['java', 'OrderProcessor', '--input', 'nope.csv'], timeout=timeout)
    return code != 0
