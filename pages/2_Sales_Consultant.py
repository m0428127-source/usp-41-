import streamlit as st

# --- 1. 工具函數 ---
def smart_format(value):
    if value is None or value == 0: return "0"
    return f"{value:.10f}".rstrip('0').rstrip('.')

def auto_unit_format(g_value):
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
st.set_page_config(page_title="USP <41> 合規評估", layout="centered")
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

st.markdown("### 📋 1️⃣ 設定規格與需求")

col1, col2 = st.columns(2)
with col1:
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間", "DU_多量程"])
    user_sf = st.select_slider("目標安全係數 (SF)", options=list(range(1, 11)), value=2)
with col2:
    has_std = st.radio("評估模式", ["手動輸入實測 Std", "無數據 (理論預估)"])

d_base_options = [1.0, 0.5, 0.2, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001]
d_converted = [float(convert_from_g(x, display_unit)) for x in d_base_options]
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
st.markdown("### 📥 2️⃣ 數據輸入區")

col_snw, col_std = st.columns(2)
with col_snw:
    is_snw_unknown = st.checkbox("尚未決定最小淨重量")
    if not is_snw_unknown:
        snw_input = st.text_input(f"客戶設定最小淨重量 ({display_unit})", value=smart_format(st.session_state.snw_val), key="snw_text_field")
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
        std_input = st.text_input(f"重複性實測標準差 Std ({display_unit})", value=smart_format(st.session_state.std_val), key="std_text_field")
        try:
            std_raw = float(std_input)
            st.session_state.std_val = std_raw
        except ValueError:
            std_raw = st.session_state.std_val
        std_g = convert_to_g(std_raw, display_unit)
    else:
        st.info("ℹ️ 模式：機台理論極限預估")
        std_g = 0

s_limit_d1 = 0.41 * d1_g
ideal_min_w_d1 = 2000 * s_limit_d1
ideal_min_w_d2 = 2000 * (0.41 * d2_g) if d2_g else None
effective_s = max(std_g, s_limit_d1)
is_corrected = std_g < s_limit_d1
usp_min_w = 2000 * effective_s
current_sf = snw_g / usp_min_w if (snw_g is not None and usp_min_w > 0) else 0

# --- 6. 專業結論面板 ---
st.divider()
st.markdown("### 🏁 3️⃣ 評估結論")

if is_snw_unknown:
    st.info("💡 目前已計算出機台最小秤量門檻。")
else:
    snw_display = auto_unit_format(snw_g)
    minw_display = auto_unit_format(usp_min_w)
    
    st.markdown(f"#### 當前實際安全係數 (SF): `{current_sf:.2f}`")

    if current_sf >= user_sf:
        msg = f"已達標：當前最小淨重 ({snw_display}) 遠高於判定門檻 ({minw_display})，安全緩衝充足。"
        st.success(f"### 🛡️ 安全狀態：優良\n{msg}")
    elif current_sf >= 1:
        msg = f"請注意：當前最小淨重 ({snw_display}) 雖符合法規最低限度，但低於您的目標安全係數 {user_sf}，建議提高秤量值。"
        st.warning(f"### ⚠️ 安全狀態：高風險\n{msg}")
    else:
        msg = f"嚴重警告：當前最小淨重 ({snw_display}) 已低於 USP <41> 判定之最小秤量門檻 ({minw_display})，將導致合規性失效。"
        st.error(f"### ❌ 安全狀態：不合規\n{msg}")

# 指標卡區塊
if d2_g:
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1: st.metric("d1 理論最小秤重", auto_unit_format(ideal_min_w_d1))
    with m_col2: st.metric("d2 理論最小秤重", auto_unit_format(ideal_min_w_d2))
    with m_col3: st.metric("實際最小秤重(判定)", auto_unit_format(usp_min_w), delta="法規修正(Std < 0.41d)" if is_corrected else None, delta_color="inverse")
    with m_col4: st.metric("客戶設定 SNW", auto_unit_format(snw_g) if snw_g else "待定")
else:
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1: st.metric("機台理論最小秤重", auto_unit_format(ideal_min_w_d1))
    with m_col2: st.metric("實際最小秤重(判定)", auto_unit_format(usp_min_w), delta="法規修正(Std < 0.41d)" if is_corrected else None, delta_color="inverse")
    with m_col3: st.metric("客戶設定最小淨重", auto_unit_format(snw_g) if snw_g else "待定")

# --- 7. 報告摘要 ---
st.divider()
st.markdown("### 📄 4️⃣ 專業評估報告摘要")

if is_snw_unknown:
    sf_text, snw_text, result_text, detail_note = "待定", "待定", "待定", "尚未輸入淨重數據"
else:
    sf_text = f"{current_sf:.2f}"
    snw_text = auto_unit_format(snw_g)
    if current_sf >= user_sf:
        result_text = "✅ 合規 (優良)"
        detail_note = f"實際 SF ({sf_text}) ≥ 目標 SF ({user_sf})，秤量環境極為安全。"
    elif current_sf >= 1:
        result_text = "⚠️ 合規 (高風險)"
        detail_note = f"符合 USP 最低要求 (SF ≥ 1)，但低於目標 SF ({user_sf})，建議提高秤量值或優化環境。"
    else:
        result_text = "❌ 不合規"
        detail_note = f"實際 SF ({sf_text}) < 1，未達到 USP <41> 規定的最小秤量門檻。"

d2_report_line = f"理論最小秤量極限 (d2: 0.41d2): {auto_unit_format(ideal_min_w_d2)}\n" if d2_g else ""
copyable_report = f"""【USP 41 專業評估報告 - 2026 Edition】
------------------------------------------
評估狀態：{result_text}
判定說明：{detail_note}

天平可讀數 (d1): {auto_unit_format(d1_g)}
{"天平可讀數 (d2): " + auto_unit_format(d2_g) if d2_g else ""}
理論最小秤量極限 (d1: 0.41d1): {auto_unit_format(ideal_min_w_d1)}
{d2_report_line}
重複性實測標準差 (Std): {auto_unit_format(std_g) if std_g > 0 else "N/A"}
判定最小秤重量 (MinW): {auto_unit_format(usp_min_w)}
客戶設定最小淨重 (SNW): {snw_text}
實際安全係數 (SF): {sf_text} (目標要求: {user_sf})
------------------------------------------
"""
st.code(copyable_report, language="text")

# 加入下載按鈕增加優化感
st.download_button(
    label="📥 下載文字報告 (.txt)",
    data=copyable_report,
    file_name=f"USP41_Report_{snw_text.replace(' ', '')}.txt",
    mime="text/plain"
)
