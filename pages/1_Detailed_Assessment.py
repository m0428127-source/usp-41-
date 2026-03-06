import streamlit as st

# --- 工具函數 ---
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

# --- 網頁配置 ---
st.set_page_config(page_title="USP <41> 合規測試指引", layout="centered")
st.title("⚖️ USP 〈41〉 合規測試指引")
st.caption("最新 2026.02.01 生效標準執行方案")

# --- 全域參數設定 ---
p_step = 0.0000001
p_format = "%.7g"

# --- 側邊欄：顯示單位 ---
with st.sidebar:
    st.header("⚙️ 設定")
    display_unit = st.selectbox("偏好顯示單位", ["g", "mg", "kg"], index=0)

# ---------------------------------------------------------
# STEP 1: 基本規格與砝碼預檢
# ---------------------------------------------------------
st.markdown("### 📋 第一步：天平規格與法規導引")
with st.container(border=True):
    # 天平類型選擇
    balance_type = st.selectbox(
        "選擇天平類型", 
        ["單一量程", "DR_多區間 (Multi-interval)", "DU_多量程 (Multiple range)"],
        help="DR 與 DU 的測試要求不同，請依據您的量測範圍選擇。"
    )
    
    # 💡 您要求的專業提醒
    if "DR" in balance_type:
        st.warning("💡 **法規提醒**：根據 USP <41>，DR 類型僅須測試其**精細量程 (Finest range)**。如果您實際秤量過程中會跨越並涉及雙量程的準確性需求，請改選 **DU 類型** 以執行全面測試。")
    elif "DU" in balance_type:
        st.info("💡 **法規提醒**：DU 類型視為兩個獨立量程，系統將引導您分別輸入兩組數據進行合規判定。")

    raw_max_cap = st.number_input(f"天平最大秤量 Max Capacity ({display_unit})", value=float(convert_from_g(220.0, display_unit)), format=p_format)
    max_cap_g = convert_to_g(raw_max_cap, display_unit)

    # 顯示法規要求的砝碼範圍
    rep_min_g, rep_max_g = 0.100, max_cap_g * 0.05
    acc_min_g, acc_max_g = max_cap_g * 0.05, max_cap_g
    
    st.info(f"""
    **🔍 依據 USP <41> 規範，您應準備以下砝碼：**
    * **重複性測試**：`{auto_unit_format(rep_min_g)}` ~ `{auto_unit_format(rep_max_g)}`
    * **準確度測試**：`{auto_unit_format(acc_min_g)}` ~ `{auto_unit_format(acc_max_g)}`
    """)

    # 砝碼合規性檢核
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        rep_w_raw = st.number_input(f"擬用重複性砝碼 ({display_unit})", value=float(convert_from_g(0.1, display_unit)), format=p_format)
    with col_w2:
        acc_w_raw = st.number_input(f"擬用準確度砝碼 ({display_unit})", value=float(convert_from_g(200.0, display_unit)), format=p_format)
    
    rep_w_g = convert_to_g(rep_w_raw, display_unit)
    acc_w_g = convert_to_g(acc_w_raw, display_unit)

    if rep_min_g <= rep_w_g <= rep_max_g and acc_min_g <= acc_w_g <= acc_max_g:
        st.success("✅ 預計使用砝碼符合 USP <41> 重量區間要求。")
    else:
        st.error("❌ 警告：擬用砝碼重量不符合 USP <41> 規定。")

# ---------------------------------------------------------
# STEP 2: 填入實測數據
# ---------------------------------------------------------
st.markdown("### 📊 第二步：執行測試並填入數據")
with st.container(border=True):
    d_base_options = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001]
    d_converted_options = [float(smart_format(convert_from_g(x, display_unit))) for x in d_base_options]
    
    # 根據類型動態調整輸入框
    if "DU" in balance_type:
        d1_raw = st.select_slider("天平可讀數 d1 (細量程)", options=d_converted_options, value=d_converted_options[5])
        std1_raw = st.number_input(f"實測標準差 STD1 ({display_unit})", value=float(convert_from_g(0.000008, display_unit)), format=p_format)
        snw1_raw = st.number_input(f"淨重需求 SNW1 ({display_unit})", value=float(convert_from_g(0.02, display_unit)), format=p_format)
        
        st.divider()
        
        d2_raw = st.select_slider("天平可讀數 d2 (粗量程)", options=d_converted_options, value=d_converted_options[4])
        std2_raw = st.number_input(f"實測標準差 STD2 ({display_unit})", value=float(convert_from_g(0.00008, display_unit)), format=p_format)
        snw2_raw = st.number_input(f"淨重需求 SNW2 ({display_unit})", value=float(convert_from_g(0.2, display_unit)), format=p_format)
        
        ranges = [
            {"d": convert_to_g(d1_raw, display_unit), "std": convert_to_g(std1_raw, display_unit), "snw": convert_to_g(snw1_raw, display_unit), "label": "量程 1 (Fine)"},
            {"d": convert_to_g(d2_raw, display_unit), "std": convert_to_g(std2_raw, display_unit), "snw": convert_to_g(snw2_raw, display_unit), "label": "量程 2 (Coarse)"}
        ]
    else:
        label = "精細量程" if "DR" in balance_type else "單一量程"
        d_raw = st.select_slider(f"天平可讀數 d ({label})", options=d_converted_options, value=d_converted_options[4])
        std_raw = st.number_input(f"實測標準差 STD ({display_unit})", value=float(convert_from_g(0.00008, display_unit)), format=p_format)
        snw_raw = st.number_input(f"您的最小淨重需求 SNW ({display_unit})", value=float(convert_from_g(0.02, display_unit)), format=p_format)
        
        ranges = [
            {"d": convert_to_g(d_raw, display_unit), "std": convert_to_g(std_raw, display_unit), "snw": convert_to_g(snw_raw, display_unit), "label": label}
        ]

# ---------------------------------------------------------
# STEP 3: 執行合規檢查
# ---------------------------------------------------------
st.divider()
if st.button("🚀 產出合規判定報告", use_container_width=True, type="primary"):
    st.subheader("🏁 USP 〈41〉 合規判定報告")
    
    for data in ranges:
        s_threshold = 0.41 * data['d']
        actual_min_w = 2000 * max(data['std'], s_threshold)
        safety_factor = data['snw'] / actual_min_w if actual_min_w > 0 else 0
        
        with st.container(border=True):
            st.markdown(f"#### 📍 {data['label']} 診斷 (d = {auto_unit_format(data['d'])})")
            
            if data['snw'] >= actual_min_w:
                st.success(f"**判定結果：符合秤量需求**")
            else:
                st.error(f"**判定結果：不合規 (淨重需求太小)**")

            c1, c2, c3 = st.columns(3)
            c1.metric("法定 MinW", auto_unit_format(actual_min_w))
            c2.metric("您的需求 SNW", auto_unit_format(data['snw']))
            c3.metric("安全係數 SF", f"{safety_factor:.2f}")

            with st.expander("🔍 查看技術細節"):
                st.write(f"- 實測標準差 (s): `{auto_unit_format(data['std'])}`")
                st.write(f"- 0.41d 修正界限: `{auto_unit_format(s_threshold)}` {'(已採用修正值)' if data['std'] < s_threshold else ''}")
                
                # 準確度提示
                mpe_limit = (0.05 / 100) / 3 
                st.write(f"**準確度檢核：**")
                st.write(f"- 擬用砝碼 `{auto_unit_format(acc_w_g)}` 證書不確定度 $U$ 須 $\le$ `{auto_unit_format(acc_w_g * mpe_limit)}` (0.05% 的 1/3)")

st.caption("本工具僅供技術評估使用，正式報告請依 QMS 規範產出。")
