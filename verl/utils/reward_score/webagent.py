import re
import random
import ast
import operator
import difflib

def extract_solution(solution_str):
    """Extract the equation from the solution string."""
    # Remove everything before the first "Assistant:"
    if "Assistant:" in solution_str:
        solution_str = solution_str.split("Assistant:", 1)[1]
    elif "<|im_start|>assistant" in solution_str:
        solution_str = solution_str.split("<|im_start|>assistant", 1)[1]
    else:
        return None
    # solution_str = solution_str.split('\n')[-1]

    # answer_pattern = r'<action>(.*?)</action>'
    # match = re.finditer(answer_pattern, solution_str)
    # matches = list(match)
    # if matches:
    #     final_answer = matches[-1].group(1).strip()
    # else:
    #     final_answer = None
    return solution_str


def validate_equation(equation_str, available_numbers):
    """Validate that equation only uses available numbers and each number once."""
    try:
        # Extract all numbers from the equation
        numbers_in_eq = [int(n) for n in re.findall(r'\d+', equation_str)]
        
        # Check if all numbers in equation are available
        available_numbers = sorted(available_numbers)
        numbers_in_eq = sorted(numbers_in_eq)
        
        # Each number should be used exactly once
        return numbers_in_eq == available_numbers
    except:
        return False


def evaluate_equation(equation_str):
    """Safely evaluate the arithmetic equation using eval() with precautions."""
    try:
        # Define a regex pattern that only allows numbers, operators, parentheses, and whitespace
        allowed_pattern = r'^[\d+\-*/().\s]+$'
        if not re.match(allowed_pattern, equation_str):
            raise ValueError("Invalid characters in equation.")

        # Evaluate the equation with restricted globals and locals
        result = eval(equation_str, {"__builtins__": None}, {})
        return result
    except Exception as e:
        return None

def evaluate_format(equation_str):
    # evaluate if the response is start with <think> and end with </action>
    temp = equation_str
    temp = temp.strip()
    # if '<think>' in temp:
    #     pos1 = temp.find('<think>')
    #     temp = temp[pos1:]
    # else:
    #     return False, 'no token <think>'

    # if '</action>' in temp:
    #     pos2 = temp.rfind('</action>')
    #     temp = temp[:pos2 + len('</action>')]
    # else:
    #     return False, 'no token </action>'
    
    # check if <action> </action> <think> </think> only appear once in the response
    # if temp.count('<think>') != 1 or temp.count('</think>') != 1 or temp.count('</action>') != 1 or temp.count('<action>') != 1:
    #     return False
    
    # if '</think>' in temp and '<action>' in temp:
    #     if temp.find('</think>') < temp.find('<action>'):
    #         action = temp.split('<action>')[1].split('</action>')[0]
    #         return True, action
    if '<action>' in temp and '</action>' in temp:
        action = temp.split('<action>')[1].split('</action>')[0]
        pos = temp.find('</action>')
        postfix = temp[pos+len('</action'):].strip()
        if len(postfix) > 10:
            return True, action
        else:
            return True, 'too long generation'
    else:
        return False, 'no token <action> or </action>'


def compute_score(solution_str, ground_truth, method='strict', format_score=0.1, score=1.):
    """The scoring function for countdown task.
    
    Args:
        solution_str: the solution text
        ground_truth: dictionary containing target number and available numbers
        method: the method to extract the solution
        format_score: the score for correct format but wrong answer
        score: the score for the correct answer
    """
    action = extract_solution(solution_str=solution_str)
    do_print = random.randint(1, 64) == 1
    
    if do_print:
        print(f"--------------------------------")
        print(f"Target: {ground_truth}")
        print(f"Solution string: {solution_str}")
        print(f"Extracted action: {action}")

    # if action is None:
    #     if do_print:
    #         print(f"No action found")
    #     return 0
    flag, temp = evaluate_format(action)
    # Evaluate equation
    if flag:
        if temp == 'too long generation':
            return 2 * format_score
        action = temp
        # print(action.strip(), ground_truth.strip())
        # input()
        # action = temp
        a1 = action.split('(')[0].strip()
        a2 = ground_truth.split('(')[0].strip()
        if a1 != a2:
            return format_score
        else:
            b1 = action.split('(')[1].split(')')[0].strip()
            b2 = ground_truth.split('(')[1].split(')')[0].strip()
            if b1 == b2:
                return 1
            else:
                return 2 * format_score
        # matcher = difflib.SequenceMatcher(None, action.strip(), ground_truth.strip())
        # similarity_score = matcher.ratio()
        # return similarity_score
    else:
        return -1
