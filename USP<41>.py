import streamlit as st

st.set_page_config(page_title="USP <41> 合規套件", layout="centered")

st.title("⚖️ USP 〈41〉 & 〈1251〉 天平評估工具")
st.markdown("""
歡迎使用此評估系統。請根據您的需求選擇下方的功能模組：

### 🛠️ [完整評估模式] 
適合，了解符合 USP<41> 重複性與準確度具體測試需求(砝碼選用以及限制)
### 🤝 [快速模式] 
適合，快速評估天平在 USP<41> 規範下，您實際秤重需求是否符合理論最小秤重量。
""")

st.info("💡 提示：請使用左側選單切換模式。")
