"""
Safe Code Execution Engine for EduBob v2
Windows-compatible version using multiprocessing instead of signal.SIGALRM
"""

import re
import io
import sys
import multiprocessing
from typing import Dict, List, Any, Optional
from contextlib import redirect_stdout, redirect_stderr


def _execute_in_process(code: str, test_cases: List[Dict], result_queue: multiprocessing.Queue):
    """
    Execute code in a separate process (for timeout control).
    This function runs in the child process.
    """
    try:
        # Create restricted namespace with safe builtins only
        safe_builtins = {
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'abs': abs,
            'max': max,
            'min': min,
            'sum': sum,
            'sorted': sorted,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'all': all,
            'any': any,
            'isinstance': isinstance,
            'type': type,
            'round': round,
        }
        
        namespace = {'__builtins__': safe_builtins}
        
        # Execute the student's code to define their function
        exec(code, namespace)
        
        # Extract the function name from the code
        func_name = _extract_function_name(code)
        if not func_name:
            result_queue.put({
                "error": "No function definition found in code",
                "passed": 0,
                "failed": len(test_cases),
                "results": []
            })
            return
        
        # Get the function from namespace
        if func_name not in namespace:
            result_queue.put({
                "error": f"Function '{func_name}' not found after execution",
                "passed": 0,
                "failed": len(test_cases),
                "results": []
            })
            return
        
        student_func = namespace[func_name]
        
        # Run test cases
        passed = 0
        failed = 0
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            test_result = {
                "test_number": i,
                "passed": False,
                "input": test_case.get("input", ""),
                "expected": test_case.get("expected", ""),
                "actual": "",
                "error": None
            }
            
            try:
                # Evaluate the input expression to get actual arguments
                # Input format: "'World'" or "5, 10" etc.
                input_expr = test_case.get("input", "")
                
                # Create a safe eval namespace
                eval_namespace = {'__builtins__': safe_builtins}
                
                # Parse input - could be single arg or multiple args
                if ',' in input_expr:
                    # Multiple arguments
                    args = eval(f"({input_expr},)", eval_namespace)
                else:
                    # Single argument
                    args = (eval(input_expr, eval_namespace),)
                
                # Call the student's function
                actual_result = student_func(*args)
                
                # Convert result to string for comparison
                actual_str = str(actual_result)
                expected_str = str(test_case.get("expected", ""))
                
                test_result["actual"] = actual_str
                
                # Compare results
                if actual_str == expected_str:
                    test_result["passed"] = True
                    passed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                test_result["error"] = f"{type(e).__name__}: {str(e)}"
                test_result["actual"] = "Error during execution"
                failed += 1
            
            results.append(test_result)
        
        # Send results back through queue
        result_queue.put({
            "passed": passed,
            "failed": failed,
            "results": results,
            "error": None
        })
        
    except Exception as e:
        result_queue.put({
            "error": f"Execution error: {type(e).__name__}: {str(e)}",
            "passed": 0,
            "failed": len(test_cases),
            "results": []
        })


def _extract_function_name(code: str) -> Optional[str]:
    """
    Extract the function name from student code using regex.
    Looks for the first 'def function_name(' pattern.
    """
    match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)
    if match:
        return match.group(1)
    return None


def run_code_with_tests(
    code: str,
    test_cases: List[Dict],
    timeout_s: int = 5
) -> Dict[str, Any]:
    """
    Execute student code with test cases in a safe, timeout-controlled environment.
    Windows-compatible using multiprocessing instead of signal.SIGALRM.
    
    Args:
        code: The student's Python code (should define a function)
        test_cases: List of test case dicts with format:
            {
                "input": "'World'",  # Python expression to pass as argument(s)
                "expected": "Hello, World!"  # Expected return value as string
            }
        timeout_s: Maximum execution time in seconds (default: 5)
    
    Returns:
        Dictionary with format:
        {
            "passed": int,  # Number of tests passed
            "failed": int,  # Number of tests failed
            "results": [    # Detailed results for each test
                {
                    "test_number": int,
                    "passed": bool,
                    "input": str,
                    "expected": str,
                    "actual": str,
                    "error": str | None
                }
            ],
            "error": str | None  # Overall execution error if any
        }
    """
    # Validate inputs
    if not code or not code.strip():
        return {
            "passed": 0,
            "failed": len(test_cases),
            "results": [],
            "error": "No code provided"
        }
    
    if not test_cases:
        return {
            "passed": 0,
            "failed": 0,
            "results": [],
            "error": "No test cases provided"
        }
    
    # Create a queue for inter-process communication
    result_queue = multiprocessing.Queue()
    
    # Create and start the execution process
    process = multiprocessing.Process(
        target=_execute_in_process,
        args=(code, test_cases, result_queue)
    )
    
    process.start()
    
    # Wait for process to complete or timeout
    process.join(timeout=timeout_s)
    
    # Check if process is still alive (timeout occurred)
    if process.is_alive():
        # Timeout - terminate the process
        process.terminate()
        process.join(timeout=1)  # Give it 1 second to terminate gracefully
        
        if process.is_alive():
            # Force kill if still alive
            process.kill()
            process.join()
        
        return {
            "passed": 0,
            "failed": len(test_cases),
            "results": [
                {
                    "test_number": i,
                    "passed": False,
                    "input": tc.get("input", ""),
                    "expected": tc.get("expected", ""),
                    "actual": "Timeout",
                    "error": f"Code execution exceeded {timeout_s} seconds"
                }
                for i, tc in enumerate(test_cases, 1)
            ],
            "error": f"Code execution timed out after {timeout_s} seconds"
        }
    
    # Process completed - get results from queue
    try:
        if not result_queue.empty():
            result = result_queue.get(timeout=1)
            return result
        else:
            return {
                "passed": 0,
                "failed": len(test_cases),
                "results": [],
                "error": "No results returned from execution process"
            }
    except Exception as e:
        return {
            "passed": 0,
            "failed": len(test_cases),
            "results": [],
            "error": f"Error retrieving results: {str(e)}"
        }


def check_code_safety(code: str) -> Dict[str, Any]:
    """
    Basic safety check for dangerous operations.
    Note: This is a demo-level check, not production-grade sandboxing.
    
    Args:
        code: The code to check
    
    Returns:
        {
            "safe": bool,
            "warnings": List[str],
            "blocked_operations": List[str]
        }
    """
    dangerous_patterns = [
        'import ',
        '__import__',
        'eval(',
        'exec(',
        'compile(',
        'open(',
        'file(',
        'input(',
        'os.',
        'sys.',
        'subprocess.',
        'socket.',
        'requests.',
        'urllib.',
    ]
    
    warnings = []
    blocked_operations = []
    
    code_lower = code.lower()
    
    for pattern in dangerous_patterns:
        if pattern.lower() in code_lower:
            blocked_operations.append(pattern)
            warnings.append(f"Blocked operation detected: {pattern}")
    
    return {
        "safe": len(blocked_operations) == 0,
        "warnings": warnings,
        "blocked_operations": blocked_operations
    }


if __name__ == "__main__":
    # Test the code runner
    print("Testing code_runner.py...\n")
    
    # Test 1: Simple function
    test_code = """
def greet(name):
    return f"Hello, {name}!"
"""
    
    test_cases = [
        {"input": "'World'", "expected": "Hello, World!"},
        {"input": "'Bob'", "expected": "Hello, Bob!"}
    ]
    
    print("Test 1: Simple greeting function")
    result = run_code_with_tests(test_code, test_cases)
    print(f"Passed: {result['passed']}/{len(test_cases)}")
    print(f"Results: {result['results']}\n")
    
    # Test 2: Math function
    test_code2 = """
def add(a, b):
    return a + b
"""
    
    test_cases2 = [
        {"input": "2, 3", "expected": "5"},
        {"input": "10, 20", "expected": "30"}
    ]
    
    print("Test 2: Addition function")
    result2 = run_code_with_tests(test_code2, test_cases2)
    print(f"Passed: {result2['passed']}/{len(test_cases2)}")
    print(f"Results: {result2['results']}\n")
    
    print("✓ Code runner tests complete")

# Made with Bob
