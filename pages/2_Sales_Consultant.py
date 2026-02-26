import streamlit as st

# --- 1. 工具函數 ---
def smart_format(value):
    """ 
    強制數字呈現（非科學記號），並動態修剪末尾無意義的 0。
    輸入 220 顯示 220, 0.99 顯示 0.99, 0.00001 顯示 0.00001
    """
    if value is None or value == 0: return "0"
    # 使用精度為 10 位的小數格式，確保小數字不會變成科學記號，再修剪右側 0
    formatted = format(value, '.10f').rstrip('0').rstrip('.')
    return formatted if formatted != "" else "0"

def auto_unit_format(g_value):
    """ 指標卡與報告使用的格式 """
    if g_value is None or g_value == 0: return f"0 {display_unit}"
    # 將數值轉換回顯示單位後進行格式化
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

# --- 3. 初始化 Session State (確保數值不因滑動而跳轉) ---
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
# 設定高精度小數格式，防止 number_input 顯示科學記號
p_step = 0.0000001
p_format = "%.10f" # 這裡改為 f 確保輸入框也不會跳科學記號

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

# 鎖定機制
if active_d_g != st.session_state.last_d:
    st.session_state.last_d = active_d_g

st.markdown("---")
# --- 數據輸入區 ---
col_snw, col_std = st.columns(2)

with col_snw:
    is_snw_unknown = st.checkbox("尚未決定最小淨重量")
    if not is_snw_unknown:
        snw_raw = st.number_input(f"客戶設定最小淨重量 ({display_unit})", 
                                  min_value=0.0000001, 
                                  value=float(st.session_state.snw_val),
                                  step=p_step,
                                  format=p_format, # 確保顯示為數字
                                  key="snw_input_field")
        st.session_state.snw_val = snw_raw
        snw_g = convert_to_g(snw_raw, display_unit)
    else:
        snw_g = None

with col_std:
    if has_std == "手動輸入實測 Std":
        std_raw = st.number_input(f"重複性實測標準差 Std ({display_unit})", 
                                  min_value=0.0000001,
                                  value=float(st.session_state.std_val),
                                  step=p_step,
                                  format=p_format, # 確保顯示為數字
                                  key="std_input_field")
        st.session_state.std_val = std_raw
        std_g = convert_to_g(std_raw, display_unit)
    else:
        st.info("ℹ️ 模式：機台理論極限預估")
        std_g = 0

# --- 5. 核心計算 ---
s_limit = 0.41 * d1_g
effective_s = max(std_g, s_limit)
is_corrected = std_g < s_limit
usp_min_w = 2000 * effective_s
ideal_min_w = 2000 * s_limit

# 計算安全係數
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

# 指標卡 (會使用 smart_format 呈現數字)
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

# --- 7. 報告摘要 ---
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
