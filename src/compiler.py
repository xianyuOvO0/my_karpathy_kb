# src/compiler.py
import os
import re
import json
from openai import OpenAI
from config import (
    SILICONFLOW_API_KEY, BASE_URL, MODEL_NAME,
    WIKI_DIR, COMPILE_TEMPERATURE, COMPILE_MAX_TOKENS
)
from ingest import load_raw_files

client = OpenAI(api_key=SILICONFLOW_API_KEY, base_url=BASE_URL)

COMPILE_PROMPT = '''
你是一个知识编译器。请将以下原始资料整理成结构化的Markdown知识库，并按照实体类型放入不同子目录。

任务要求：
1. 实体识别与分类：
   - 概念/技术/术语 -> 放入 concepts/ 子目录
   - 人物 -> 放入 people/ 子目录
   - 其他（组织、事件等）-> 放入 others/ 子目录（可选）

2. 文件命名：输出格式为 ---FILE_START--- 子目录/文件名.md ---FILE_START---，例如：
   ---FILE_START--- concepts/注意力机制.md ---FILE_START---
   ---FILE_START--- people/Andrej_Karpathy.md ---FILE_START---

3. 每个文件必须包含YAML Frontmatter，格式如下：
   ---
   title: "概念名称"
   date: 2026-04-20
   tags: [标签1, 标签2]
   sources: ["原始文件1", "原始文件2"]
   ---

4. 正文结构：
   # 标题
   ## 摘要（100字以内）
   ## 详细说明
   ## 相关概念（使用[[双向链接]]，不需要带路径）
   ## 待探索问题（可选）

5. 生成索引文件 README.md 放在 wiki 根目录，列出所有生成的概念和人物，按类别分组。

6. 双向链接：在正文中使用 [[概念名]]，不要包含子目录路径。Obsidian 会自动跨目录解析。

输出格式示例：

---FILE_START--- concepts/注意力机制.md ---FILE_START---
---
title: "注意力机制"
date: 2026-04-20
tags: ["深度学习", "Transformer"]
sources: ["attention-paper.pdf"]
---
# 注意力机制
## 摘要
一种让模型关注输入关键部分的机制...
## 详细说明
...
## 相关概念
- [[Transformer]]
- [[自注意力]]

---FILE_START--- people/Andrej_Karpathy.md ---FILE_START---
---
title: "Andrej Karpathy"
date: 2026-04-20
tags: ["AI", "人物"]
sources: ["wiki"]
---
# Andrej Karpathy
## 摘要
OpenAI 联合创始人，提出长上下文知识库范式...
...

---FILE_START--- README.md ---FILE_START---
# 知识库索引
## 概念
- [[注意力机制]]
## 人物
- [[Andrej_Karpathy]]

原始资料：
{raw_content}
'''

def compile_knowledge(raw_content: str) -> str:
    """调用 LLM 编译知识库，返回原始输出文本"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": COMPILE_PROMPT.format(raw_content=raw_content)}],
        temperature=COMPILE_TEMPERATURE,
        max_tokens=COMPILE_MAX_TOKENS
    )
    return response.choices[0].message.content

def save_pages(output_text: str, wiki_dir: str = WIKI_DIR):
    """解析 LLM 输出，保存多个 .md 文件，并生成 tags.json"""
    os.makedirs(wiki_dir, exist_ok=True)
    
    # 正则提取 ---FILE_START--- 路径/文件名.md ---FILE_START--- 内容
    pattern = r'---FILE_START---\s*([^\n]+?\.md)\s*---FILE_START---\s*\n(.*?)(?=---FILE_START---|$)'
    matches = re.findall(pattern, output_text, re.DOTALL)
    
    if not matches:
        print("警告：未找到任何文件块，请检查LLM输出格式")
        print("输出预览:", output_text[:500])
        return
    
    # 用于收集 tags 信息
    tags_map = {}   # tag -> list of file paths (relative to wiki_dir)
    
    for filepath, content in matches:
        filepath = filepath.strip().replace('\\', '/')
        full_path = os.path.join(wiki_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"生成: {full_path}")
        
        # 提取 frontmatter 中的 tags
        frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            # 简单提取 tags 行: tags: [xxx, yyy]
            tags_match = re.search(r'tags:\s*\[(.*?)\]', frontmatter_text)
            if tags_match:
                tags_str = tags_match.group(1)
                # 解析标签，支持带引号和不带引号
                tags = re.findall(r'["\']?([^"\'\[\],]+)["\']?', tags_str)
                tags = [t.strip() for t in tags if t.strip()]
                for tag in tags:
                    tags_map.setdefault(tag, []).append(filepath)
    
    # 生成 index/tags.json
    index_dir = os.path.join(wiki_dir, "index")
    os.makedirs(index_dir, exist_ok=True)
    tags_json_path = os.path.join(index_dir, "tags.json")
    with open(tags_json_path, 'w', encoding='utf-8') as f:
        json.dump(tags_map, f, ensure_ascii=False, indent=2)
    print(f"生成: {tags_json_path}")

def run_compile():
    print("加载原始资料...")
    raw_content = load_raw_files()
    if len(raw_content) < 100:
        print("警告：raw目录内容很少，请放入一些文档")
        return
    print(f"总字符数: {len(raw_content)}，开始编译...")
    output = compile_knowledge(raw_content)
    save_pages(output)
    print("完成！现在用Obsidian打开wiki/文件夹")

if __name__ == "__main__":
    run_compile()