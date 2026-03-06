import streamlit as st

# --- 1. 工具函數 ---
def smart_format(value):
    if value == 0: return "0"
    return f"{value:.7g}"

def auto_unit_format(g_value):
    abs_val = abs(g_value)
    if abs_val == 0: return "0 g"
    if abs_val < 0.001: return f"{smart_format(g_value * 1000)} mg"
    elif abs_val >= 1000: return f"{smart_format(g_value / 1000)} kg"
    else: return f"{smart_format(g_value)} g"

def convert_to_g(value, unit):
    if unit == "mg": return value / 1000
    if unit == "kg": return value * 1000
    return value

def convert_from_g(value, unit):
    if unit == "mg": return value * 1000
    if unit == "kg": return value / 1000
    return value

# --- 2. 網頁配置 ---
st.set_page_config(page_title="USP <41> 測試合規工作站", layout="centered")
st.title("⚖️ USP 〈41〉 天平測試合規指引")
st.caption("依據 2026.02.01 最新生效標準設計")

# 側邊欄設定
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("偏好單位", ["g", "mg", "kg"], index=0)
    st.divider()
    st.info("💡 手機操作建議：請垂直持握手機以獲得最佳閱讀體驗。")

# ---------------------------------------------------------
# STEP 1: 天平基本規格與預檢
# ---------------------------------------------------------
st.markdown("### 📋 第一步：天平基本規格")
with st.container(border=True):
    balance_type = st.selectbox(
        "選擇天平類型", 
        ["單一量程", "DR_多區間 (Multi-interval)", "DU_多量程 (Multiple range)"]
    )
    
    # DR/DU 關鍵提醒
    if "DR" in balance_type:
        st.warning("💡 **專業提醒**：因為 DR 僅須測試細量程 (Finest range)，若您的量測涉及跨越雙量程，請選擇 **DU 類型** 以執行完整評估。")
    
    raw_max_cap = st.number_input(f"天平最大秤量 Max ({display_unit})", value=float(convert_from_g(220.0, display_unit)), format="%.4f")
    max_cap_g = convert_to_g(raw_max_cap, display_unit)

# ---------------------------------------------------------
# STEP 2: 砝碼選用規範與預檢 (將用戶文字整合在此)
# ---------------------------------------------------------
st.markdown("### 🎯 第二步：測試砝碼預檢")
with st.container(border=True):
    # 用戶要求的詳細規範說明 (使用 Expander 節省手機空間)
    with st.expander("📌 點擊查看：USP <41> 砝碼選用具體規範"):
        st.markdown("""
        **一、 重複性測試 (Repeatability)**
        * **砝碼重量**：介於 **100 mg** 到 **天平最大秤量 (Max) 的 5%** 之間。
        * **測試程序**：必須使用單一測試砝碼，重複稱量至少 **10 次**。
        
        **二、 準確性測試 (Accuracy)**
        * **測試範圍**：應使用標稱質量介於 **Max 的 5% 至 100%** 之間的砝碼。
        * **1/3 準則**：砝碼的擴充不確定度 (U) 或 MPE 必須小於 **0.05% 的三分之一**。
        """)

    # 計算法定砝碼區間
    rep_min, rep_max = 0.1, max_cap_g * 0.05
    acc_min, acc_max = max_cap_g * 0.05, max_cap_g
    
    st.markdown(f"**根據您的 Max，法定砝碼應選用：**")
    st.code(f"重複性：{auto_unit_format(rep_min)} ~ {auto_unit_format(rep_max)}\n準確度：{auto_unit_format(acc_min)} ~ {auto_unit_format(acc_max)}")

    col1, col2 = st.columns(2)
    with col1:
        rep_w_raw = st.number_input(f"擬用重複性砝碼", value=float(convert_from_g(rep_min, display_unit)), format="%.4f")
    with col2:
        acc_w_raw = st.number_input(f"擬用準確度砝碼", value=float(convert_from_g(acc_max*0.5, display_unit)), format="%.4f")
    
    rep_w_g = convert_to_g(rep_w_raw, display_unit)
    acc_w_g = convert_to_g(acc_w_raw, display_unit)

    # 檢查砝碼是否合格
    if rep_min <= rep_w_g <= rep_max and acc_min <= acc_w_g <= acc_max:
        st.success("✅ 預計使用的砝碼重量符合 USP 規範。")
    else:
        st.error("❌ 預計使用的砝碼重量「不符合」法規建議區間。")

# ---------------------------------------------------------
# STEP 3: 數據輸入 (包含 0.41d 規則說明)
# ---------------------------------------------------------
st.markdown("### 📊 第三步：輸入實測數據")

with st.container(border=True):
    # 規格細節說明
    with st.expander("📌 點擊查看：重複性判定標準 (0.41d 規則)"):
        st.markdown("""
        * **判定標準**：$2s / m_{SNW} \\le 0.10\%$
        * **0.41d 規則**：若實測標準差 $s < 0.41d$ ($d$ 為分度值)，則計算時必須以 $0.41d$ 取代 $s$。
        * **最小稱量值 ($m_{min}$)**：即 $2000 \times s$ (或 $2000 \times 0.41d$)。
        """)

    d_options = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
    d_conv = [float(convert_from_g(x, display_unit)) for x in d_options]
    
    # 依據 DU/單量程動態調整
    if "DU" in balance_type:
        st.write("**【量程 1 (Fine)】**")
        d1_raw = st.select_slider("分度值 d1", options=d_conv, value=d_conv[4])
        std1_raw = st.number_input("實測標準差 s1", value=0.00008, format="%.6f")
        snw1_raw = st.number_input("需求最小淨重 SNW1", value=0.02, format="%.4f")
        
        st.divider()
        st.write("**【量程 2 (Coarse)】**")
        d2_raw = st.select_slider("分度值 d2", options=d_conv, value=d_conv[3])
        std2_raw = st.number_input("實測標準差 s2", value=0.0008, format="%.6f")
        snw2_raw = st.number_input("需求最小淨重 SNW2", value=0.2, format="%.4f")
        
        test_ranges = [
            {"d": convert_to_g(d1_raw, display_unit), "s": convert_to_g(std1_raw, display_unit), "snw": convert_to_g(snw1_raw, display_unit), "label": "細量程 (Fine)"},
            {"d": convert_to_g(d2_raw, display_unit), "s": convert_to_g(std2_raw, display_unit), "snw": convert_to_g(snw2_raw, display_unit), "label": "粗量程 (Coarse)"}
        ]
    else:
        d_raw = st.select_slider("分度值 d", options=d_conv, value=d_conv[4])
        std_raw = st.number_input("實測標準差 s", value=0.00008, format="%.6f")
        snw_raw = st.number_input("需求最小淨重 SNW", value=0.02, format="%.4f")
        test_ranges = [{"d": convert_to_g(d_raw, display_unit), "s": convert_to_g(std_raw, display_unit), "snw": convert_to_g(snw_raw, display_unit), "label": "單一/精細量程"}]

# ---------------------------------------------------------
# STEP 4: 最終診斷報告 (整合 1251 建議)
# ---------------------------------------------------------
if st.button("🚀 執行合規診斷報告", use_container_width=True, type="primary"):
    st.subheader("🏁 USP 〈41〉 設備適宜性診斷報告")
    
    for data in test_ranges:
        # 核心判定邏輯
        s_limit = 0.41 * data['d']
        effective_s = max(data['s'], s_limit)
        m_min = 2000 * effective_s
        sf = data['snw'] / m_min if m_min > 0 else 0
        
        with st.container(border=True):
            st.markdown(f"#### 📍 {data['label']} 診斷 (d = {auto_unit_format(data['d'])})")
            
            # 結果判定
            if data['snw'] >= m_min:
                st.success(f"**【合規判定：成功】**\n\n您的最小淨重需求 ({auto_unit_format(data['snw'])}) 符合且高於法定最小秤量值 ({auto_unit_format(m_min)})。")
            else:
                st.error(f"**【合規判定：失敗】**\n\n您的最小淨重需求已低於法規要求的極限值 ({auto_unit_format(m_min)})。")

            # 關鍵指標指標卡
            c1, c2, c3 = st.columns(3)
            c1.metric("法定 MinW", auto_unit_format(m_min))
            c2.metric("需求 SNW", auto_unit_format(data['snw']))
            c3.metric("安全係數 SF", f"{sf:.2f}")

            # 1251 安全係數提醒
            if sf >= 2:
                st.info("🛡️ **安全狀態：優良**。符合 〈1251〉 建議之安全係數 2，環境波動風險極低。")
            elif sf >= 1.5:
                st.warning("⚠️ **安全狀態：普通**。符合自動化程序建議 (1.5)，但低於一般環境建議 (2)。")
            elif sf >= 1:
                st.error("❗ **安全狀態：極高風險**。僅壓線符合法規最低標準，強烈建議提高秤量值或優化環境。")

            # 準確度證書 U 檢核
            mpe_limit = (0.05 / 100) / 3
            u_threshold = acc_w_g * mpe_limit
            st.markdown(f"""
            **準確度技術細節 (1/3 準則)：**
            * 擬用準確度砝碼：`{auto_unit_format(acc_w_g)}`
            * 砝碼證書擴充不確定度 (U) 必須 $\le$ **`{auto_unit_format(u_threshold)}`**
            """)

st.divider()
st.caption("※ 本工具僅供技術分析與指引之用，正式合規結論應以實驗室原始紀錄為準。")
