# config for training GPT-2 (124M) on 1 node with 2X RTX 4090 24GB - Fast Test Version
# launch as: torchrun --standalone --nproc_per_node=2 train.py config/train_gpt2_2gpu.py

wandb_log = True
wandb_project = 'owt'
wandb_run_name='gpt2-124M-2gpu-quick'

# Batch size adjustments for 2x 4090 GPUs (24GB each)
batch_size = 8  # Reduced from 12 to account for less VRAM per GPU
block_size = 1024
# 为加速训练，减少梯度累积步骤
gradient_accumulation_steps = 5  # 从40减少到5，加快单次迭代速度

# 短周期训练参数 - 约30-60分钟完成
max_iters = 1000  # 从600000减少到1000
lr_decay_iters = 1000  # 与max_iters保持一致
warmup_iters = 100  # 减少预热步骤

# 更频繁的评估和日志记录
eval_interval = 100  # 每100次迭代评估一次
eval_iters = 20  # 减少评估迭代次数提高速度
log_interval = 1  # 每次迭代都记录日志

# Optimization
weight_decay = 1e-1

# 禁用动态编译以避免错误
compile = False
