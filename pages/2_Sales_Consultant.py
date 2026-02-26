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
st.set_page_config(page_title="USP <41> 業務溝通工具", layout="centered")
st.title("⚖️ USP 天平合規快速評估")
st.caption("2026 最新法規版 | 業務快速提案專用")

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("顯示單位", ["g", "mg", "kg"], index=0)
    st.divider()
    st.info("💡 業務技巧：若客戶環境不佳，建議將安全係數 (SF) 設定為 3 以上。")

# --- 4. 快速輸入區 ---
st.markdown("### 1️⃣ 機台規格與安全係數")
col_type, col_sf = st.columns([1, 1])

with col_type:
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間", "DU_多量程"])

with col_sf:
    user_sf = st.select_slider("設定安全係數 (SF)", options=list(range(1, 11)), value=2)

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

st.markdown("---")
st.markdown("### 2️⃣ 環境與需求 (不知道標準差？)")

# --- 關鍵設計：環境預估選單 ---
env_scenario = st.radio(
    "選擇現場環境預估標準差 (STD):",
    ["專業實驗室 (穩定)", "一般辦公室/化驗室", "生產線/開放空間", "手動輸入特定數值"],
    index=1,
    horizontal=True
)

# 根據選單設定預設的 std_g
if env_scenario == "專業實驗室 (穩定)":
    default_std_g = active_d_g * 0.45  # 接近理論極限
elif env_scenario == "一般辦公室/化驗室":
    default_std_g = active_d_g * 1.0   # 標準表現
elif env_scenario == "生產線/開放空間":
    default_std_g = active_d_g * 2.5   # 較差表現
else:
    default_std_g = active_d_g * 1.0

col_snw, col_std = st.columns(2)
with col_snw:
    snw_raw = st.number_input(f"客戶最輕秤多少？ ({display_unit})", value=float(convert_from_g(0.02, display_unit)), format="%.7g")
    snw_g = convert_to_g(snw_raw, display_unit)

with col_std:
    if env_scenario == "手動輸入特定數值":
        std_raw = st.number_input(f"手動輸入標準差 STD ({display_unit})", value=float(smart_format(convert_from_g(default_std_g, display_unit))), format="%.7g")
    else:
        st.write(f"預估標準差: `{auto_unit_format(default_std_g)}`")
        std_raw = convert_from_g(default_std_g, display_unit)
    std_g = convert_to_g(std_raw, display_unit)

# --- 5. 核心邏輯計算 ---
s_limit_d1 = 0.41 * d1_g
effective_s = max(std_g, s_limit_d1)
usp_min_weight_g = 2000 * effective_s
current_real_sf = snw_g / usp_min_weight_g if usp_min_weight_g > 0 else 0
theoretical_limit_g = 2000 * s_limit_d1

# --- 6. 視覺化診斷結果 ---
st.divider()
st.markdown(f"### 🏁 評估結論 (目標安全係數: {user_sf})")

if current_real_sf >= user_sf:
    st.success(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (合規且建議)")
elif current_real_sf >= 1:
    st.warning(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (法規邊緣)")
else:
    st.error(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (不合規)")

# 指標卡
c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label="機台極限 (SF=1)", value=auto_unit_format(theoretical_limit_g))
with c2:
    st.metric(label="法規認定最小秤重", value=auto_unit_format(usp_min_weight_g), 
              delta=f"環境風險: {env_scenario}", delta_color="normal")
with c3:
    st.metric(label="建議最輕秤量 (含SF)", value=auto_unit_format(usp_min_weight_g * user_sf))

# --- 7. 專業背書與溝通 ---
st.info(f"💡 **建議**：在「{env_scenario}」環境下，若要達到安全係數 {user_sf}，建議最輕秤量需大於 **{auto_unit_format(usp_min_weight_g * user_sf)}**。")

with st.expander("📄 點擊查看給客戶的專業說明"):
    st.markdown(f"""
    * **為什麼要看安全係數 (SF)？**
      USP <1251> 建議，考量到天平使用一段時間後的性能飄移或環境突發震動，應設定高於法規底線 (SF=1) 的安全邊際。
    * **本評估結論：**
      目前客戶目標重量為 **{auto_unit_format(snw_g)}**。
      在本環境預估下，您的安全係數為 **{current_real_sf:.2f}**。
    """)
    if st.button("📋 複製評估簡報", use_container_width=True):
        text = f"【USP 41 評估】環境:{env_scenario} | 目標:{auto_unit_format(snw_g)} | 安全係數:{current_real_sf:.2f} | 判定:{'合規' if current_real_sf>=1 else '不合規'}"
        st.code(text)
