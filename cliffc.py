import argparse
import os
import sys
from cliff.cliffapi import CliffTranslator

def main():
    # 1. Initialize the Argument Parser
    parser = argparse.ArgumentParser(
        prog="cliff",
        description="The Cliff Programming Language Compiler/Interpreter"
    )

    # 2. Add Arguments
    parser.add_argument(
        "filename", 
        help="The source file to execute (any format)",
        nargs='?' 
    )

    parser.add_argument(
        "-v", "--version", 
        action="version", 
        version="Cliff Language Engine v1.0.4"
    )

    # 3. Parse the arguments
    args = parser.parse_args()

    # 4. If no filename is provided, show help
    if not args.filename:
        parser.print_help()
        return

    # 5. File existence validation
    if not os.path.exists(args.filename):
        print(f"compiler error: (runtime error)")
        print(f"   in command line: {args.filename}")
        print(f"reason: The file was not found.")
        sys.exit(1)

    # 6. Read and Execute (Accepts any extension)
    try:
        with open(args.filename, 'r') as f:
            source = f.read()

        # Initialize the Cliff engine
        interpreter = CliffTranslator()
        interpreter.load_and_run(source)
        
    except Exception as e:
        print(f"compiler error: (unknown error)")
        print(f"reason: Failed to initialize engine: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()