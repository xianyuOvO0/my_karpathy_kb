# debug_compile.py
import sys
sys.path.append('src')
from compiler import load_raw_files, compile_knowledge, save_pages

print("1. 读取 raw/ 目录...")
raw_content = load_raw_files()
print(f"   读取到 {len(raw_content)} 个字符")
if len(raw_content) < 50:
    print("   错误: raw/ 目录内容太少或为空")
    sys.exit(1)

print("2. 调用 API 编译...")
try:
    output = compile_knowledge(raw_content)
    print(f"   API 返回内容长度: {len(output)} 字符")
    print("   返回内容前300字符预览:")
    print(output[:300])
except Exception as e:
    print(f"   API 调用失败: {e}")
    sys.exit(1)

print("3. 保存 wiki 页面...")
save_pages(output)
print("   完成，请检查 wiki 文件夹")