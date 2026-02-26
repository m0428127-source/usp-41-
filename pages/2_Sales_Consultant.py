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
st.caption("工程師與業務專用顧問工具 (Official Feb 1, 2026)")

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("顯示單位", ["g", "mg", "kg"], index=0)
    st.divider()
    st.header("🔍 環境檢查 (USP 1251)")
    env_all = st.checkbox("水平、穩固、遠離氣流與熱源")
    preheat = st.checkbox("天平已預熱並校準完成")
    st.caption("依據 USP <1251> 建議維護良好的秤量環境。")

# --- 4. 快速輸入區 ---
st.markdown("### 1️⃣ 機台規格與安全係數")
col_type, col_sf = st.columns([1, 1])

with col_type:
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間", "DU_多量程"])

with col_sf:
    # 安全係數拉條 (1-10)
    user_sf = st.select_slider("設定安全係數 (Safety Factor)", options=list(range(1, 11)), value=2)

# 分度值選擇邏輯
d_base_options = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
d_converted = [float(smart_format(convert_from_g(x, display_unit))) for x in d_base_options]

if balance_type in ["DR_多區間", "DU_多量程"]:
    c1, c2 = st.columns(2)
    with c1:
        d1_raw = st.select_slider(f"分度值 d1 (低量程) ({display_unit})", options=d_converted, value=d_converted[5])
        d1_g = convert_to_g(d1_raw, display_unit)
    with c2:
        d2_raw = st.select_slider(f"分度值 d2 (高量程) ({display_unit})", options=d_converted, value=d_converted[4])
        d2_g = convert_to_g(d2_raw, display_unit)
    active_d_g = d1_g
else:
    d_raw = st.select_slider(f"分度值 d ({display_unit})", options=d_converted, value=d_converted[4])
    active_d_g = convert_to_g(d_raw, display_unit)

st.markdown("---")
st.markdown("### 2️⃣ 需求與實測")
col_snw, col_std = st.columns(2)
with col_snw:
    snw_raw = st.number_input(f"客戶預期最小淨重 ({display_unit})", 
                             value=float(convert_from_g(0.02, display_unit)), format="%.7g")
    snw_g = convert_to_g(snw_raw, display_unit)
with col_std:
    std_raw = st.number_input(f"重複性實測標準差 STD ({display_unit})", 
                             value=float(smart_format(convert_from_g(active_d_g * 0.8, display_unit))), format="%.7g")
    std_g = convert_to_g(std_raw, display_unit)

# --- 5. 核心邏輯計算 (USP <41>) ---
# 依據法規，若 s < 0.41d，則以 0.41d 計算
s_threshold_g = 0.41 * active_d_g
effective_s = max(std_g, s_threshold_g)
# 最小秤量公式 m = 2000 * s
usp_min_weight_g = 2000 * effective_s
current_real_sf = snw_g / usp_min_weight_g if usp_min_weight_g > 0 else 0

# --- 6. 視覺化診斷結果 ---
st.divider()
st.markdown(f"### 🏁 評估結論 (目標安全係數: {user_sf})")

if current_real_sf >= user_sf:
    st.success(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (符合預期)")
    st.caption(f"✅ 滿足設定要求。USP <1251> 指出增加安全係數可補償環境隨機波動。")
elif current_real_sf >= 1:
    st.warning(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (高風險)")
    st.caption("⚠️ 雖符合 USP <41> 底線，但未達設定之安全邊際，環境變動可能導致不合規。")
else:
    st.error(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (不合規)")
    st.caption("❌ 此機台於目前環境下不符合 USP <41> 重複性要求。")

# 三位一體對比指標卡
st.markdown("#### 📊 性能對比")
c1, c2, c3 = st.columns(3)

# 1. 機台性能極限 (0.41d)
theoretical_limit_g = 2000 * s_threshold_g
c1.metric(
    label=f"機台性能極限 (d={auto_unit_format(active_d_g)}, SF=1)", 
    value=auto_unit_format(theoretical_limit_g),
    help="根據 USP <41> 之 0.41d 修正得出之理論極限。"
)

# 2. 實際最小秤重 (包含法規修正邏輯)
is_using_threshold = std_g < s_threshold_g
c2.metric(
    label="實際最小秤重 (法規判定值)", 
    value=auto_unit_format(usp_min_weight_g),
    delta="環境優良(採0.41d修正)" if is_using_threshold else f"環境影響: {(usp_min_weight_g / theoretical_limit_g):.1f}x",
    delta_color="normal" if is_using_threshold else "inverse",
    help="依據 USP <41> 規範：若 s < 0.41d，則採 0.41d 計算。"
)

# 3. 客戶目標秤重
c3.metric(
    label="客戶目標秤重", 
    value=auto_unit_format(snw_g)
)

st.info(f"💡 若要滿足設定之安全係數 **SF={user_sf}**，最小淨重建議需大於：**{auto_unit_format(usp_min_weight_g * user_sf)}**")

# --- 7. 專業背書區 ---
with st.expander("📄 查看詳細法規判斷依據 (USP <41>)"):
    st.markdown(f"""
    * **重複性要求**：$2 \times s / m \le 0.10\%$。
    * **標準差修正**：若實測 $s < 0.41d$，則以 $0.41d$ (${auto_unit_format(s_threshold_g)}$) 計算。
    * **最小秤量 (MinW)**：$2000 \\times s = {auto_unit_format(usp_min_weight_g)}$。
    * **安全係數 (SF)**：根據 USP <1251>，建立安全係數可確保在日常環境波動下仍維持合規。
    """)
    if st.button("生成專業評估摘要", use_container_width=True):
        st.code(f"""
【USP 41 天平評估報告】
天平類型: {balance_type}
分度值 d: {auto_unit_format(active_d_g)}
設定安全係數 (SF): {user_sf}
法規最小秤量 (SF=1): {auto_unit_format(usp_min_weight_g)}
建議最小淨重 (需大於): {auto_unit_format(usp_min_weight_g * user_sf)}
客戶目標淨重: {auto_unit_format(snw_g)}
判定結論: {"✅ 符合客戶需求" if current_real_sf >= user_sf else "❌ 未達標，建議改善環境或調整機型"}
        """)

st.divider()
st.caption("註：本工具計算邏輯嚴格遵循 USP-NF 〈41〉 與 〈1251〉 2026年2月1日生效之最新版本規範。")
