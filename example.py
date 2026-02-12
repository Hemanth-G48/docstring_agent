"""Example usage of the docstring generation agent."""

from app import DocstringOrchestrator, DocstringStyle


def main():
    # Example 1: Process a Python file
    print("=== Example 1: Process a File ===")
    orchestrator = DocstringOrchestrator(
        style=DocstringStyle.GOOGLE,
        max_iterations=2,
        quality_threshold=0.8
    )
    
    # This would process an actual file
    # result = orchestrator.process_file("my_module.py")
    
    # Example 2: Process code directly
    print("\n=== Example 2: Process Code Directly ===")
    source_code = '''
def calculate_area(length, width):
    return length * width

def greet_user(name, greeting="Hello"):
    message = f"{greeting}, {name}!"
    return message
'''
    
    result = orchestrator.process_code(source_code)
    print("Enhanced code:")
    print(result)
    
    # Example 3: Get detailed results
    print("\n=== Example 3: Get Results ===")
    # results = orchestrator.get_results("my_module.py")
    # for r in results:
    #     print(f"Function: {r.element_name}")
    #     print(f"Confidence: {r.confidence_score:.2%}")
    #     print(f"Warnings: {r.warnings}")
    #     print()


if __name__ == "__main__":
    main()
