import streamlit as st
import openai
import json
import os
from datetime import datetime

# ===== エンドポイント =====
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  # Target URI
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")  # APIキー
MODEL_NAME = "gpt-4o-mini"  # /deployments/XXX/ の XXX
# =======================================

# Azure接続
client = openai.AzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    api_version="2025-01-01-preview"
)

HISTORY_FILE = "recipes.json"

# 履歴関数
@st.cache_data(ttl=1)
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

st.title("🍲 かんたんレシピ生成アプリ")
# 新しいサイドバー（削除機能付き）
with st.sidebar:
    st.header("📋 履歴")
    
    # 更新/全削除ボタン
    col1, col2 = st.columns(2)
    col1.metric("全件数", len(load_history()))
    if col2.button("🗑️ 全削除"):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.cache_data.clear()
        st.success("全履歴削除！")
        st.rerun()
    
    # 個別履歴表示
    history = load_history()
    if history:
        for idx, item in enumerate(reversed(history[-10:]), 1):
            ingredients = item.get('ingredients', '不明')
            col_i, col_d = st.columns([1, 0.1])
            with col_i:
                with st.expander(f"#{idx} {ingredients[:25]}"):
                    st.markdown(item.get('recipe', 'レシピなし'))
            with col_d:
                if st.button("🗑️", key=f"del_{idx}"):
                    # 削除処理
                    new_history = history[:]
                    del new_history[-idx]
                    save_history(new_history)
                    st.rerun()
    else:
        st.info("🍳 まだレシピがありません")


# 食材入力
ingredients = st.text_input("食材を入力してね（例: 卵、牛乳、玉ねぎ）")

if st.button("🥘 この食材でレシピを生成！", use_container_width=True) and ingredients.strip():
    with st.spinner("AIがレシピを考え中..."):
        prompt = f"次の食材で4人分の簡単レシピを日本語で書いて: {ingredients.strip()}"
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        recipe = response.choices[0].message.content
        
        st.success("✅ 生成完了！")
        st.markdown("### 🆕 **今日のレシピ**")
        st.markdown(recipe)
        
        # 履歴保存
        new_item = {
            "ingredients": ingredients.strip(),
            "recipe": recipe,
            "time": datetime.now().strftime("%H:%M")
        }
        history.append(new_item)
        save_history(history)
         
        




