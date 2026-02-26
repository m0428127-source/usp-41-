import streamlit as st

# --- 1. 工具函數 ---
def smart_format(value):
    """ 
    絕不使用科學記號，且自動修剪末尾無意義的 0
    """
    if value is None or value == 0: return "0"
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

# 初始化 d2_g
d2_g = None

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
# --- 數據輸入區 ---
col_snw, col_std = st.columns(2)

with col_snw:
    is_snw_unknown = st.checkbox("尚未決定最小淨重量")
    if not is_snw_unknown:
        snw_input = st.text_input(f"客戶設定最小淨重量 ({display_unit})", 
                                  value=smart_format(st.session_state.snw_val),
                                  key="snw_text_field")
        try:
            snw_raw = float(snw_input)
            st.session_state.snw_val = snw_raw
        except ValueError:
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
            std_raw = st.session_state.std_val
        std_g = convert_to_g(std_raw, display_unit)
    else:
        st.info("ℹ️ 模式：機台理論極限預估")
        std_g = 0

# --- 5. 核心計算 ---
# d1 計算
s_limit_d1 = 0.41 * d1_g
ideal_min_w_d1 = 2000 * s_limit_d1

# d2 計算 (如果有)
ideal_min_w_d2 = 2000 * (0.41 * d2_g) if d2_g else None

# 實際合規計算 (基於實測 Std 與 d1)
effective_s = max(std_g, s_limit_d1)
is_corrected = std_g < s_limit_d1
usp_min_w = 2000 * effective_s
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

# 指標卡
if d2_g:
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1: st.metric("d1 理想最小秤重量", auto_unit_format(ideal_min_w_d1))
    with m_col2: st.metric("d2 理想最小秤重量", auto_unit_format(ideal_min_w_d2))
    with m_col3: st.metric("實際判定 MinW", auto_unit_format(usp_min_w), delta="法規修正" if is_corrected else None, delta_color="inverse")
    with m_col4: st.metric("設定 SNW", auto_unit_format(snw_g) if snw_g else "待定")
else:
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1: st.metric("機台理想最小秤重", auto_unit_format(ideal_min_w_d1))
    with m_col2: st.metric("機台實際最小秤重", auto_unit_format(usp_min_w), delta="法規修正" if is_corrected else None, delta_color="inverse")
    with m_col3: st.metric("客戶設定最小淨重", auto_unit_format(snw_g) if snw_g else "待定")

# --- 7. 報告摘要 ---
st.divider()
st.markdown("### 📄 專業評估報告摘要")

if is_snw_unknown:
    sf_text, snw_text, result_text = "待定", "待定", "待定"
else:
    sf_text = f"{current_sf:.2f}"
    snw_text = auto_unit_format(snw_g)
    result_text = "✅ 符合法規" if current_sf >= 1 else "❌ 不符合法規"

d2_report_line = f"理論最小秤量極限 (d2: 0.41d2): {auto_unit_format(ideal_min_w_d2)}\n" if d2_g else ""

copyable_report = f"""【USP 41 專業評估報告 - 2026 Edition】
------------------------------------------
評估結果：{result_text}
天平可讀數 (d1): {auto_unit_format(d1_g)}
{"天平可讀數 (d2): " + auto_unit_format(d2_g) if d2_g else ""}
理論最小秤量極限 (d1: 0.41d1): {auto_unit_format(ideal_min_w_d1)}
{d2_report_line}重複性實測標準差 (Std): {auto_unit_format(std_g) if std_g > 0 else "N/A"}
判定最小秤重量 (MinW): {auto_unit_format(usp_min_w)}
客戶設定最小淨重 (SNW): {snw_text}
實際安全係數 (SF): {sf_text} (目標要求: {user_sf})
------------------------------------------
"""
st.code(copyable_report, language="text")
