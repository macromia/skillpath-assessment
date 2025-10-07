import argparse, json, os, sys
from checks import (
    CheckError, detect_python_files, detect_java_files, static_checks_python,
    static_checks_java, run_unit_tests, run_program, validate_outputs,
    error_path_check
)

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUBRIC_PATH = os.path.join(SCRIPT_DIR, 'rubric.json')


def load_rubric():
    with open(RUBRIC_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', choices=['python','java'], required=False)
    args = ap.parse_args()

    rubric = load_rubric()
    weights = rubric['weights']
    tol = float(rubric['tolerances']['float'])
    timeout = int(rubric.get('timeout_seconds', 20))

    # Auto‑detect language if not provided
    lang = args.lang
    if not lang:
        if detect_python_files():
            lang = 'python'
        elif detect_java_files():
            lang = 'java'
        else:
            print(json.dumps({"error":"Could not detect language; missing expected files."}))
            return 2

    # Static checks
    if lang == 'python':
        static = static_checks_python()
    else:
        static = static_checks_java()

    score = 0
    details = { 'lang': lang, 'checks': {} }

    # OOP/functions/control_flow
    for key in ['functions','control_flow','oop']:
        gained = weights[key] if static.get(key) else 0
        score += gained
        details['checks'][key] = {'pass': bool(static.get(key)), 'points': gained, 'max': weights[key]}

    # Run program
    try:
        ok, logs = run_program(lang, timeout)
    except CheckError as e:
        ok, logs = False, str(e)

    details['run_logs'] = logs[-4000:]

    file_io_pass = ok
    gained = weights['file_io'] if file_io_pass else 0
    score += gained
    details['checks']['file_io'] = {'pass': file_io_pass, 'points': gained, 'max': weights['file_io']}

    # Validate analytics + outputs
    issues = validate_outputs(tol)
    analytics_pass = (len(issues) == 0)
    gained = weights['analytics_correctness'] if analytics_pass else 0
    score += gained
    details['checks']['analytics_correctness'] = {
        'pass': analytics_pass,
        'points': gained,
        'max': weights['analytics_correctness'],
        'issues': issues
    }

    # Error handling check
    eh_pass = error_path_check(lang, timeout)
    gained = weights['error_handling'] if eh_pass else 0
    score += gained
    details['checks']['error_handling'] = {'pass': eh_pass, 'points': gained, 'max': weights['error_handling']}

    # Unit tests (optional but graded)
    ut_pass, ut_logs = run_unit_tests(lang, timeout)
    gained = weights['unit_tests'] if ut_pass else 0
    score += gained
    details['checks']['unit_tests'] = {'pass': ut_pass, 'points': gained, 'max': weights['unit_tests'], 'logs': ut_logs[-4000:]}

    # Final
    total = sum(weights.values())
    details['score'] = score
    details['max_score'] = total
    details['passed'] = score >= int(0.7 * total)

    print(json.dumps(details, indent=2))
    return 0 if details['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
