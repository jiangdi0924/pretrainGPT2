"""
项目目录结构生成脚本

该脚本用于生成当前项目的目录和文件结构，方便后续处理和文档生成。
支持排除特定目录和文件，以及自定义输出格式。
"""

import os
import argparse
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# 默认排除的目录和文件
DEFAULT_EXCLUDE = [
    ".git",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "*.so",
    "*.egg",
    "*.egg-info",
    "dist",
    "build",
    "wandb",
    "logs",
    ".ipynb_checkpoints",
]

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="生成项目目录结构")
    parser.add_argument(
        "--path", 
        type=str, 
        default=".", 
        help="要扫描的目录路径，默认为当前目录"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="project_structure.txt", 
        help="输出文件名，默认为project_structure.txt"
    )
    parser.add_argument(
        "--max-depth", 
        type=int, 
        default=None, 
        help="扫描的最大目录深度，默认为无限制"
    )
    parser.add_argument(
        "--exclude", 
        type=str, 
        nargs="+", 
        default=DEFAULT_EXCLUDE,
        help="要排除的目录或文件模式列表"
    )
    parser.add_argument(
        "--include-size", 
        action="store_true", 
        help="是否包含文件大小信息"
    )
    parser.add_argument(
        "--markdown", 
        action="store_true", 
        help="以Markdown格式输出"
    )
    parser.add_argument(
        "--json", 
        action="store_true", 
        help="以JSON格式输出"
    )
    return parser.parse_args()

def should_exclude(path, exclude_patterns):
    """判断路径是否应该被排除"""
    name = os.path.basename(path)
    
    # 检查是否匹配任何排除模式
    for pattern in exclude_patterns:
        # 处理通配符模式
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        # 直接匹配
        elif name == pattern:
            return True
        # 检查路径中是否包含模式
        elif pattern in path:
            return True
    
    return False

def get_size_str(size_bytes):
    """将字节大小转换为可读格式"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def generate_structure(path, exclude_patterns, max_depth=None, include_size=False, current_depth=0):
    """递归生成目录结构"""
    if max_depth is not None and current_depth > max_depth:
        return {}
    
    result = {}
    path = Path(path).resolve()
    
    try:
        for item in sorted(path.iterdir()):
            if should_exclude(str(item), exclude_patterns):
                continue
            
            if item.is_file():
                if include_size:
                    size = item.stat().st_size
                    result[item.name] = get_size_str(size)
                else:
                    result[item.name] = "file"
            elif item.is_dir():
                result[item.name] = generate_structure(
                    item, 
                    exclude_patterns, 
                    max_depth, 
                    include_size, 
                    current_depth + 1
                )
    except PermissionError:
        logger.warning(f"无法访问目录: {path}")
        return {"ERROR": "无法访问"}
    
    return result

def structure_to_text(structure, prefix="", is_last=True, is_root=False):
    """将结构转换为文本格式"""
    lines = []
    
    if is_root:
        lines.append(".")
        prefix = ""
    
    items = list(structure.items())
    
    for i, (name, value) in enumerate(items):
        is_last_item = i == len(items) - 1
        
        # 确定当前行的前缀
        if is_root:
            current_prefix = "├── " if not is_last_item else "└── "
        else:
            current_prefix = prefix + ("└── " if is_last else "├── ")
        
        # 处理文件
        if isinstance(value, str):
            if value != "file":
                line = f"{current_prefix}{name} ({value})"
            else:
                line = f"{current_prefix}{name}"
            lines.append(line)
        # 处理目录
        else:
            lines.append(f"{current_prefix}{name}/")
            
            # 为子项确定前缀
            if is_root:
                next_prefix = "│   " if not is_last_item else "    "
            else:
                next_prefix = prefix + ("    " if is_last else "│   ")
            
            # 递归处理子目录
            sub_lines = structure_to_text(value, next_prefix, is_last_item)
            lines.extend(sub_lines)
    
    return lines

def structure_to_markdown(structure, level=0):
    """将结构转换为Markdown格式"""
    lines = []
    
    for name, value in structure.items():
        indent = "  " * level
        
        # 处理文件
        if isinstance(value, str):
            if value != "file":
                lines.append(f"{indent}- 📄 `{name}` ({value})")
            else:
                lines.append(f"{indent}- 📄 `{name}`")
        # 处理目录
        else:
            lines.append(f"{indent}- 📁 **{name}/**")
            # 递归处理子目录
            sub_lines = structure_to_markdown(value, level + 1)
            lines.extend(sub_lines)
    
    return lines

def structure_to_json(structure):
    """将结构转换为JSON格式"""
    import json
    return json.dumps(structure, ensure_ascii=False, indent=2)

def main():
    """主函数"""
    args = parse_args()
    
    # 解析路径
    path = os.path.abspath(args.path)
    logger.info(f"开始扫描目录: {path}")
    
    # 生成结构
    structure = {os.path.basename(path): generate_structure(
        path, 
        args.exclude, 
        args.max_depth, 
        args.include_size
    )}
    
    # 根据格式输出结果
    if args.json:
        result = structure_to_json(structure)
    elif args.markdown:
        result = "\n".join(structure_to_markdown(structure[os.path.basename(path)]))
    else:
        result = "\n".join(structure_to_text(structure, is_root=True))
    
    # 输出到文件或控制台
    if args.output == "-":
        print(result)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        logger.info(f"目录结构已保存到: {args.output}")

if __name__ == "__main__":
    main()
