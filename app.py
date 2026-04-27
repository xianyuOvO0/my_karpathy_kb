# app.py
import sys
sys.path.append('src')

from compiler import run_compile
from query_engine import run_query
from linter import run_lint
from obsidian_compat import run_obsidian_compat

def main():
    print("Karpathy风格知识库系统")
    print("1. 编译知识库 (raw/ -> wiki/)")
    print("2. 问答模式")
    print("3. 健康检查")
    print("4. Obsidian 兼容性设置")
    choice = input("请选择: ")
    
    if choice == '1':
        run_compile()
    elif choice == '2':
        run_query()
    elif choice == '3':
        run_lint()
    elif choice == '4':
        run_obsidian_compat()
    else:
        print("无效选择")

if __name__ == "__main__":
    main()