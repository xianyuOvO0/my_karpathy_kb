# src/obsidian_compat.py
import os
import json
from config import WIKI_DIR

def ensure_obsidian_config(wiki_dir: str = WIKI_DIR):
    """为 Obsidian 创建基本的 .obsidian 配置文件，提升兼容性"""
    obsidian_dir = os.path.join(wiki_dir, ".obsidian")
    os.makedirs(obsidian_dir, exist_ok=True)
    
    # 创建 app.json
    app_json_path = os.path.join(obsidian_dir, "app.json")
    if not os.path.exists(app_json_path):
        app_config = {
            "promptDelete": False,
            "alwaysUpdateLinks": True,
            "newFileLocation": "current",
            "attachmentFolderPath": "./attachments"
        }
        with open(app_json_path, 'w', encoding='utf-8') as f:
            json.dump(app_config, f, indent=2)
        print(f"生成 Obsidian 配置: {app_json_path}")
    
    # 创建 core-plugins.json（启用图谱等核心插件）
    plugins_path = os.path.join(obsidian_dir, "core-plugins.json")
    if not os.path.exists(plugins_path):
        plugins_config = {
            "file-explorer": True,
            "global-search": True,
            "switcher": True,
            "graph": True,
            "backlink": True,
            "outgoing-link": True,
            "tag-pane": True,
            "page-preview": True,
            "templates": True,
            "note-composer": True,
            "command-palette": True,
            "editor-status": True,
            "markdown-importer": False,
            "word-count": True,
            "open-with-default-app": True,
            "file-recovery": True
        }
        with open(plugins_path, 'w', encoding='utf-8') as f:
            json.dump(plugins_config, f, indent=2)
        print(f"生成 Obsidian 核心插件配置: {plugins_path}")

def run_obsidian_compat():
    ensure_obsidian_config()
    print("Obsidian 兼容性处理完成，现在可以用 Obsidian 打开 wiki/ 文件夹了")

if __name__ == "__main__":
    run_obsidian_compat()