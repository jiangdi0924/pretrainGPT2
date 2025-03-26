#!/usr/bin/env python
# 这个脚本设置PyTorch的错误抑制配置，然后运行训练脚本

import os
import sys
import torch._dynamo

# 设置PyTorch在编译失败时自动回退到eager模式
torch._dynamo.config.suppress_errors = True

# 输出配置确认
print("已启用PyTorch编译错误抑制，将在编译失败时自动回退到eager模式")

# 获取命令行参数并传递给train.py
args = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else "config/train_shakespeare_char.py"
cmd = f"python train.py {args}"

# 执行训练命令
print(f"执行命令: {cmd}")
os.system(cmd)
