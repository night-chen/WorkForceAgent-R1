# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
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
"""
Preprocess the GSM8k dataset to parquet format
"""

import re
import os
import datasets
from datasets import load_dataset

from verl.utils.hdfs_io import copy, makedirs
import argparse

prefix_base = """A conversation between User and Assistant. The user asks a question, and the Assistant solves it. The assistant first thinks about the reasoning process in the mind and then provides the user with the answer.
User: {user}
Assistant: Let me solve this step by step.
<think>"""

prefix_qwen_instruct = """<|im_start|>system
You are a helpful assistant. You first thinks about the reasoning process in the mind and then provides the user with the answer.<|im_end|>
<|im_start|>user
{user}<|im_end|>
<|im_start|>assistant
Let me solve this step by step.
<think>"""

def extract_solution(solution_str):
    # extract the solution between special tokens of <action> and </action>
    solution = solution_str.split('<action>')[1].split('</action>')[0]
    return solution
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local_dir', default='~/data/gsm8k')
    parser.add_argument('--hdfs_dir', default=None)
    parser.add_argument("--prefix_style", type=str, default="base")

    args = parser.parse_args()

    num_few_shot = 5
    data_source = '<DATA_PATH>'

    full_dataset = datasets.load_dataset(data_source)['train']

    train_dataset = full_dataset.train_test_split(test_size=0.1)['train']
    test_dataset = full_dataset.train_test_split(test_size=0.1)['test']

    # instruction_following = "Let's think step by step and output the final answer after \"####\"."
    if args.prefix_style == 'base':
        prefix_template = prefix_base
    elif args.prefix_style == 'qwen-instruct':
        prefix_template = prefix_qwen_instruct
    # add a row to each data item that represents a unique il.....;jud
    def make_map_fn(split):

        def process_fn(example, idx):
            question_raw = example.pop('prompt')

            question = prefix_template.format(user=question_raw)

            answer_raw = example.pop('action')
            solution = extract_solution(answer_raw)
            data = {
                "data_source": 'webagent',
                "prompt": [{
                    "role": "user",
                    "content": question,
                }],
                "ability": "math",
                "reward_model": {
                    "style": "rule",
                    "ground_truth": solution
                },
                "extra_info": {
                    'split': split,
                    'index': idx,
                    'answer': answer_raw,
                    "question": question_raw,
                }
            }
            return data

        return process_fn

    train_dataset = train_dataset.map(function=make_map_fn('train'), with_indices=True)
    test_dataset = test_dataset.map(function=make_map_fn('test'), with_indices=True)

    local_dir = args.local_dir
    hdfs_dir = args.hdfs_dir

    train_dataset.to_parquet(os.path.join(local_dir, 'train.parquet'))
    test_dataset.to_parquet(os.path.join(local_dir, 'test.parquet'))

    if hdfs_dir is not None:
        makedirs(hdfs_dir)

        copy(src=local_dir, dst=hdfs_dir)
