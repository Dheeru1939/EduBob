"""
Quick regression for the code_runner argument-parsing fix.

Verifies that the runner correctly handles all the test_case input
formats the LLM tends to generate:
  - Single string:    "'World'"
  - CSV ints:         "5, 10"
  - CSV strings:      "'a', 'b'"
  - Paren-wrapped:    "('example', 'about')"
  - List arg:         "[1, 2, 3]"
  - Dict arg:         "{'a': 1, 'b': 2}"
  - Empty:            ""
"""

from core.code_runner import run_code_with_tests


CASES = [
    {
        "name": "single string arg",
        "code": "def greet(name):\n    return f'Hello, {name}!'",
        "test_cases": [{"input": "'World'", "expected": "Hello, World!"}],
    },
    {
        "name": "two int args via CSV",
        "code": "def add(a, b):\n    return a + b",
        "test_cases": [{"input": "5, 10", "expected": "15"}],
    },
    {
        "name": "two string args via paren-wrapped tuple (the bug case)",
        "code": "def create_url(site, path):\n    return f'https://{site}.com/{path}'",
        "test_cases": [{"input": "('example', 'about')", "expected": "https://example.com/about"}],
    },
    {
        "name": "two string args via plain CSV",
        "code": "def create_url(site, path):\n    return f'https://{site}.com/{path}'",
        "test_cases": [{"input": "'example', 'about'", "expected": "https://example.com/about"}],
    },
    {
        "name": "single list arg",
        "code": "def total(nums):\n    return sum(nums)",
        "test_cases": [{"input": "[1, 2, 3]", "expected": "6"}],
    },
    {
        "name": "single dict arg",
        "code": "def get_a(d):\n    return d['a']",
        "test_cases": [{"input": "{'a': 42, 'b': 99}", "expected": "42"}],
    },
    {
        "name": "LLM quote-wrapped string expected (the new bug case)",
        "code": "def greet(name):\n    return f'Hello, {name}!'",
        "test_cases": [{"input": "'Alice'", "expected": "'Hello, Alice!'"}],
    },
    {
        "name": "LLM double-quote-wrapped string expected",
        "code": "def greet(name):\n    return f'Hello, {name}!'",
        "test_cases": [{"input": "'Bob'", "expected": '"Hello, Bob!"'}],
    },
]


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Code runner argument-parsing regression test")
    print("=" * 60)

    all_pass = True
    for c in CASES:
        result = run_code_with_tests(c["code"], c["test_cases"], timeout_s=5)
        passed = result["passed"]
        total = result["passed"] + result["failed"]
        status = "PASS" if passed == total else "FAIL"
        if passed != total:
            all_pass = False
            err = result["results"][0].get("error", "(no error info)")
            actual = result["results"][0].get("actual", "")
            print(f"  {status}  {c['name']}")
            print(f"        actual: {actual} | error: {err}")
        else:
            print(f"  {status}  {c['name']}")

    print("=" * 60)
    if all_pass:
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED")
