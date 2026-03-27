import re
import sys
import os

class CliffInternal:
    def __init__(self):
        self.functions = {}  # Stores Cliff 'void' blocks
        self.commands = {}   # Stores Syntax keywords: { 'keyword': python_function }
        
        # Register Default Built-in Syntax
        self.register_command("typew", self._builtin_typew)
        self.register_command("print", self._builtin_print)

    def register_command(self, keyword, func):
        """Allows modules to inject new syntax/functions."""
        self.commands[keyword] = func

    def _builtin_typew(self, line, line_num):
        match = re.search(r'typew\{(.*?)\}', line)
        if match:
            content = match.group(1)
            if not (content.startswith('"') and content.endswith('"')):
                self.report_error("type error", line_num, line, "typew requires quotes")
            print(content.strip('"'))
        else:
            self.report_error("syntax error", line_num, line, "Malformed typew")

    def _builtin_print(self, line, line_num):
        match = re.search(r'class=(.*?)\}', line)
        if match:
            self.execute_block(match.group(1), line_num, line)
        else:
            self.report_error("type error", line_num, line, "print requires 'class='")

    def report_error(self, error_type, line_num, code, reason):
        print(f"\ncompiler error: ({error_type})")
        print(f"   in line {line_num}: {code.strip()}")
        print(f"reason: {reason}")
        sys.exit(1)

    def execute_block(self, block_name, caller_line, caller_code):
        if block_name in self.functions:
            for line_num, line_code in self.functions[block_name]:
                self.parse_line(line_num, line_code)
        else:
            self.report_error("runtime error", caller_line, caller_code, f"void {{{block_name}}} not found")

    def parse_line(self, line_num, line):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("//") or line.startswith("import") or line.startswith("void") or line == "end()":
            return

        # DYNAMIC SYNTAX CHECK
        found_command = False
        for keyword in self.commands:
            if line.startswith(keyword):
                self.commands[keyword](line, line_num)
                found_command = True
                break
        
        if not found_command:
            self.report_error("unknown error", line_num, line, f"'{line.split('{')[0]}' is not a registered command.")

class CliffTranslator:
    def __init__(self):
        self.api = CliffInternal()

    def load_and_run(self, main_code):
        self.process_code(main_code)
        if "Stuff" in self.api.functions:
            self.api.execute_block("Stuff", "Internal", "Entry Point")
        else:
            print("compiler error: (runtime error)\nreason: No void {Stuff} found.")

    def process_code(self, code):
        lines = code.splitlines()
        current_void = None
        
        for index, line_content in enumerate(lines):
            line_num = index + 1
            clean_line = line_content.strip()
            
            if clean_line.startswith("import"):
                # Handle standard .cliff imports
                match = re.search(r'import\{(.*?)\}', clean_line)
                if match:
                    path = match.group(1)
                    if path.endswith(".py"): 
                        self.load_python_module(path)
                    elif os.path.exists(path):
                        with open(path, 'r') as f: self.process_code(f.read())
                continue

            if clean_line.startswith("void"):
                name = re.search(r'\{(.*?)\}', clean_line).group(1)
                current_void = name
                self.api.functions[name] = []
            elif clean_line == "end()":
                current_void = None
            elif current_void and clean_line:
                self.api.functions[current_void].append((line_num, clean_line))

    def load_python_module(self, path):
        """Loads a Python file that adds new syntax to Cliff."""
        import importlib.util
        module_name = os.path.basename(path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Call the module's setup function to register new commands
        if hasattr(module, "setup"):
            module.setup(self.api)