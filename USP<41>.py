import streamlit as st

# 設定網頁標題與專業風格
st.set_page_config(page_title="USP <41> Balances 合規診斷工具", layout="wide")

st.title("⚖️ USP 〈41〉 Balances 測試需求診斷工具")
st.caption("依據標準：USP-NF 〈41〉 (Official Feb 1, 2026)")

# --- 側邊欄：使用者輸入參數 ---
st.sidebar.header("📋 輸入天平基本參數")

balance_type = st.sidebar.selectbox(
    "1. 天平類型 (Balance Type)",
    ["單一量程 (Single range)", "多區間 (Multi-interval)", "多量程 (Multiple range)"],
    help="依據 USP <41>，多區間與多量程有不同的測試範圍要求。"
)

max_capacity = st.sidebar.number_input("2. 最大秤量 Max Capacity (g)", min_value=0.0, step=0.1, format="%.4f")
d_value = st.sidebar.number_input("3. 實際分度值 Scale Interval (d) (mg)", min_value=0.0, step=0.01, format="%.4f")
m_snw = st.sidebar.number_input("4. 預期最小淨重 Smallest Net Weight (mg)", min_value=0.0, step=1.0)

is_manufacturing = st.sidebar.checkbox("此天平是否用於製造 (Manufacturing)?")

# --- 邏輯判斷與診斷報告 ---
if st.sidebar.button("生成 USP <41> 診斷報告"):
    
    if is_manufacturing:
        st.error("⚠️ 根據 USP 〈41〉 第一段：'The scope of this chapter does not cover balances used for manufacturing.' (本章節不涵蓋用於製造之天平)。請確認您的用途。")
    elif max_capacity <= 0 or d_value <= 0 or m_snw <= 0:
        st.warning("請確保所有輸入參數皆大於 0。")
    else:
        st.subheader("📊 USP 〈41〉 測試評估診斷結果")
        
        col1, col2 = st.columns(2)

        # --- 重複性測試 (Repeatability) ---
        with col1:
            st.info("### 1. 重複性測試要求 (Repeatability)")
            
            # 砝碼選擇 logic (USP <41> Repeatability 段落)
            w_min = 100 # mg
            w_max = max_capacity * 1000 * 0.05 # 5% capacity in mg
            
            st.markdown(f"""
            * **砝碼選擇要求**：
                * 必須使用**單一**面額砝碼。
                * 重量區間：**{w_min} mg ~ {w_max:.2f} mg** (依據：不得低於 100 mg 且不得超過 5% Max Capacity)。
                * **注意**：此測試砝碼不需要校正。
            * **測試次數**：
                * 對該砝碼進行至少 **10 次** 秤重。
            """)
            
            # 點位要求 (USP <41> Repeatability 針對多區間/多量程之描述)
            if balance_type == "多區間 (Multi-interval)":
                st.write("📍 **點位要求**：必須在**最精細量程** (Smallest scale interval range) 執行。")
            elif balance_type == "多量程 (Multiple range)":
                st.write("📍 **點位要求**：必須在操作中使用的**每一個量程**執行。若需進入較粗量程，需使用預載物 (Preload)。")
            else:
                st.write("📍 **點位要求**：在天平秤盤中心執行即可。")

            # 允收標準計算
            limit_val = 0.0010 # 0.10%
            min_std = 0.41 * (d_value / 1000) # 轉為 g
            st.markdown(f"""
            * **允收標準 (Acceptance Criteria)**：
                * 公式：$2 \times s / m_{{SNW}} \le 0.10\%$
                * **關鍵限制**：若計算出的標準差 $s$ 小於 **{0.41 * d_value:.4f} mg** ($0.41d$)，則必須以該值取代 $s$ 進行計算。
            """)

        # --- 準確度測試 (Accuracy) ---
        with col2:
            st.info("### 2. 準確度測試要求 (Accuracy)")
            
            # 砝碼選擇 logic (USP <41> Accuracy 段落)
            acc_min = max_capacity * 0.05
            acc_max = max_capacity
            
            st.markdown(f"""
            * **砝碼選擇要求**：
                * **必須經過校正**。
                * 重量區間：**{acc_min:.2f} g ~ {acc_max:.2f} g** (依據：介於 5% 與 100% Max Capacity 之間)。
                * **砝碼不確定度限制**：砝碼的 $MPE$ 或擴展不確定度 $U$ 必須小於 **{(0.05/100)/3 * 100:.4f}%** (即準確度標準 0.05% 的 1/3)。
            * **測試次數**：
                * 執行 **1 次** 測試即可。
            * **允收標準 (Acceptance Criteria)**：
                * 公式：$|I - m| / m \le 0.05\%$ (其中 $I$ 為顯示值，$m$ 為砝碼標稱值)。
            """)

        st.divider()

        # --- 綜合診斷說明 (Specific Notes) ---
        st.success("### 📝 綜合注意事項 (General Requirements)")
        
        # 引用 USP <41> 與 <1251> 的實務建議
        st.write("根據您輸入的資料，此台天平的**操作限制**如下：")
        
        # 計算最小重量
        min_weight_res = (2 * 0.41 * d_value) / 0.0010
        st.warning(f"💡 **最小重量警示**：此天平在最理想狀態下(s=0.41d)的最小重量為 **{min_weight_res:.2f} mg**。您的預期最小淨重 ({m_snw} mg) 必須大於此值。")

        st.markdown(f"""
        1.  **皮重容器限制**：重複性測試所計算出的最小重量，不應包含任何容器(Tare)的重量。(來源：USP <41>)
        2.  **週期性檢查**：應根據風險評估 (Risk-based) 決定校正與效能檢查的頻率。(來源：USP <41> Introduction)
        3.  **環境要求**：天平必須安裝在穩固且與秤重需求相稱的環境中，並確保水平。(來源：USP <1251>)
        """)

else:
    st.write("請在左側輸入參數並點擊『生成診斷報告』。")
