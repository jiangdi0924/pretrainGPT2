# 在1个节点的2张RTX 4090 24GB上训练GPT-2 (124M)的配置
# 启动命令: torchrun --standalone --nproc_per_node=2 train.py config/train_gpt2_2gpu.py

wandb_log = True
wandb_project = 'owt'
wandb_run_name='gpt2-124M-2gpu'

# 针对2x 4090 GPU (各24GB)的批量大小调整
batch_size = 8  # 从12减少到8以适应每个GPU较少的显存
block_size = 1024
# 原始设置: 5 * 8 = 40，现在我们使用 5 * 4 * 8/2 = 80
# 这保持总批量大小相似: batch_size * gradient_accumulation_steps * num_gpus
gradient_accumulation_steps = 20 * 2  # 5 * 8 (原始) * (8/2) / (12/8)

# 训练参数
max_iters = 600000
lr_decay_iters = 600000

# 评估和日志记录
eval_interval = 1000
eval_iters = 200
log_interval = 10

# 优化设置
weight_decay = 1e-1