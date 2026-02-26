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
st.caption("工程師實測 / 業務快速提案 雙模工具 (Official Feb 1, 2026)")

# --- 3. 初始化 Session State (記憶功能) ---
if 'user_std_input' not in st.session_state:
    st.session_state.user_std_input = None
if 'last_active_d' not in st.session_state:
    st.session_state.last_active_d = None

# --- 4. 側邊欄與輸入區 ---
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("顯示單位", ["g", "mg", "kg"], index=0)
    st.divider()
    st.header("🔍 環境檢查")
    st.checkbox("水平、穩固、遠離氣流")
    st.checkbox("天平已預熱")

st.markdown("### 1️⃣ 設定規格與需求")
col1, col2 = st.columns(2)
with col1:
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間", "DU_多量程"])
    user_sf = st.select_slider("目標安全係數 (SF)", options=list(range(1, 11)), value=2)
with col2:
    has_std = st.radio("評估模式", ["手動輸入 STD", "無數據 (理論預估)"])

# 分度值邏輯
d_base_options = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
d_converted = [float(smart_format(convert_from_g(x, display_unit))) for x in d_base_options]

if balance_type in ["DR_多區間", "DU_多量程"]:
    c1, c2 = st.columns(2)
    with c1: 
        d1_g = convert_to_g(st.select_slider(f"d1 (精細區) ({display_unit})", options=d_converted, value=d_converted[5]), display_unit)
    with c2: 
        d2_g = convert_to_g(st.select_slider(f"d2 (寬鬆區) ({display_unit})", options=d_converted, value=d_converted[4]), display_unit)
    active_d_g = d1_g
else:
    active_d_g = convert_to_g(st.select_slider(f"分度值 d ({display_unit})", options=d_converted, value=d_converted[4]), display_unit)
    d1_g = active_d_g

# 自動更新 STD 預設值 (若換型號則帶入 0.8d 模擬實測)
if active_d_g != st.session_state.last_active_d:
    st.session_state.user_std_input = float(smart_format(convert_from_g(active_d_g * 0.8, display_unit)))
    st.session_state.last_active_d = active_d_g

st.markdown("---")
col_snw, col_std = st.columns(2)
with col_snw:
    snw_g = convert_to_g(st.number_input(f"客戶設定最小淨重量 ({display_unit})", value=float(convert_from_g(0.02, display_unit)), format="%.7g"), display_unit)

with col_std:
    if has_std == "手動輸入 STD":
        std_raw = st.number_input(f"實測標準差 STD ({display_unit})", value=st.session_state.user_std_input, format="%.7g", key="std_in")
        st.session_state.user_std_input = std_raw
        std_g = convert_to_g(std_raw, display_unit)
    else:
        st.write("**模式：理論極限預估**")
        std_g = 0

# --- 5. 核心計算 (依據 USP <41> 2026) ---
# 理論極限底線 s = 0.41d [cite: 25]
s_limit = 0.41 * d1_g
# 理想最小秤重量 (SF=1)
ideal_min_w = 2000 * s_limit
# 實際最小秤重量 m_min = 2000 * max(s, 0.41d) [cite: 27, 28]
usp_min_w = 2000 * max(std_g, s_limit)
# 當前安全係數 SF = Smallest Net Weight / Minimum Weight [cite: 24, 32]
current_sf = snw_g / usp_min_w if usp_min_w > 0 else 0

# --- 6. 結論顯示區 ---
st.divider()
st.markdown("### 🏁 評估結論")

status_color = "green" if current_sf >= user_sf else "orange" if current_sf >= 1 else "red"
if status_color == "green": st.success(f"🛡️ **安全狀態：優良** (當前 SF: {current_sf:.2f})")
elif status_color == "orange": st.warning(f"⚠️ **安全狀態：高風險** (當前 SF: {current_sf:.2f})")
else: st.error(f"❌ **安全狀態：不合規** (當前 SF: {current_sf:.2f})")

# 指標卡補充
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("機台理想最小秤重量", auto_unit_format(ideal_min_w))
    st.caption("基於 $0.41d$ 理論極限 [cite: 25, 31]")

with c2:
    st.metric("機台實際最小秤重量", auto_unit_format(usp_min_w))
    st.caption("標準差 < $0.41d$ 則使用 $0.41d$ [cite: 28]")

with c3:
    st.metric("客戶設定最小淨重量", auto_unit_format(snw_g), 
              delta=f"當前 SF: {current_sf:.2f}", 
              delta_color="normal" if current_sf >= 1 else "inverse")
    st.caption("Smallest Net Weight (SNW) ")

st.divider()
st.info(f"""
💡 **計算邏輯說明：**
* **安全係數 (SF)：** 計算方式為 **客戶設定最小淨重量 / 機台實際最小秤重量**。
* **合規條件：** 根據 USP 〈41〉，客戶設定的最小淨重量 **不得小於** 計算出的最小秤重量 (即 SF 必須 $\ge 1$) 。
* **修正原則：** 最小秤重量 $m_{min} = 2000 \times s$。若 $s < 0.41d$，則以 $0.41d$ 取代 $s$ 計算 [cite: 25, 27]。
""")

# --- 7. 報告摘要 ---
with st.expander("📄 查看專業評估報告摘要"):
    summary = f"""【USP 41 專業評估報告 - 2026 版】
評估狀態：{'✅ 符合法規' if current_sf >= 1 else '❌ 不符合法規'}
安全邊際：{'🛡️ 充足 (達到 SF 目標)' if current_sf >= user_sf else '⚠️ 不足 (低於 SF 目標)'}
---------------------------------
天平分度值 (d): {auto_unit_format(d1_g)}
機台理想極限 (0.41d): {auto_unit_format(ideal_min_w)}
機台實際最小秤量: {auto_unit_format(usp_min_w)}
客戶設定最小淨重: {auto_unit_format(snw_g)}
當前安全係數 (SF): {current_sf:.2f} (設定目標: {user_sf})
---------------------------------
※ 備註：最小秤重量不含皮重容器重量 [cite: 28, 29]。
"""
    st.code(summary)
