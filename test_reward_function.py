from verl.utils.reward_score.function_calling import compute_score
import re
answer = '''<json>
[{"name": "live_giveaways_by_type", "arguments": {"type": "alpha"}}, {"name": "live_giveaways_by_type", "arguments": {"type": "game"}}]
<json>'''
answer_pattern = r'<json>(.*?)</json>'
match = re.finditer(answer_pattern, answer)
matches = list(match)
print(matches)
solution = {
    "target": '''[{"name": "live_giveaways_by_type", "arguments": {"type": "beta"}}, {"name": "live_giveaways_by_type", "arguments": {"type": "game"}}]''',
    "candidates": '''[{"name": "live_giveaways_by_type", "description": "Retrieve live giveaways from the GamerPower API based on the specified type.", "parameters": {"type": {"description": "The type of giveaways to retrieve (e.g., game, loot, beta).", "type": "str", "default": "game"}}}]'''
}
print(compute_score(answer, solution))

# from verl.utils.reward_score.webagent import compute_score
# answer = '''<|im_start|>assistant
# <think>
# Okay, so I'm trying to create a new change request in ServiceNow based on the user's instructions. The goal is to fill out various fields with specific values. Let me go through each field step by step to make sure I understand what needs to be done.

# First, I look at the current state of the page. The focused element is the "Number" field with the value 'CHG0030076'. That's already set, so I don't need to change that. Next, I need to fill in the "Short description" field. The user provided the value "Scheduled maintenance on database server - bond_trading_uk". I see that the bid for the "Short description" field is 'a526', which is a textbox. So, I should use the fill action to input this value.

# After that, there are several other fields to fill, like "Test plan", "Backout plan", "Close notes", "Description", "Risk", "Impact", "Implementation plan", "Category", and "Configuration item". Each of these has specific values provided. I'll need to locate their respective bids and use the appropriate actions, whether it's filling in text or selecting options from dropdowns.

# I also notice that some fields like "Service", "Service offering", and "Assignment group" are set to empty strings, so I'll leave those as they are unless the system requires any changes. For the "Configuration item", the value is "bond_trade_aus", so I'll need to ensure that's correctly filled in, possibly using a searchbox if it's a lookup field.

# I should proceed methodically, filling each field one by one, making sure not to miss any. Since the system might have dynamic elements or auto-suggestions, I need to be cautious and possibly wait for the page to update after each action. It's important to verify that each field is correctly populated before moving on to the next to avoid errors during submission.

# Once all fields are filled, I'll look for the "Submit" button to complete the change request. I should also be prepared to handle any validations or additional steps that might pop up after submission.
# </think>
# <action>
# click('a324')
# </action>


# '''
# import re
# answer_pattern = r'<action>(.*?)</action>'
# match = re.finditer(answer_pattern, answer)
# matches = list(match)
# print(matches)
# solution = '''click('a526')'''
# print(compute_score(answer, solution))