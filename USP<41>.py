import streamlit as st

# --- 工具函數：單位自動轉換 ---
def format_weight(mg_value):
    """自動判定顯示 mg 或 g"""
    if mg_value >= 1000:
        return f"{mg_value / 1000:.4f} g"
    return f"{mg_value:.2f} mg"

# 設定網頁標題
st.set_page_config(page_title="USP <41> Balances 專業診斷與判定工具", layout="wide")

st.title("⚖️ USP 〈41〉 Balances 測試需求診斷工具")
st.caption("工程師專用版 | 依據標準：USP-NF 〈41〉 (Official Feb 1, 2026)")

# --- 側邊欄：天平硬體參數 ---
st.sidebar.header("📋 1. 天平硬體參數")
balance_type = st.sidebar.selectbox(
    "天平類型",
    ["單一量程 (Single range)", "多區間 (Multi-interval)", "多量程 (Multiple range)"]
)
max_capacity_g = st.sidebar.number_input("最大秤量 Max Capacity (g)", min_value=0.0, value=220.0, step=0.1, format="%.4f")
d_value_mg = st.sidebar.number_input("實際分度值 Scale Interval (d) (mg)", min_value=0.0, value=0.1, step=0.01, format="%.4f")
m_snw_mg = st.sidebar.number_input("客戶預期最小淨重 Smallest Net Weight (mg)", min_value=0.0, value=20.0, step=1.0)

st.sidebar.divider()

# --- 側邊欄：用戶填寫實測使用的砝碼 ---
st.sidebar.header("🧪 2. 擬使用測試砝碼")
st.sidebar.info("請輸入您或客戶預計在現場使用的砝碼重量。")
user_rep_w_mg = st.sidebar.number_input("重複性測試砝碼 (mg)", min_value=0.0, value=100.0, step=100.0)
user_acc_w_g = st.sidebar.number_input("準確度測試砝碼 (g)", min_value=0.0, value=200.0, step=10.0)

# --- 邏輯運算 ---
if st.sidebar.button("🛠️ 生成診斷與適宜性判定報告"):
    # 基礎計算
    five_percent_g = max_capacity_g * 0.05
    five_percent_mg = five_percent_g * 1000
    rep_min_mg = 100.0
    rep_max_mg = five_percent_mg
    
    acc_min_g = five_percent_g
    acc_max_g = max_capacity_g
    
    # 診斷報告開始
    st.subheader("📊 USP 〈41〉 測試點位與適宜性診斷")
    
    col1, col2 = st.columns(2)

    # --- 重複性 (Repeatability) 判定 ---
    with col1:
        st.info("### 重複性測試 (Repeatability)")
        st.markdown(f"""
        * **法規推薦區間**：`{format_weight(rep_min_mg)}` ~ `{format_weight(rep_max_mg)}`
        * **目前選擇重量**：`{format_weight(user_rep_w_mg)}`
        """)
        
        # 判定邏輯
        if user_rep_w_mg < rep_min_mg:
            st.error(f"❌ **不符合規範**：重量低於 100 mg。")
        elif user_rep_w_mg > rep_max_mg:
            st.error(f"❌ **不符合規範**：重量超過最大秤量的 5% ({format_weight(rep_max_mg)})。")
        else:
            st.success("✅ **適合**：該重量符合 USP <41> 重複性測試要求。")
        
        # 點位提醒
        if "多區間" in balance_type:
            st.warning("📍 **注意**：必須在「最精細量程段」測試。")

    # --- 準確度 (Accuracy) 判定 ---
    with col2:
        st.info("### 準確度測試 (Accuracy)")
        st.markdown(f"""
        * **法規推薦區間**：`{acc_min_g:.2f} g` ~ `{max_capacity_g:.2f} g`
        * **目前選擇重量**：`{user_acc_w_g:.4f} g`
        """)
        
        # 判定邏輯
        if user_acc_w_g < acc_min_g:
            st.error(f"❌ **不符合規範**：重量低於最大秤量的 5% ({acc_min_g:.2f} g)。")
        elif user_acc_w_g > acc_max_g:
            st.error(f"❌ **不符合規範**：重量超過天平最大秤量。")
        else:
            st.success("✅ **適合**：該重量符合 USP <41> 準確度測試要求。")
            
        st.caption(f"💡 註：砝碼擴展不確定度 U 須 ≤ {(0.05/3):.4f}%")

    st.divider()

    # --- 3. 綜合能力評估 (整合之前的最小淨重邏輯) ---
    st.subheader("🛡️ 天平能力與客戶需求匹配度")
    
    # 計算理論最小重量 (以 s = 0.41d 為基準)
    min_std_mg = 0.41 * d_value_mg
    min_weight_limit_mg = (2 * min_std_mg) / 0.001
    
    c1, c2, c3 = st.columns(3)
    c1.metric("天平極限最小淨重 (s=0.41d)", format_weight(min_weight_limit_mg))
    c2.metric("客戶預期最小淨重", f"{m_snw_mg} mg")
    
    # 判斷客戶需求是否合理
    if m_snw_mg < min_weight_limit_mg:
        st.error(f"🚨 **嚴重警告**：客戶要求的最小淨重 ({m_snw_mg} mg) 低於此天平的物理極限 ({min_weight_limit_mg:.2f} mg)。")
        st.markdown("> **工程師建議**：建議客戶更換更高精度的天平（d 值更小），或增加最小取樣量。")
    elif m_snw_mg < min_weight_limit_mg * 2:
        st.warning(f"⚠️ **風險提示**：客戶需求接近天平極限。")
        st.markdown(f"> **工程師建議**：現場環境稍微不穩即可能導致重複性不合格。建議至少維持在 `{format_weight(min_weight_limit_mg * 2)}` 以上。")
    else:
        st.success("✅ **規格匹配**：該天平精度足以應付客戶的日常秤量需求。")

    # --- 自動生成溝通摘要 ---
    st.markdown("---")
    with st.expander("📋 複製溝通摘要 (給客戶或報告用)"):
        summary = f"""
【USP <41> 合規診斷摘要】
1. 天平規格：{max_capacity_g}g / {d_value_mg}mg
2. 重複性測試：
   - 推薦重量：{format_weight(rep_min_mg)} ~ {format_weight(rep_max_mg)}
   - 擬用重量：{format_weight(user_rep_w_mg)} -> {'符合' if rep_min_mg <= user_rep_w_mg <= rep_max_mg else '不符合'}
3. 準確度測試：
   - 推薦重量：{acc_min_g:.2f}g ~ {max_capacity_g:.2f}g
   - 擬用重量：{user_acc_w_g:.2f}g -> {'符合' if acc_min_g <= user_acc_w_g <= acc_max_g else '不符合'}
4. 最小淨重判定：
   - 客戶需求：{m_snw_mg} mg
   - 天平法規極限：{min_weight_limit_mg:.2f} mg
   - 判定結果：{'符合需求' if m_snw_mg >= min_weight_limit_mg else '無法達成，建議改善'}
        """
        st.code(summary)

else:
    st.info("👈 請在左側輸入天平參數與預計使用的砝碼，點擊按鈕進行診斷。")
