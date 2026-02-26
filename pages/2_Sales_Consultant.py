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

# --- 4. 快速輸入區 ---
st.markdown("### 1️⃣ 機台規格與安全係數")
col_type, col_sf = st.columns([1, 1])

with col_type:
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間", "DU_多量程"])

with col_sf:
    user_sf = st.select_slider("設定安全係數 (Safety Factor)", options=list(range(1, 11)), value=2)

d_base_options = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
d_converted = [float(smart_format(convert_from_g(x, display_unit))) for x in d_base_options]

# 雙量程處理邏輯
is_dual_range = balance_type in ["DR_多區間", "DU_多量程"]

if is_dual_range:
    c1, c2 = st.columns(2)
    with c1:
        d1_raw = st.select_slider(f"分度值 d1 (精細區) ({display_unit})", options=d_converted, value=d_converted[5])
        d1_g = convert_to_g(d1_raw, display_unit)
    with c2:
        d2_raw = st.select_slider(f"分度值 d2 (寬鬆區) ({display_unit})", options=d_converted, value=d_converted[4])
        d2_g = convert_to_g(d2_raw, display_unit)
    active_d_g = d1_g # 預設以最精細量程作為評估基準
else:
    d_raw = st.select_slider(f"分度值 d ({display_unit})", options=d_converted, value=d_converted[4])
    active_d_g = convert_to_g(d_raw, display_unit)
    d1_g = active_d_g
    d2_g = None

st.markdown("---")
st.markdown("### 2️⃣ 需求與實測")
col_snw, col_std = st.columns(2)
with col_snw:
    snw_raw = st.number_input(f"客戶預期最小淨重 ({display_unit})", value=float(convert_from_g(0.02, display_unit)), format="%.7g")
    snw_g = convert_to_g(snw_raw, display_unit)
with col_std:
    std_raw = st.number_input(f"重複性實測標準差 STD ({display_unit})", value=float(smart_format(convert_from_g(active_d_g * 0.8, display_unit))), format="%.7g")
    std_g = convert_to_g(std_raw, display_unit)

# --- 5. 核心邏輯計算 (包含雙量程理論值) ---
s_limit_d1 = 0.41 * d1_g
theoretical_min_w_d1 = 2000 * s_limit_d1

if is_dual_range:
    s_limit_d2 = 0.41 * d2_g
    theoretical_min_w_d2 = 2000 * s_limit_d2
else:
    theoretical_min_w_d2 = None

# 法規判定：使用 active_d_g (d1)
effective_s = max(std_g, s_limit_d1)
usp_min_weight_g = 2000 * effective_s
current_real_sf = snw_g / usp_min_weight_g if usp_min_weight_g > 0 else 0

# --- 6. 視覺化診斷結果 ---
st.divider()
st.markdown(f"### 🏁 評估結論 (目標安全係數: {user_sf})")

if current_real_sf >= user_sf:
    st.success(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (符合預期)")
elif current_real_sf >= 1:
    st.warning(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (高風險)")
else:
    st.error(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (不合規)")

# 三位一體對比指標卡 (雙量程優化版)
st.markdown("#### 📊 性能對比分析")
c1, c2, c3 = st.columns(3)

with c1:
    if is_dual_range:
        st.metric(label=f"理論極限 (d1={auto_unit_format(d1_g)})", value=auto_unit_format(theoretical_min_w_d1))
        st.caption(f"高量程區間 (d2) 極限: {auto_unit_format(theoretical_min_w_d2)}")
    else:
        st.metric(label=f"理論極限 (d={auto_unit_format(d1_g)})", value=auto_unit_format(theoretical_min_w_d1))

with c2:
    is_using_threshold = std_g < s_limit_d1
    st.metric(
        label="實際最小秤重 (法規值)", 
        value=auto_unit_format(usp_min_weight_g),
        delta="環境優良(0.41d修正)" if is_using_threshold else f"環境影響: {(usp_min_weight_g / theoretical_limit_g):.1f}x" if 'theoretical_limit_g' in locals() else "",
        delta_color="normal" if is_using_threshold else "inverse"
    )

with c3:
    st.metric(label="客戶目標秤重", value=auto_unit_format(snw_g))

# 針對雙量程的特別提醒
if is_dual_range and snw_g > (theoretical_min_w_d1 * 5): # 假設一個切換門檻提示
    st.info(f"💡 **雙量程提醒**：當秤量跨越至 d2 範圍時，最小秤量門檻將變為 **{auto_unit_format(theoretical_min_w_d2)}**。")

st.info(f"💡 若要滿足設定之安全係數 **SF={user_sf}**，最小淨重建議需大於：**{auto_unit_format(usp_min_weight_g * user_sf)}**")

# --- 7. 專業背書區 ---
with st.expander("📄 查看詳細法規判斷依據 (USP <41>)"):
    st.markdown(f"""
    * **d1 理論底線**：{auto_unit_format(theoretical_min_w_d1)} (基於 $0.41 \\times d1$)
    """)
    if is_dual_range:
        st.markdown(f"* **d2 理論底線**：{auto_unit_format(theoretical_min_w_d2)} (基於 $0.41 \\times d2$)")
    
    if st.button("生成專業評估摘要", use_container_width=True):
        summary = f"""
【USP 41 雙量程評估報告】
天平類型: {balance_type}
精細分度值 d1: {auto_unit_format(d1_g)}
理論極限 d1 MinW: {auto_unit_format(theoretical_min_w_d1)}
"""
        if is_dual_range:
            summary += f"寬鬆分度值 d2: {auto_unit_format(d2_g)}\n理論極限 d2 MinW: {auto_unit_format(theoretical_min_w_d2)}\n"
        
        summary += f"設定安全係數 (SF): {user_sf}\n法規認定 MinW: {auto_unit_format(usp_min_weight_g)}\n客戶目標淨重: {auto_unit_format(snw_g)}\n判定結論: {'✅ 符合' if current_real_sf >= user_sf else '❌ 不符合'}"
        st.code(summary)
