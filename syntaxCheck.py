import re

def find_matching_parenthesis(formula, start_idx):
    """
    Finds the index of the matching closing parenthesis for the parenthesis at start_idx.
    """
    stack = 0
    for i in range(start_idx, len(formula)):
        if formula[i] == '(':
            stack += 1
        elif formula[i] == ')':
            stack -= 1
            if stack == 0:
                return i
    return -1  # No matching parenthesis

def find_unmatched_parenthesis(formula):
    """
    Identifies the location of unmatched or mismatched parentheses in a formula.

    Specifically pinpoints:
    - First unmatched closing ')' (if any).
    - Any unclosed '(' remaining at the end of the formula.

    Returns:
    - A descriptive error message, pinpointing the unmatched parentheses issue.
    """
    # Regex to match all parentheses
    parentheses = re.finditer(r'[()]', formula)
    stack = []
    positions = []  # Keeps track of parenthesis positions for error reporting

    for match in parentheses:
        char = match.group()  # The matched parenthesis '(' or ')'
        pos = match.start()  # Position of the parenthesis

        if char == '(':
            stack.append('(')
            positions.append(pos)  # Push opening parenthesis onto the stack
        elif char == ')':
            if stack:
                stack.pop()  # Pop matching '(' from the stack
                positions.pop()
            else:
                # Found unmatched closing parenthesis
                return f"Unmatched closing parenthesis at position {pos + 1}"

    # If there are still unmatched '(' left in the stack
    if stack:
        position = positions.pop()
        return f"Unmatched opening parenthesis at position {position + 1}"

    # If no unmatched parentheses are found
    return "No unmatched parentheses"

def split_at_top_level(content):
    """
    Splits a string by commas while respecting nested parentheses.
    Commas within parentheses are ignored during splitting.
    """
    parts = []
    current = []
    paren_level = 0

    for char in content:
        if char == ',' and paren_level == 0:
            # If we encounter a top-level comma, split here
            parts.append(''.join(current).strip())
            current = []
        else:
            # Adjust parentheses level when encountering '(' or ')'
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            current.append(char)

    # Add the last part
    if current:
        parts.append(''.join(current).strip())

    return parts

def validate_if(formula):
    """
    Validates the syntax of an `IF` formula, isolating and analyzing incorrectly formed
    conditions, arguments, or structures.

    Always expects the formula to contain errors and flags the most specific type of issue detected.
    """

    while "IF" in formula.upper():  # Keep processing while there's an `IF`
        # Locate the innermost IF statement using parentheses

        if_match = re.search(r'IF\s*', formula, re.IGNORECASE)

        if not if_match:
            break

        no_opening_brackets = re.search(r'\bIF[^(]', formula, re.IGNORECASE)
        if no_opening_brackets:
            return "Error: `IF` found without opening parentheses"

        if formula.count(',') / 3 != 0:
            return "Error: Missing Comma"
        """
        invalid_if_match = re.search(r'(?<![=,& ])IF\(', formula, re.IGNORECASE)

        if invalid_if_match:
            return "Error: `Nested IF formula found without comma,& or = behind`"
        """
        # Start of `IF(`
        start_idx = if_match.start()

        # Find the corresponding closing parenthesis
        end_idx = find_matching_parenthesis(formula, start_idx + 2)
        print(end_idx)
        if end_idx == -1:
            return "Mismatched parentheses in IF formula"

        # Extract the innermost `IF` formula
        inner_formula = formula[start_idx + 3:end_idx].strip()  # Skip `IF(` and trailing `)`

        # Split the arguments of the inner `IF` formula
        args = split_at_top_level(inner_formula)

        # Validate the number of arguments
        if len(args) < 2:
            return f"Incomplete IF formula: expected at least 2 arguments, found {len(args)}"
        elif len(args) > 3:
            return f"Too many arguments in IF formula: expected at most 3, found {len(args)}"

        # Validate each argument
        for i, arg in enumerate(args):
            arg = arg.strip()
            if not arg:
                return f"Missing or empty argument at position {i + 1} in IF formula"

            # Recursively validate nested IFs if they exist
            if "IF(" in arg.upper():
                nested_result = validate_if(arg)
                if nested_result != "Unaccounted For If":  # Propagate the specific error
                    return nested_result

            # Check for mashed content in the argument
            if i == 0:  # First argument is the condition
                if not re.match(r'^[A-Za-z0-9\s><=!+\-*/&|()]+$', arg.strip()):
                    return f"Invalid condition in IF formula: `{arg.strip()}`"
            else:  # Validate the then/else arguments
                if not re.match(r'^[A-Za-z0-9\s><=!+\-*/&|(),]*$', arg.strip()):
                    return f"Invalid argument syntax in IF formula: `{arg.strip()}`"

        # Replace the validated inner formula with a placeholder to continue validating outer IFs
        formula = formula[:start_idx] + "<VALID_IF>" + formula[end_idx + 1:]

    # No error explicitly detected, but this should never happen if you're inducing errors
    return "Generic IF formula error: Still in testing."


def validate_vlookup(formula):
    if formula.count('(') != 1:
        return "Error: Missing Opening Parenthesis"
    elif formula.count(')') != 1:
        return "Error: Missing Closing Parenthesis"
    elif formula.count(',') < 3:
        return "Error: Missing Comma"

def extract_and_validate_nested_functions(parts):
    """
    Extracts and validates all nested functions (e.g., IF, VLOOKUP, etc.)
    in a list of parts from a LET formula.
    """

    for i, part in enumerate(parts):
            if "IF(" in part.upper():
                nested_result = validate_if(part)
                if "Error" in nested_result:
                    return f"Error in nested `IF` formula `{part}`: {nested_result}"
            # Detect and validate nested LET formulas
            elif "LET(" in part.upper():
                nested_result = validate_let(part)
                if "Error" in nested_result:
                    return f"Error in nested `LET` formula `{part}`: {nested_result}"
            # Detect and validate nested VLOOKUP formulas
            elif "VLOOKUP(" in part.upper():
                nested_result = validate_vlookup(part)
                if "Error" in nested_result:
                    return f"Error in nested `VLOOKUP` formula `{part}`: {nested_result}"
    return None  # No errors found


def validate_let(formula):
    """
    Validates the syntax of a LET formula, ensuring:
    - Correct pairing of variables and their values.
    - Proper handling and validation of nested function calls (e.g., IF, VLOOKUP).
    - Correctness of the final computed result.
    """
    # Locate the LET content inside parentheses
    start = formula.find("(")
    end = find_matching_parenthesis(formula, start + 1)

    if end == -1:
        return "Error: Mismatched parentheses in `LET` formula"

    content = formula[start + 1:end].strip()  # Extract everything inside LET()
    parts = split_at_top_level(content)  # Split into top-level sections

    # Validate minimum number of parts (at least one variable-value pair and a result)
    if len(parts) < 3:
        return "Error: Incomplete `LET` formula (missing variables or final result)"

    # **Step 1**: Validate all nested functions (IF, VLOOKUP, etc.)
    nested_validation_error = extract_and_validate_nested_functions(parts)
    if nested_validation_error:
        return nested_validation_error  # Bubble up the error message

    # **Step 2**: Validate variable-value pairs
    variables = parts[:-1]  # Exclude the final result
    final_result = parts[-1]  # The final computed result

    if len(variables) % 2 != 0:
        return "Error: Variables in `LET` formula are not properly paired"

    for i in range(0, len(variables), 2):
        var_name = variables[i].strip()
        var_value = variables[i + 1].strip()

        # Check if the variable name is valid
        if not var_name:
            return f"Error: Empty variable name at position {i // 2 + 1} in `LET` formula"

        # Optionally validate raw variable values (already recursively checked above)
        if not re.match(r'^[A-Za-z0-9\s><=!+\-*/&|().,]*$', var_value):
            return f"Error: Invalid syntax in value assigned to variable `{var_name}`"

    # **Step 3**: Validate the final computed result
    if not final_result.strip():
        return "Error: Missing computed result expression in `LET` formula"

    # Validate nested functions in the final result, if present
    if '(' in final_result and ')' in final_result:
        nested_final_result_validation = extract_and_validate_nested_functions([final_result])
        if nested_final_result_validation:
            return nested_final_result_validation


    return "Generic LET formula error: Still in testing."

def validate_function_syntax(expression):
    """
    Validates the syntax of a generic function (e.g., SUM, AVERAGE, etc.).
    Ensures parentheses and arguments are correctly formatted.
    """
    # Check for proper matching parentheses
    start = expression.find("(")
    end = find_matching_parenthesis(expression, start + 1)

    if start == -1 or end == -1 or start >= end:
        return f"Invalid function syntax: {expression}"

    # Validate the function arguments
    inner_content = expression[start + 1:end]
    args = split_at_top_level(inner_content)

    if len(args) == 0:
        return f"Function has no arguments: {expression}"
    elif any(not arg.strip() for arg in args):
        return f"Function has empty arguments: {expression}"

def validate_formula(formula):
    formula = formula.upper()
    """
    Validates the given formula string, identifying potential syntax errors such as incorrect
    parentheses, missing commas in IF or LET formulas, etc.
    """
    if find_unmatched_parenthesis(formula) != "No unmatched parentheses":
        return find_unmatched_parenthesis(formula)

    # Validate LET formulas
    if formula.count("LET") > 0:
        return validate_let(formula)


    if formula.count('IF') > 0:
        return validate_if(formula)

    if formula.count('VLOOKUP') > 0:
        return validate_vlookup(formula)


    return "Unaccounted For Error Still In Beta"