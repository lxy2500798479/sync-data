"""
sync_data包的主入口 - 兼容性包装
"""

# 直接导入外层的main函数
import sys
import os

# 添加父目录到path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from main import main

if __name__ == "__main__":
    main()
