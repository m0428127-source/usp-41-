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
st.set_page_config(page_title="USP <41> 專業合規評估", layout="centered")
st.title("⚖️ USP 天平合規快速評估")
st.caption("工程師實測 / 業務快速提案 雙模工具 (2026 Edition)")

# --- 3. 初始化 Session State (防止數據重置) ---
if 'user_std_input' not in st.session_state:
    st.session_state.user_std_input = None
if 'last_active_d' not in st.session_state:
    st.session_state.last_active_d = None

# --- 4. 側邊欄 ---
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("顯示單位", ["g", "mg", "kg"], index=0)
    st.divider()
    st.header("🔍 環境檢查 (USP 1251)")
    env_all = st.checkbox("水平、穩固、遠離氣流與熱源")
    preheat = st.checkbox("天平已預熱並校準完成")

# --- 5. 快速輸入區 ---
st.markdown("### 1️⃣ 機台規格與評估模式")
col_type, col_mode = st.columns([1, 1])

with col_type:
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間", "DU_多量程"])

with col_mode:
    has_std = st.radio("是否有實測標準差數據？", ["手動輸入 STD", "無數據 (採機台極限預估)"], horizontal=False)

user_sf = st.select_slider("設定目標安全係數 (Safety Factor)", options=list(range(1, 11)), value=2)

# 分度值選擇
d_base_options = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
d_converted = [float(smart_format(convert_from_g(x, display_unit))) for x in d_base_options]

if balance_type in ["DR_多區間", "DU_多量程"]:
    c1, c2 = st.columns(2)
    with c1:
        d1_raw = st.select_slider(f"分度值 d1 (精細區) ({display_unit})", options=d_converted, value=d_converted[5])
        d1_g = convert_to_g(d1_raw, display_unit)
    with c2:
        d2_raw = st.select_slider(f"分度值 d2 (寬鬆區) ({display_unit})", options=d_converted, value=d_converted[4])
        d2_g = convert_to_g(d2_raw, display_unit)
    active_d_g = d1_g
else:
    d_raw = st.select_slider(f"分度值 d ({display_unit})", options=d_converted, value=d_converted[4])
    active_d_g = convert_to_g(d_raw, display_unit)
    d1_g = active_d_g
    d2_g = None

# 💡 自動更新逻辑：如果 d 變了，重置 STD 預設值，否則保留使用者輸入
if active_d_g != st.session_state.last_active_d:
    st.session_state.user_std_input = float(smart_format(convert_from_g(active_d_g * 0.8, display_unit)))
    st.session_state.last_active_d = active_d_g

st.markdown("---")
st.markdown("### 2️⃣ 數據與需求")
col_snw, col_std = st.columns(2)

with col_snw:
    snw_raw = st.number_input(f"客戶預期最小淨重 ({display_unit})", value=float(convert_from_g(0.02, display_unit)), format="%.7g")
    snw_g = convert_to_g(snw_raw, display_unit)

s_limit_d1 = 0.41 * d1_g

with col_std:
    if has_std == "手動輸入 STD":
        # 使用 key 綁定 session_state，這樣輸入就不會因為頁面重新整理而消失
        std_raw = st.number_input(
            f"重複性實測標準差 STD ({display_unit})", 
            value=st.session_state.user_std_input, 
            format="%.7g",
            key="std_input_widget"
        )
        # 更新 session_state 供下次刷新使用
        st.session_state.user_std_input = std_raw
        std_g = convert_to_g(std_raw, display_unit)
        effective_s = max(std_g, s_limit_d1)
        mode_label = "實測評估"
    else:
        st.info("ℹ️ 模式：機台理論極限預估")
        effective_s = s_limit_d1
        std_g = 0
        mode_label = "理論預估"

# --- 6. 核心計算與顯示 (維持您的邏輯) ---
usp_min_weight_g = 2000 * effective_s
current_real_sf = snw_g / usp_min_weight_g if usp_min_weight_g > 0 else 0
theoretical_min_w_d1 = 2000 * s_limit_d1

st.divider()
st.markdown(f"### 🏁 評估結論 ({mode_label})")

if current_real_sf >= user_sf:
    st.success(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (符合預期)")
elif current_real_sf >= 1:
    st.warning(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (法規邊緣)")
else:
    st.error(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (不合規)")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label="機台物理極限 (SF=1)", value=auto_unit_format(theoretical_min_w_d1))
with c2:
    label_text = "法規判定 MinW" if has_std == "手動輸入 STD" else "理論最優 MinW"
    st.metric(label=label_text, value=auto_unit_format(usp_min_weight_g))
with c3:
    st.metric(label="客戶目標秤重", value=auto_unit_format(snw_g))

st.info(f"💡 {'實測建議' if has_std == '手動輸入 STD' else '快速提案建議'}：若要滿足目標 **SF={user_sf}**，建議淨重應大於 **{auto_unit_format(usp_min_weight_g * user_sf)}**。")

with st.expander("📄 查看評估摘要"):
    summary = f"""【USP 41 評估 - {mode_label}】\n天平類型: {balance_type}\n分度值 d: {auto_unit_format(d1_g)}\n"""
    if has_std == "手動輸入 STD": summary += f"實測標準差 STD: {auto_unit_format(std_g)}\n"
    summary += f"認定最小秤量 (MinW): {auto_unit_format(usp_min_weight_g)}\n客戶目標淨重: {auto_unit_format(snw_g)}\n安全係數: {current_real_sf:.2f}\n判定: {'✅ 符合' if current_real_sf >= user_sf else '❌ 未達標'}"
    st.code(summary)
