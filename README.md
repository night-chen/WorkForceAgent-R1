# WorkForceAgent

This is the official implementation of the paper "WorkForceAgent-R1: Incentivizing Reasoning Capability in LLM-based Web Agents via Reinforcement Learning". 
The implementation is based on the [TinyZero repository](https://github.com/Jiayi-Pan/TinyZero), which is a reproduction of [DeepSeek R1 Zero](https://github.com/deepseek-ai/DeepSeek-R1) in countdown and multiplication tasks. 
We reimplement the reward function and the data processing procedure to train a reasoning model based on web-browsing tasks.
The entire repository is built upon [veRL](https://github.com/volcengine/verl).

Through RL, the 7B/14B models have developed reasoning capabilities to analyze the current page observation, potential actions, and possible feedbacks from the environment.
This help the final checkpoints to surpass the existing state-of-the-art models, including powerful commercial models, like gpt-4.


## Installation

```
conda create -n zero python=3.9
# install torch [or you can skip this step and let vllm to install the correct version for you]
pip install torch==2.4.0 --index-url https://download.pytorch.org/whl/cu121
# install vllm
pip3 install vllm==0.6.3 # or you can install 0.5.4, 0.4.2 and 0.3.1
pip3 install ray

# verl
pip install -e .

# flash attention 2
pip3 install flash-attn --no-build-isolation
# quality of life
pip install wandb IPython matplotlib
```

### Run Training
```
conda activate zero
```

For the following code, if you see Out-of-vram, try add `critic.model.enable_gradient_checkpointing=True` to the script.

### Instruct Ablation
We experiment with QWen-2.5-3B Instruct too.
**Data Preparation**
To follow chat template, we need to reprocess the data:
```
conda activate zero
python examples/data_preprocess/workarena.py --template_type=qwen-instruct --local_dir={path_to_your_dataset}
```

**Training**
```
export N_GPUS=2
export BASE_MODEL={path_to_your_model}
export DATA_DIR={path_to_your_dataset}
export ROLLOUT_TP_SIZE=2
export EXPERIMENT_NAME=countdown-qwen2.5-3b-instruct
export VLLM_ATTENTION_BACKEND=XFORMERS

bash ./scripts/train_workarena_7b_grpo.sh
```

## Acknowledge
* We run our experiments based on [veRL](https://github.com/volcengine/verl).

## Citation
```
@misc{zhuang2025workforceagentr1incentivizingreasoningcapability,
      title={WorkForceAgent-R1: Incentivizing Reasoning Capability in LLM-based Web Agents via Reinforcement Learning}, 
      author={Yuchen Zhuang and Di Jin and Jiaao Chen and Wenqi Shi and Hanrui Wang and Chao Zhang},
      year={2025},
      eprint={2505.22942},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2505.22942}, 
}
```
