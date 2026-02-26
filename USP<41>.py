import streamlit as st

# --- 1. 工具函數 (嚴格保持精度與自動單位轉換) ---
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

# --- 2. 網頁配置 (手機優先) ---
st.set_page_config(page_title="USP <41> 專業合規評估", layout="centered")
st.title("⚖️ USP 天平合規快速評估")
st.caption("工程師與業務專用工具 (2026 Feb 1st Edition)")

# --- 3. 側邊欄：環境檢核 ---
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("顯示單位", ["g", "mg", "kg"], index=0)
    st.divider()
    st.header("🔍 環境檢查 (USP 1251)")
    env_all = st.checkbox("水平、穩固、遠離氣流與熱源")
    preheat = st.checkbox("天平已預熱並校準完成")
    if not (env_all and preheat):
        st.warning("⚠️ 環境不理想會顯著降低安全係數")

# --- 4. 快速輸入區 (業務常用場景) ---
st.markdown("### 1️⃣ 機台規格與需求")
col_a, col_b = st.columns(2)
with col_a:
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間", "DU_多量程"])
with col_b:
    d_base_options = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
    d_converted = [float(smart_format(convert_from_g(x, display_unit))) for x in d_base_options]
    d_raw = st.select_slider(f"分度值 d ({display_unit})", options=d_converted, value=d_converted[4])
    d_g = convert_to_g(d_raw, display_unit)

snw_raw = st.number_input(f"客戶預期最小淨重 ({display_unit})", 
                         value=float(convert_from_g(0.02, display_unit)), 
                         format="%.7g")
snw_g = convert_to_g(snw_raw, display_unit)

st.markdown("### 2️⃣ 現場實測數據")
std_raw = st.number_input(f"重複性實測標準差 STD ({display_unit})", 
                         value=float(smart_format(d_raw * 0.8)), # 預設給一個參考值
                         format="%.7g")
std_g = convert_to_g(std_raw, display_unit)

# --- 5. 核心邏輯計算 (USP <41>) ---
s_threshold_g = 0.41 * d_g
actual_min_weight_g = 2000 * max(std_g, s_threshold_g)
ideal_min_weight_g = 2000 * s_threshold_g
safety_factor = snw_g / actual_min_weight_g if actual_min_weight_g > 0 else 0

# --- 6. 視覺化診斷結果 (手機優先佈局) ---
st.divider()
st.markdown("### 🏁 評估結論")

# 安全係數儀表判定
if safety_factor >= 2:
    st.success(f"### 🛡️ 安全係數 (SF): {safety_factor:.2f} (極佳)")
    st.caption("✅ 滿足 USP 1251 建議值，製程風險極低。")
elif safety_factor >= 1:
    st.warning(f"### 🛡️ 安全係數 (SF): {safety_factor:.2f} (邊緣)")
    st.caption("⚠️ 已達法規底線，但環境波動可能導致不合規，建議提升 SF 至 2。")
else:
    st.error(f"### 🛡️ 安全係數 (SF): {safety_factor:.2f} (不符合)")
    st.caption("❌ 該天平或環境無法滿足此秤量需求。")

# 三位一體對比指標卡
st.markdown("#### 📊 性能對比")
c1, c2, c3 = st.columns(3)
c1.metric("機台理論極限", auto_unit_format(ideal_min_weight_g))
c2.metric("現場實測最小秤重", auto_unit_format(actual_min_weight_g), 
          delta=f"{(actual_min_weight_g/ideal_min_weight_g):.1f}x 理論值", delta_color="inverse")
c3.metric("客戶目標淨重", auto_unit_format(snw_g))

# --- 7. 專業背書區 (預設摺疊) ---
with st.expander("📄 查看詳細法規判斷依據 (USP <41>)"):
    # 準確度測試簡易輸入
    acc_w_raw = st.number_input("準確度測試砝碼重", value=snw_raw * 10)
    acc_w_g = convert_to_g(acc_w_raw, display_unit)
    mpe_limit = acc_w_g * (0.05 / 100 / 3)
    st.markdown(f"""
    * **重複性判定標準**：$2 \\times s / m_{{目標}} \\le 0.10\\%$
    * **標準差修正**：若實測 $s < {auto_unit_format(s_threshold_g)}$，則採 ${auto_unit_format(s_threshold_g)}$ 計算。
    * **準確度建議**：砝碼不確定度 $U$ 應 $\le {auto_unit_format(mpe_limit)}$。
    """)
    if st.button("生成專業評估摘要", use_container_width=True):
        st.code(f"""
        【USP 41 天平評估報告】
        機台分度值: {auto_unit_format(d_g)}
        客戶目標淨重: {auto_unit_format(snw_g)}
        實測最小秤量: {auto_unit_format(actual_min_weight_g)}
        安全係數: {safety_factor:.2f}
        判定結論: {"符合需求" if safety_factor >= 1 else "不符合需求"}
        """)

st.divider()
st.info("💡 **業務小撇步**：若安全係數低於 2，可向客戶建議改善避震桌面或推薦更高規型號。")
