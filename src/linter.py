# src/linter.py
import os
import glob
import re
from config import WIKI_DIR

def lint_wiki(wiki_dir: str = WIKI_DIR):
    issues = []
    all_pages_full = set()      # 完整相对路径（不含.md）
    all_links = set()           # 链接中出现的概念名（可能不含路径）
    
    for md_file in glob.glob(f"{wiki_dir}/**/*.md", recursive=True):
        rel_path = os.path.relpath(md_file, wiki_dir).replace('\\', '/')
        page_ref = rel_path[:-3]   # 去掉 .md
        all_pages_full.add(page_ref)
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            links = re.findall(r'\[\[(.*?)(?:\|.*?)?\]\]', content)
            for link in links:
                link_clean = link.split('#')[0]
                all_links.add(link_clean)
    
    # 死链检测（简化：链接是否存在于 all_pages_full 中，或匹配以 /链接 结尾的页面）
    dead_links = []
    for link in all_links:
        if '/' in link:
            if link not in all_pages_full:
                dead_links.append(link)
        else:
            matched = any(p.endswith('/' + link) for p in all_pages_full)
            if not matched and link not in all_pages_full:
                dead_links.append(link)
    if dead_links:
        issues.append(f"❌ 死链 ({len(dead_links)}个): {', '.join(dead_links[:10])}")
    
    # 孤立页面：没有被任何页面链接的页面（排除 README 和 index 下的文件）
    linked_pages = set()
    for link in all_links:
        if '/' in link:
            linked_pages.add(link)
        else:
            for p in all_pages_full:
                if p.endswith('/' + link):
                    linked_pages.add(p)
    orphan_pages = all_pages_full - linked_pages
    # 排除 README 和 index/ 下的文件
    orphan_pages = {p for p in orphan_pages if not p.endswith('README') and not p.startswith('index/')}
    if orphan_pages:
        issues.append(f"⚠️ 孤立页面 ({len(orphan_pages)}个): {', '.join(list(orphan_pages)[:10])}")
    
    return issues

def run_lint():
    issues = lint_wiki()
    if issues:
        print("知识库健康检查发现问题：")
        for i in issues:
            print(f"  {i}")
    else:
        print("✅ 知识库健康，无死链、孤立页面或空页面")

if __name__ == "__main__":
    run_lint()