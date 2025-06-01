import re
import random
import ast
import operator
import difflib
import json

def extract_solution(solution_str):
    """Extract the equation from the solution string."""
    # Remove everything before the first "Assistant:"
    if "Assistant:" in solution_str:
        solution_str = solution_str.split("Assistant:", 1)[1]
    elif "<|im_start|>assistant" in solution_str:
        solution_str = solution_str.split("<|im_start|>assistant", 1)[1]
    # else:
    #     return None
    # solution_str = solution_str.split('\n')[-1]
    final_answer = None
    if '<tool_call>' in solution_str:
        final_answer = solution_str.split('<tool_call>')[1]
        if '</tool_call>' in final_answer:
            final_answer = final_answer.split('</tool_call>')[0]

    # answer_pattern = r'<tool_call>(.*?)</tool_call>'
    # match = re.finditer(answer_pattern, solution_str)
    # matches = list(match)
    # if matches:
    #     final_answer = matches[-1].group(1).strip()
    # else:
    #     final_answer = None
    return final_answer


def validate_action(action, tools):
    """Validate that equation only uses available tools."""
    try:
        start_id = action.find('{')
        end_id = action.rfind('}')
        action = action[start_id:end_id+1]
        action = json.loads(action.strip())
        action = action['tool_calls']
        if type(tools) == str:
            tools = json.loads(tools)
        available_tools = {}
        for tool in tools:
            available_tools[tool['name']] = tool['parameters']
        for step in action:
            if step['name'] not in available_tools:
                return False, ''
            else:
                for param in step['arguments']:
                    if param not in available_tools[step['name']]:
                        return False, ''
        return True, action
    except Exception as e:
        # print(e)
        return False, ''

def evaluate_action(solution, target):
    """Safely evaluate the arithmetic equation using eval() with precautions."""
    try:
        # solution = json.loads(solution_str)
        target = json.loads(target)
        score = 0
        score_per_step = 1 / len(target)
        for idx in range(len(target)):
            if solution[idx]['name'] == target[idx]['name']:
                score_per_step_per_arg = score_per_step / len(target[idx]['arguments'])
                for arg in target[idx]['arguments']:
                    try:
                        if target[idx]['arguments'][arg] == solution[idx]['arguments'][arg]:
                            score += score_per_step_per_arg
                    except:
                        score += 0
        return score           
    except Exception as e:
        return 0

def evaluate_format(equation_str):
    # evaluate if the response is start with <think> and end with </action>
    temp = equation_str
    temp = temp.strip()
    if '<json>' in temp:
        temp = temp.split('<json>')[1]
    else:
        return False, 'No <json> tag found'

    if '</json>' in temp:
        temp = temp.split('</json>')[0]
    else:
        return False, 'No </json> tag found'
    
    # if action is None:
    #     return False, 'No action found'
    # else:
    try:
        action = json.loads(temp)
        return True, action
    except:
        return False, 'Action is not in json format'


def compute_score(solution_str, ground_truth, method='strict', format_score=0.1, score=1.):
    """The scoring function for countdown task.
    
    Args:
        solution_str: the solution text
        ground_truth: dictionary containing target number and available numbers
        method: the method to extract the solution
        format_score: the score for correct format but wrong answer
        score: the score for the correct answer
    """
    target = ground_truth['target']
    tools = ground_truth['candidates']

    # action = solution_str # extract_solution(solution_str=solution_str)
    do_print = random.randint(1, 64) == 1
    action = extract_solution(solution_str=solution_str)
    
    if do_print:
        print(f"--------------------------------")
        print(f"Target: {target}")
        print(f"Solution string: {solution_str}")
        print(f"Extracted action: {action}")

    # flag, temp = evaluate_format(solution_str)
    if action is None:
        if do_print:
            print(f"Format error, no tool call found.")
        return 0
    # else:
    #     action = temp
    #     if do_print:
    #         print(f"Extracted action: {action}")

    flag, action = validate_action(action, tools)
    if not flag:
        if do_print:
            print(f"Invalid action")
        return format_score
    
    try:
        score = evaluate_action(action, target)
        return score + format_score
    except:
        return format_score