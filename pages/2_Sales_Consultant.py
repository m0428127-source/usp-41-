import streamlit as st

# --- 1. 工具函數 (核心優化) ---
def smart_format(value):
    """ 
    最完美的數據呈現：
    1. 絕不使用科學記號 (如 8e-05)
    2. 自動去掉末端多餘的 0 (如 220.0000)
    3. 輸入 220 顯示 220，輸入 0.00008 顯示 0.00008
    """
    if value is None or value == 0: return "0"
    # 使用 .10f 強制展開小數避免科學記號，再移除右側多餘的 0 與小數點
    return f"{value:.10f}".rstrip('0').rstrip('.')

def auto_unit_format(g_value):
    """ 指標卡與報告使用的格式 """
    if g_value is None or g_value == 0: return f"0 {display_unit}"
    val_in_unit = convert_from_g(g_value, display_unit)
    return f"{smart_format(val_in_unit)} {display_unit}"

def convert_to_g(value, unit):
    if unit == "mg": return value / 1000
    if unit == "kg": return value * 1000
    return value

def convert_from_g(value, unit):
    if unit == "mg": return value * 1000
    if unit == "kg": return value / 1000
    return value

# --- 2. 網頁配置 ---
st.set_page_config(page_title="USP <41> 專業合規評估", layout="centered")
st.title("⚖️ USP 天平合規快速評估")
st.caption("依據標準：USP-NF 〈41〉 & 〈1251〉 (Official Feb 1, 2026)")

# --- 3. 初始化 Session State ---
if 'snw_val' not in st.session_state:
    st.session_state.snw_val = 0.02
if 'std_val' not in st.session_state:
    st.session_state.std_val = 0.00008
if 'last_d' not in st.session_state:
    st.session_state.last_d = 0.0001

# --- 4. 側邊欄 ---
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("顯示單位", ["g", "mg", "kg"], index=0)
    st.divider()
    st.header("🔍 USP 1251 環境檢查")
    st.checkbox("天平放置於穩固、水平檯面")
    st.checkbox("環境受控，且遠離直接氣流")

st.markdown("### 1️⃣ 設定規格與需求")

col1, col2 = st.columns(2)
with col1:
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間", "DU_多量程"])
    user_sf = st.select_slider("目標安全係數 (SF)", options=list(range(1, 11)), value=2)
with col2:
    has_std = st.radio("評估模式", ["手動輸入實測 Std", "無數據 (理論預估)"])

# 可讀數清單
d_base_options = [1.0, 0.5, 0.2, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001]
d_converted = [float(convert_from_g(x, display_unit)) for x in d_base_options]

if balance_type in ["DR_多區間", "DU_多量程"]:
    c1, c2 = st.columns(2)
    with c1: 
        d1_val = st.select_slider(f"d1 (精細量程) ({display_unit})", options=d_converted, value=d_converted[5], format_func=smart_format)
        d1_g = convert_to_g(d1_val, display_unit)
    with c2: 
        d2_val = st.select_slider(f"d2 (粗量程) ({display_unit})", options=d_converted, value=d_converted[4], format_func=smart_format)
        d2_g = convert_to_g(d2_val, display_unit)
    active_d_g = d1_g
else:
    d_val = st.select_slider(f"可讀數 d ({display_unit})", options=d_converted, value=d_converted[4], format_func=smart_format)
    active_d_g = convert_to_g(d_val, display_unit)
    d1_g = active_d_g

if active_d_g != st.session_state.last_d:
    st.session_state.last_d = active_d_g

st.markdown("---")
# --- 數據輸入區 (關鍵修正：改用 text_input 兼顧去零與非科學記號) ---
col_snw, col_std = st.columns(2)

with col_snw:
    is_snw_unknown = st.checkbox("尚未決定最小淨重量")
    if not is_snw_unknown:
        # 改用 text_input 並預設呈現 smart_format 後的字串
        snw_input = st.text_input(f"客戶設定最小淨重量 ({display_unit})", 
                                  value=smart_format(st.session_state.snw_val),
                                  key="snw_text_field")
        try:
            snw_raw = float(snw_input)
            st.session_state.snw_val = snw_raw
        except ValueError:
            st.error("請輸入有效數字")
            snw_raw = st.session_state.snw_val
        snw_g = convert_to_g(snw_raw, display_unit)
    else:
        snw_g = None

with col_std:
    if has_std == "手動輸入實測 Std":
        std_input = st.text_input(f"重複性實測標準差 Std ({display_unit})", 
                                  value=smart_format(st.session_state.std_val),
                                  key="std_text_field")
        try:
            std_raw = float(std_input)
            st.session_state.std_val = std_raw
        except ValueError:
            st.error("請輸入有效數字")
            std_raw = st.session_state.std_val
        std_g = convert_to_g(std_raw, display_unit)
    else:
        st.info("ℹ️ 模式：機台理論極限預估")
        std_g = 0

# --- 5. 核心計算 (邏輯文字完全不變) ---
s_limit = 0.41 * d1_g
effective_s = max(std_g, s_limit)
is_corrected = std_g < s_limit
usp_min_w = 2000 * effective_s
ideal_min_w = 2000 * s_limit
current_sf = snw_g / usp_min_w if (snw_g is not None and usp_min_w > 0) else 0

# --- 6. 專業結論面板 ---
st.divider()
st.markdown("### 🏁 專業評估結論")

if is_snw_unknown:
    st.info("💡 目前已計算出機台最小秤量門檻。")
else:
    if current_sf >= user_sf:
        st.success(f"🛡️ **安全狀態：優良** | 當前實測 SF: **{current_sf:.2f}**")
    elif current_sf >= 1:
        st.warning(f"⚠️ **安全狀態：高風險**")
    else:
        st.error(f"❌ **安全狀態：不合規**")

# 指標卡 (自動去零且非科學化顯示)
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("機台理想最小秤重量", auto_unit_format(ideal_min_w))
with c2:
    st.metric("機台實際最小秤重量", auto_unit_format(usp_min_w), 
              delta="法規修正" if is_corrected else None, delta_color="inverse")
with c3:
    if not is_snw_unknown:
        st.metric("客戶設定最小淨重量", auto_unit_format(snw_g), 
                  delta=f"SF: {current_sf:.2f}" if current_sf > 0 else None)
    else:
        st.metric("客戶設定最小淨重量", "待定")

# --- 7. 報告摘要 (邏輯文字完全不變) ---
st.divider()
st.markdown("### 📄 專業評估報告摘要")

if is_snw_unknown:
    sf_text, snw_text, result_text = "待定", "待定", "待定"
else:
    sf_text = f"{current_sf:.2f}"
    snw_text = auto_unit_format(snw_g)
    result_text = "✅ 符合法規" if current_sf >= 1 else "❌ 不符合法規"

copyable_report = f"""【USP 41 專業評估報告 - 2026 Edition】
------------------------------------------
評估結果：{result_text}
天平可讀數 (d): {auto_unit_format(d1_g)}
理論最小秤量極限 (0.41d): {auto_unit_format(ideal_min_w)}
重複性實測標準差 (Std): {auto_unit_format(std_g) if std_g > 0 else "N/A"}
判定最小秤重量 (MinW): {auto_unit_format(usp_min_w)}
客戶設定最小淨重 (SNW): {snw_text}
實際安全係數 (SF): {sf_text} (目標要求: {user_sf})
------------------------------------------
"""
st.code(copyable_report, language="text")
