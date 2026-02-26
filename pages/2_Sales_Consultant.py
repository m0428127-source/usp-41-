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
st.caption("工程師與業務專用顧問工具 (2026 Feb 1st Edition)")

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
    # 新增：安全係數拉條 (1-10)
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
    # 在評估時我們主要看 d1 (最嚴苛/常用於最小秤量的量程)
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

# --- 5. 核心邏輯計算 (包含自定義 SF) ---
s_threshold_g = 0.41 * active_d_g
# USP 底線最小秤重 (SF=1)
usp_min_weight_g = 2000 * max(std_g, s_threshold_g)
# 客戶要求的最小秤重 (根據選擇的 SF)
required_min_weight_g = usp_min_weight_g * (user_sf / 1.0) 
# 實際當前的安全係數 (SNW / USP底線)
current_real_sf = snw_g / usp_min_weight_g if usp_min_weight_g > 0 else 0

# --- 6. 視覺化診斷結果 ---
st.divider()
st.markdown(f"### 🏁 評估結論 (目標安全係數: {user_sf})")

if current_real_sf >= user_sf:
    st.success(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (符合預期)")
    st.caption(f"✅ 滿足您設定的 SF={user_sf} 要求，製程非常穩定。")
elif current_real_sf >= 1:
    st.warning(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (高風險)")
    st.caption(f"⚠️ 雖符合 USP 〈41〉 底線，但未達到您要求的 SF={user_sf}。環境波動可能導致超差。")
else:
    st.error(f"### 🛡️ 當前安全係數 (SF): {current_real_sf:.2f} (不合規)")
    st.caption(f"❌ 低於 USP 法規底線。在此環境下，該天平無法滿足秤量需求。")

# 三位一體對比指標卡
st.markdown("#### 📊 性能對比")
c1, c2, c3 = st.columns(3)
c1.metric("機台理論極限 (SF=1)", auto_unit_format(2000 * s_threshold_g))
c2.metric(f"要求的門檻 (SF={user_sf})", auto_unit_format(usp_min_weight_g * user_sf), 
          delta=f"{user_sf}x 放大", delta_color="normal")
c3.metric("客戶目標淨重", auto_unit_format(snw_g))

# --- 7. 專業背書區 ---
with st.expander("📄 查看詳細法規判斷依據 (USP <41>)"):
    st.markdown(f"""
    * **USP 底線要求**：重複性標準差 $s$ 若小於 $0.41d$，以 $0.41d$ (${auto_unit_format(s_threshold_g)}$) 計算。
    * **法規最小秤量 (MinW)**：$2000 \\times s = {auto_unit_format(usp_min_weight_g)}$。
    * **安全係數說明**：USP 〈1251〉 建議安全係數應足夠應對環境變化。您目前設定為 **{user_sf}** 倍。
    """)
    if st.button("生成專業評估摘要", use_container_width=True):
        st.code(f"""
【USP 41 天平評估報告】
天平類型: {balance_type}
分度值 d: {auto_unit_format(active_d_g)}
設定安全係數 (SF): {user_sf}
實測最小秤量 (SF=1): {auto_unit_format(usp_min_weight_g)}
建議最小淨重 (需大於): {auto_unit_format(usp_min_weight_g * user_sf)}
客戶目標淨重: {auto_unit_format(snw_g)}
判定結論: {"✅ 符合客戶 SF 需求" if current_real_sf >= user_sf else "❌ 未達標，建議改善環境或升級規格"}
        """)

st.info("💡 **小撇步**：拉動上方的「安全係數」滑桿，可以直接向客戶展示在不同風險耐受度下，天平的秤量能力變化。")
