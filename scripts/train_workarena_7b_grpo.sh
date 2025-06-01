export N_GPUS=4
###
 # @Author: yipin 1259478761@qq.com
 # @Date: 2025-05-20 08:44:08
 # @LastEditors: yipin 1259478761@qq.com
 # @LastEditTime: 2025-05-20 08:44:33
 # @FilePath: /projects/WorkForceAgent/scripts/train_workarena_7b_grpo.sh
 # @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
### 
export BASE_MODEL=<MODEL_PATH>
export DATA_DIR=<DATA_PATH>
export ROLLOUT_TP_SIZE=4
export EXPERIMENT_NAME=workarena-qwen2.5-7b-warmup-grpo-0512
export VLLM_ATTENTION_BACKEND=XFORMERS
CUDA_VISIBLE_DEVICES=4,5,6,7 python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    data.train_files=$DATA_DIR/train.parquet \
    data.val_files=$DATA_DIR/test.parquet \
    data.train_batch_size=128 \
    data.val_batch_size=128 \
    data.max_prompt_length=13312 \
    data.max_response_length=1024 \
    actor_rollout_ref.model.path=$BASE_MODEL \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.use_dynamic_bsz=True \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.actor.ppo_mini_batch_size=8 \
    actor_rollout_ref.actor.ppo_micro_batch_size=8 \
    actor_rollout_ref.actor.use_kl_loss=True \
    actor_rollout_ref.actor.kl_loss_coef=0.001 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.rollout.log_prob_micro_batch_size=8 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=$ROLLOUT_TP_SIZE \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
    actor_rollout_ref.ref.log_prob_micro_batch_size=8 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=True \
    actor_rollout_ref.actor.fsdp_config.grad_offload=True \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    actor_rollout_ref.rollout.n=8 \
    actor_rollout_ref.rollout.temperature=0.6 \
    critic.model.enable_gradient_checkpointing=True \
    critic.optim.lr=1e-5 \
    critic.model.path=$BASE_MODEL \
    critic.ppo_micro_batch_size=8 \
    critic.model.enable_gradient_checkpointing=True \
    algorithm.kl_ctrl.kl_coef=0.001 \
    trainer.logger=['wandb'] \
    +trainer.val_before_train=False \
    trainer.default_hdfs_dir=null \
    trainer.n_gpus_per_node=$N_GPUS \
    trainer.nnodes=1 \
    trainer.save_freq=100 \
    trainer.test_freq=100 \
    trainer.project_name=TinyZero \
    trainer.experiment_name=$EXPERIMENT_NAME \
    trainer.total_epochs=15 2>&1 | tee verl_demo.log
