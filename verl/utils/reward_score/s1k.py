# Copyright 2024 Bytedance Ltd. and/or its affiliates
# Copyright 2022 EleutherAI and the HuggingFace Inc. team. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Adapted from https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/hendrycks_math/utils.py

from typing import List
from .gpt_sampler import ChatCompletionSampler
gpt_sampler = ChatCompletionSampler()

def compute_score(solution_str, ground_truth) -> float:
    retval = 0.
    try:
        string_in_last_boxed = last_boxed_only_string(solution_str)
        if string_in_last_boxed is not None:
            answer = remove_boxed(string_in_last_boxed)
            if is_equiv(answer, ground_truth):
                retval = 1.
            else:
                retval = 0.1
    except Exception as e:
        print(e)

    return retval


# string normalization from https://github.com/EleutherAI/lm-evaluation-harness/blob/master/lm_eval/tasks/hendrycks_math.py
# def is_equiv(str1, str2, verbose=False):
#     if str1 is None and str2 is None:
#         print("WARNING: Both None")
#         return True
#     if str1 is None or str2 is None:
#         return False

#     try:
#         ss1 = strip_string(str1)
#         ss2 = strip_string(str2)
#         if verbose:
#             print(ss1, ss2)
#         return ss1 == ss2
#     except Exception:
#         return str1 == str2

def is_equiv(str1, str2):
    if str1 is None and str2 is None:
        print("WARNING: Both None")
        return True
    if str1 is None or str2 is None:
        return False

    if str1.isdigit() and str2.isdigit():
        str1 = str(int(str1))
    elif gpt_sampler is not None:
        options = [str2]
        options_str = "[" + ", ".join(["'" + str(o) + "'" for o in options]) + "]"
        idx = extract_answer_idx(options_str, str1)
        if idx != "-1":
            if idx.isdigit():
                idx = int(idx) - 1
                if len(options) > idx >= 0:
                    str1 = options[idx]
                else:
                    print("Warning: Index out of bounds; leaving answer unchanged\n", str1, "\noptions", options_str, "\ndoc['answer']", str2, "\nidx", idx)
            else:
                print("Warning: Processing did not produce integer index\na", str1, "\noptions", options_str, "\ndoc['answer']", str2)
    
    return str1 == str2


EXTRACTION_TEMPLATE_IDX = r"""
Look at the following attempt by a student and extract the student's answer. If it is equivalent (ignoring trivial simplifications) to any of the provided options, return the index of that option starting from 1. Else, return -1.

Examples:

    Options: ['2x+4', '2x', '4x']
    Attempt: The answer is 3+2x.

-1
(the student's answer is not among the options)

    Options: ['72,000']
    Attempt: 72000 \text{ cents}.

1
(always give benefit of the doubt to units and ignore formatting which makes the 1st option match)

    Options: ['2/(-3)', '2/3']
    Attempt: -1 * 2/3

1
(the 1st option matches after trivial simplifications which are fine)

    Options: ['x=5']
    Attempt: 5

1

    Options: ['\dfrac{33}{100}']
    Attempt: 0.33

1

    Options: ['75^\circ']
    Attempt: ...various calculations and explanations...hence the answer is $\boxed{x in 75}$.

1

    Options: ['(1,-3)', '(1,-1)', '(1,0)', '(1,-2)']
    Attempt: -2, 1

4
(ignore whitespace and other formatting which makes the 4th option match)

    Options: ['-2,1']
    Attempt: 1, -2

1
(likely a problem where multiple solutions are possible thus ignore order)

    Options: ['12']
    Attempt: ...$\boxed{12^{\mathrm{th}}}$.

1

    Options: ['2516_8']
    Attempt: 2516

1
(give benefit of the doubt for different bases)

    Options: ['11\sqrt2']
    Attempt: 11\sqrt{2}

1

    Options: ['11,\! 111,\! 111,\! 100']
    Attempt: 11111111100

1

    Options: ['\text{Navin}']
    Attempt: ...it is navin.

1

---

YOUR TASK


Respond with only the index of the matching option starting from 1 or -1 if there is absolutely no reasonable match. Do not include a rationale.

    Options: %(expression1)s
    Attempt: %(expression2)s
""".strip()


# https://github.com/openai/simple-evals/blob/580d359553a88584c11ce4efb97d49d9386e0d9e/common.py#L153C1-L156C45
def extract_answer_idx(options: List[str], attempt: str):
    prompt = EXTRACTION_TEMPLATE_IDX % {"expression1": options, "expression2": attempt}
    response = gpt_sampler([dict(content=prompt, role="user")])
    return response


def remove_boxed(s):
    if "\\boxed " in s:
        left = "\\boxed "
        assert s[:len(left)] == left
        return s[len(left):]

    left = "\\boxed{"

    assert s[:len(left)] == left
    assert s[-1] == "}"

    return s[len(left):-1]


def last_boxed_only_string(string):
    idx = string.rfind("\\boxed")
    if "\\boxed " in string:
        return "\\boxed " + string.split("\\boxed ")[-1].split("$")[0]
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1

    if right_brace_idx is None:
        retval = None
    else:
        retval = string[idx:right_brace_idx + 1]

    return retval


def fix_fracs(string):
    substrs = string.split("\\frac")
    new_str = substrs[0]
    if len(substrs) > 1:
        substrs = substrs[1:]
        for substr in substrs:
            new_str += "\\frac"
            if substr[0] == "{":
                new_str += substr
            else:
                try:
                    assert len(substr) >= 2
                except AssertionError:
                    return string
                a = substr[0]
                b = substr[1]
                if b != "{":
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}{" + b + "}" + post_substr
                    else:
                        new_str += "{" + a + "}{" + b + "}"
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}" + b + post_substr
                    else:
                        new_str += "{" + a + "}" + b
    string = new_str
    return string


def fix_a_slash_b(string):
    if len(string.split("/")) != 2:
        return string
    a = string.split("/")[0]
    b = string.split("/")[1]
    try:
        a = int(a)
        b = int(b)
        assert string == "{}/{}".format(a, b)
        new_string = "\\frac{" + str(a) + "}{" + str(b) + "}"
        return new_string
    except AssertionError:
        return string


def remove_right_units(string):
    # "\\text{ " only ever occurs (at least in the val set) when describing units
    if "\\text{ " in string:
        splits = string.split("\\text{ ")
        assert len(splits) == 2
        return splits[0]
    else:
        return string


def fix_sqrt(string):
    if "\\sqrt" not in string:
        return string
    splits = string.split("\\sqrt")
    new_string = splits[0]
    for split in splits[1:]:
        if split[0] != "{":
            a = split[0]
            new_substr = "\\sqrt{" + a + "}" + split[1:]
        else:
            new_substr = "\\sqrt" + split
        new_string += new_substr
    return new_string


def strip_string(string):
    # linebreaks
    string = string.replace("\n", "")

    # remove inverse spaces
    string = string.replace("\\!", "")

    # replace \\ with \
    string = string.replace("\\\\", "\\")

    # replace tfrac and dfrac with frac
    string = string.replace("tfrac", "frac")
    string = string.replace("dfrac", "frac")

    # remove \left and \right
    string = string.replace("\\left", "")
    string = string.replace("\\right", "")

    # Remove circ (degrees)
    string = string.replace("^{\\circ}", "")
    string = string.replace("^\\circ", "")

    # remove dollar signs
    string = string.replace("\\$", "")

    # remove units (on the right)
    string = remove_right_units(string)

    # remove percentage
    string = string.replace("\\%", "")
    string = string.replace("\%", "")  # noqa: W605

    # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively, add "0" if "." is the start of the string
    string = string.replace(" .", " 0.")
    string = string.replace("{.", "{0.")
    # if empty, return empty string
    if len(string) == 0:
        return string
    if string[0] == ".":
        string = "0" + string

    # to consider: get rid of e.g. "k = " or "q = " at beginning
    if len(string.split("=")) == 2:
        if len(string.split("=")[0]) <= 2:
            string = string.split("=")[1]

    # fix sqrt3 --> sqrt{3}
    string = fix_sqrt(string)

    # remove spaces
    string = string.replace(" ", "")

    # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc. Even works with \frac1{72} (but not \frac{72}1). Also does a/b --> \\frac{a}{b}
    string = fix_fracs(string)

    # manually change 0.5 --> \frac{1}{2}
    if string == "0.5":
        string = "\\frac{1}{2}"

    # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple cases fix in case the model output is X/Y
    string = fix_a_slash_b(string)

    return string
