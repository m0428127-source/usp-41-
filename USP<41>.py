import streamlit as st

# --- 工具函數：單位自動轉換 (僅用於顯示) ---
def format_weight(g_value):
    """自動判定顯示 mg 或 g，增加閱讀性"""
    if g_value < 1.0:
        return f"{g_value * 1000:.2f} mg"
    return f"{g_value:.4f} g"

# 設定網頁標題
st.set_page_config(page_title="USP <41> Balances 專業診斷工具 (全 g 版)", layout="wide")

st.title("⚖️ USP 〈41〉 Balances 測試需求診斷工具")
st.caption("工程師專用版 | 單位統一：克 (g) | 依據標準：USP-NF 〈41〉 (Official Feb 1, 2026)")

# --- 側邊欄：天平硬體參數 ---
st.sidebar.header("📋 1. 天平硬體參數")
balance_type = st.sidebar.selectbox(
    "天平類型",
    ["單一量程 (Single range)", "多區間 (Multi-interval)", "多量程 (Multiple range)"]
)
# 所有輸入統一為 g
max_capacity_g = st.sidebar.number_input("最大秤量 Max Capacity (g)", min_value=0.0, value=220.0, step=0.1, format="%.4f")
d_value_g = st.sidebar.number_input("實際分度值 Scale Interval (d) (g)", min_value=0.0, value=0.0001, step=0.0001, format="%.5f", help="例如 0.1mg 請輸入 0.0001")
m_snw_g = st.sidebar.number_input("客戶預期最小淨重 Smallest Net Weight (g)", min_value=0.0, value=0.0200, step=0.001, format="%.4f")

st.sidebar.divider()

# --- 側邊欄：用戶填寫實測使用的砝碼 (全部改為 g) ---
st.sidebar.header("🧪 2. 擬使用測試砝碼 (g)")
st.sidebar.info("請輸入預計在現場使用的砝碼重量 (單位：g)")
user_rep_w_g = st.sidebar.number_input("重複性測試砝碼重量 (g)", min_value=0.0, value=0.1000, step=0.1, format="%.4f")
user_acc_w_g = st.sidebar.number_input("準確度測試砝碼重量 (g)", min_value=0.0, value=200.0, step=10.0, format="%.4f")

# --- 邏輯運算 (內部計算統一用 g) ---
if st.sidebar.button("🛠️ 生成診斷與適宜性判定報告"):
    # 法規常數與限制 (單位 g)
    five_percent_limit_g = max_capacity_g * 0.05
    rep_min_limit_g = 0.1000  # USP 要求不得低於 100mg
    rep_max_limit_g = five_percent_limit_g
    
    acc_min_limit_g = five_percent_limit_g
    acc_max_limit_g = max_capacity_g
    
    # 診斷報告
    st.subheader("📊 USP 〈41〉 測試點位與適宜性診斷")
    
    col1, col2 = st.columns(2)

    # --- 重複性 (Repeatability) 判定 ---
    with col1:
        st.info("### 重複性測試 (Repeatability)")
        st.markdown(f"""
        * **法規推薦區間**：`{format_weight(rep_min_limit_g)}` ~ `{format_weight(rep_max_limit_g)}`
        * **擬使用砝碼**：`{user_rep_w_g:.4f} g`
        """)
        
        # 判定邏輯
        if user_rep_w_g < rep_min_limit_g - 0.000001: # 容許極小誤差
            st.error(f"❌ **不符合規範**：重量低於 0.1 g (100 mg)。")
        elif user_rep_w_g > rep_max_limit_g + 0.000001:
            st.error(f"❌ **不符合規範**：重量超過最大秤量的 5% ({format_weight(rep_max_limit_g)})。")
        else:
            st.success("✅ **適合**：符合 USP <41> 重複性測試要求。")

    # --- 準確度 (Accuracy) 判定 ---
    with col2:
        st.info("### 準確度測試 (Accuracy)")
        st.markdown(f"""
        * **法規推薦區間**：`{format_weight(acc_min_limit_g)}` ~ `{format_weight(acc_max_limit_g)}`
        * **擬使用砝碼**：`{user_acc_w_g:.4f} g`
        """)
        
        # 判定邏輯
        if user_acc_w_g < acc_min_limit_g - 0.000001:
            st.error(f"❌ **不符合規範**：重量低於最大秤量的 5% ({format_weight(acc_min_limit_g)})。")
        elif user_acc_w_g > acc_max_limit_g + 0.000001:
            st.error(f"❌ **不符合規範**：重量超過天平最大秤量。")
        else:
            st.success("✅ **適合**：符合 USP <41> 準確度測試要求。")

    st.divider()

    # --- 3. 綜合能力評估 ---
    st.subheader("🛡️ 天平能力與客戶需求匹配度")
    
    # 計算理論最小重量 (以 s = 0.41d 為基準，單位均為 g)
    # 公式：2 * s / m <= 0.10%  => m >= 2 * s / 0.001
    min_std_g = 0.41 * d_value_g
    min_weight_limit_g = (2 * min_std_g) / 0.001
    
    c1, c2, c3 = st.columns(3)
    c1.metric("天平極限最小淨重 (s=0.41d)", format_weight(min_weight_limit_g))
    c2.metric("客戶預期最小淨重", format_weight(m_snw_g))
    
    # 判定與建議
    if m_snw_g < min_weight_limit_g:
        st.error(f"🚨 **嚴重警告**：客戶要求 ({format_weight(m_snw_g)}) 低於此天平極限 ({format_weight(min_weight_limit_g)})。")
    elif m_snw_g < min_weight_limit_g * 2:
        st.warning("⚠️ **風險提示**：客戶需求接近天平極限，建議增加安全係數。")
    else:
        st.success("✅ **規格匹配**：天平精度足以應付此需求。")

    # --- 自動生成溝通摘要 ---
    st.markdown("---")
    with st.expander("📋 複製溝通摘要 (專業工程師格式)"):
        # 判定符號
        rep_status = "PASS" if rep_min_limit_g <= user_rep_w_g <= rep_max_limit_g else "FAIL"
        acc_status = "PASS" if acc_min_limit_g <= user_acc_w_g <= acc_max_limit_g else "FAIL"
        
        summary = f"""
【USP <41> 天平合規性診斷報告】
■ 天平規格: {max_capacity_g:.2f} g / {d_value_g:.5f} g
■ 重複性測試 (Repeatability):
  - 要求區間: {format_weight(rep_min_limit_g)} ~ {format_weight(rep_max_limit_g)}
  - 擬用砝碼: {user_rep_w_g:.4f} g ({rep_status})
■ 準確度測試 (Accuracy):
  - 要求區間: {format_weight(acc_min_limit_g)} ~ {format_weight(acc_max_limit_g)}
  - 擬用砝碼: {user_acc_w_g:.4f} g ({acc_status})
■ 最小淨重能力判定:
  - 客戶預期需求: {format_weight(m_snw_g)}
  - 法規極限下限: {format_weight(min_weight_limit_g)}
  - 判定結果: {'符合' if m_snw_g >= min_weight_limit_g else '不符合，建議評估高精度型號'}
--------------------------------------------------
診斷時間: {st.date_input("Today").strftime('%Y-%m-%d')}
        """
        st.code(summary)

else:
    st.info("💡 **工程師提醒**：請於側邊欄輸入天平與砝碼數據（全部單位為克 g），系統將自動為您判定適宜性。")
