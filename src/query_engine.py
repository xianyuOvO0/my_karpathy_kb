# src/query_engine.py
import os
import glob
import json
from datetime import datetime
from openai import OpenAI
from config import (
    SILICONFLOW_API_KEY, BASE_URL, MODEL_NAME,
    WIKI_DIR, SESSIONS_DIR, QUERY_TEMPERATURE, QUERY_MAX_TOKENS
)

client = OpenAI(api_key=SILICONFLOW_API_KEY, base_url=BASE_URL)

class KarpathyKB:
    def __init__(self, wiki_dir: str = WIKI_DIR, sessions_dir: str = SESSIONS_DIR):
        self.wiki_dir = wiki_dir
        self.sessions_dir = sessions_dir
        os.makedirs(sessions_dir, exist_ok=True)
        self.full_context = self._load_full_wiki()
    
    def _load_full_wiki(self) -> str:
        all_files = glob.glob(f"{self.wiki_dir}/**/*.md", recursive=True)
        context_parts = []
        for f in all_files:
            with open(f, 'r', encoding='utf-8') as file:
                rel_path = os.path.relpath(f, self.wiki_dir)
                context_parts.append(f"\n--- 来源: {rel_path} ---\n{file.read()}")
        return "\n".join(context_parts)
    
    def query(self, question: str, session_id: str = None, chat_history: list = None) -> str:
        system_prompt = f"""你是基于个人知识库的AI助手。以下是完整的知识库内容（所有wiki页面）。
请**仅基于这些材料**回答问题。如果知识库中没有相关信息，请明确说“知识库中未找到”。
回答时，在末尾用括号标注信息来源，例如 (来源: Transformer.md)。

知识库内容：
{self.full_context}
"""
        messages = [{"role": "system", "content": system_prompt}]
        if chat_history:
            messages.extend(chat_history)
        messages.append({"role": "user", "content": question})
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=QUERY_TEMPERATURE,
            max_tokens=QUERY_MAX_TOKENS
        )
        answer = response.choices[0].message.content
        
        if session_id:
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            history = chat_history if chat_history else []
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": answer})
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        
        return answer

def run_query():
    kb = KarpathyKB()
    print("知识库已加载。输入问题，输入 quit 退出。")
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    history = []
    while True:
        q = input("\n你: ")
        if q.lower() == 'quit':
            break
        ans = kb.query(q, session_id=session_id, chat_history=history)
        print(f"AI: {ans}")
        history.append({"role": "user", "content": q})
        history.append({"role": "assistant", "content": ans})

if __name__ == "__main__":
    run_query()