#!/usr/bin/env python3
"""
Runner script for StateTalk Compiler
"""

import sys
import os

def main():
    print("=" * 50)
    print("StateTalk Compiler - CS4031 Project")
    print("=" * 50)
    
    # Import after printing header to avoid error message confusion
    try:
        from compiler import StateTalkCompiler
    except Exception as e:
        print(f"\n❌ Failed to import compiler: {e}")
        print("\nMake sure you have PLY installed:")
        print("  pip install ply")
        sys.exit(1)
    
    compiler = StateTalkCompiler()
    
    # Check if example.st exists
    if not os.path.exists("example.st"):
        print("\n❌ example.st not found!")
        print("Creating a simple example.st file...")
        
        simple_example = '''state Welcome {
    prompt "Hello! What's your name?"
    store input as $name (str)
    prompt "Nice to meet you, {$name}!"
    prompt "This is a simple StateTalk example."
    set $current_state = "END"
}'''
        
        with open("example.st", "w") as f:
            f.write(simple_example)
        print("✓ Created example.st")
    
    # Compile the example
    print("\nCompiling example.st...")
    success = compiler.compile("example.st", "pizzabot.py")
    
    if success:
        print("\nCompilation successful!")
        print("\nGenerated files:")
        print("   - pizzabot.py (executable chatbot)")
        print("\nTo run the chatbot:")
        print("   python pizzabot.py")
    else:
        print("\nCompilation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()