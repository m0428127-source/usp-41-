import streamlit as st

# --- 1. 工具函數 (強制純小數顯示) ---
def smart_format(value):
    """ 強制展開小數，移除多餘的 0，徹底杜絕科學記號 """
    if value == 0: return "0"
    # 使用 .7f 確保 7 位精度，並修剪結尾的 0
    return f"{value:.7f}".rstrip('0').rstrip('.')

def auto_unit_format(g_value):
    """ 根據單位自動轉換並加上單位字串 """
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
st.caption("工程師實測 / 業務快速提案 專業工具版 (2026 Edition)")

# --- 3. 初始化 Session State (記憶功能) ---
if 'user_std_input' not in st.session_state:
    st.session_state.user_std_input = None
if 'last_active_d' not in st.session_state:
    st.session_state.last_active_d = None

# --- 4. 側邊欄與環境檢查 ---
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("顯示單位", ["g", "mg", "kg"], index=0)
    st.divider()
    st.header("🔍 USP 1251 環境檢查")
    st.checkbox("天平放置於穩固、水平、防震檯面")
    st.checkbox("環境溫濕度受控，且遠離直接氣流")
    st.checkbox("天平已開機預熱並完成內部校準")

st.markdown("### 1️⃣ 設定規格與需求")
col1, col2 = st.columns(2)
with col1:
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間", "DU_多量程"])
    user_sf = st.select_slider("目標安全係數 (SF)", options=list(range(1, 11)), value=2)
with col2:
    has_std = st.radio("評估模式", ["手動輸入實測 STD", "無數據 (理論極限預估)"])

# 修正的可讀數清單 (符合使用者需求)
d_base_options = [1.0, 0.5, 0.2, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
d_converted = [float(convert_from_g(x, display_unit)) for x in d_base_options]

def format_d_label(val):
    return smart_format(val)

# 選擇分度值 (d)
if balance_type in ["DR_多區間", "DU_多量程"]:
    c1, c2 = st.columns(2)
    with c1: 
        d1_val = st.select_slider(f"d1 (精細) ({display_unit})", options=d_converted, value=d_converted[5], format_func=format_d_label)
        d1_g = convert_to_g(d1_val, display_unit)
    with c2: 
        d2_val = st.select_slider(f"d2 (寬鬆) ({display_unit})", options=d_converted, value=d_converted[4], format_func=format_d_label)
        d2_g = convert_to_g(d2_val, display_unit)
    active_d_g = d1_g
else:
    d_val = st.select_slider(f"分度值 d ({display_unit})", options=d_converted, value=d_converted[4], format_func=format_d_label)
    active_d_g = convert_to_g(d_val, display_unit)
    d1_g = active_d_g

# 自動更新 STD 預設值 (避免換檔時數據不合理)
if active_d_g != st.session_state.last_active_d:
    st.session_state.user_std_input = float(convert_from_g(active_d_g * 0.8, display_unit))
    st.session_state.last_active_d = active_d_g

st.markdown("---")
col_snw, col_std = st.columns(2)
with col_snw:
    snw_raw = st.number_input(f"客戶設定最小淨重量 ({display_unit})", 
                              value=float(convert_from_g(0.02, display_unit)), 
                              format="%.7f")
    snw_g = convert_to_g(snw_raw, display_unit)

with col_std:
    if has_std == "手動輸入實測 STD":
        std_raw = st.number_input(f"重複性實測標準差 STD ({display_unit})", 
                                  value=st.session_state.user_std_input, 
                                  format="%.7f", key="std_in")
        st.session_state.user_std_input = std_raw
        std_g = convert_to_g(std_raw, display_unit)
    else:
        st.info("ℹ️ 模式：機台理論極限預估")
        std_g = 0

# --- 5. 核心計算 (USP <41> 邏輯) ---
s_limit = 0.41 * d1_g
# 判斷標準差是否小於 0.41d
is_corrected = std_g < s_limit
effective_s = max(std_g, s_limit)

usp_min_w = 2000 * effective_s
ideal_min_w = 2000 * s_limit
current_sf = snw_g / usp_min_w if usp_min_w > 0 else 0

# --- 6. 結論顯示區 ---
st.divider()
st.markdown("### 🏁 專業評估結論")

# 狀態判定面板
if current_sf >= user_sf:
    st.success(f"🛡️ **安全狀態：優良** | 當前實測 SF: **{current_sf:.2f}** (目標: {user_sf})")
elif current_sf >= 1:
    st.warning(f"⚠️ **安全狀態：高風險** | 已符合法規底線，但未達到安全係數目標。")
else:
    st.error(f"❌ **安全狀態：不合規** | 客戶目標重量小於法規判定之最小秤量！")

# 指標卡補充
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("機台理想最小秤重量", auto_unit_format(ideal_min_w))
    st.caption("基於 $0.41d$ 理論底線")

with c2:
    st.metric("機台實際最小秤重量", auto_unit_format(usp_min_w))
    # 這裡加入動態備註
    if is_corrected:
        st.caption("⚠️ 已採用 $0.41d$ 修正計算")
    else:
        st.caption("✅ 採用實測標準差計算")

with c3:
    st.metric("客戶設定最小淨重量", auto_unit_format(snw_g), 
              delta=f"SF: {current_sf:.2f}", 
              delta_color="normal" if current_sf >= 1 else "inverse")
    st.caption("Smallest Net Weight (SNW)")

st.divider()
with st.expander("📘 USP <41> & <1251> 判定標準與公式細節"):
    st.markdown(f"""
    * **重複性判定公式**：$2s / m \le 0.10\%$ (其中 $s$ 為標準差，$m$ 為淨重)
    * **最小秤重量公式**：$m_{{min}} = 2000 \times s_{{eff}}$
    * **標準差修正原則**：若實測 $s < 0.41d$，則以 $0.41d$ 作為計算標準 ($s_{{eff}} = 0.41d$)。
    * **當前狀態**：
        * 分度值 ($d$): `{smart_format(convert_from_g(d1_g, display_unit))} {display_unit}`
        * 修正標準 ($0.41d$): `{smart_format(convert_from_g(s_limit, display_unit))} {display_unit}`
        * 最終計算標準差 ($s_{{eff}}$): `{smart_format(convert_from_g(effective_s, display_unit))} {display_unit}`
    """)

# --- 7. 報告摘要美化 ---
with st.expander("📄 點擊展開：專業評估報告電子摘要"):
    summary_md = f"""
    ### ⚖️ USP <41> Balances Assessment Report
    ---
    **1. 設備基本規格**
    - 天平類型: `{balance_type}`
    - 分度值 (d): `{auto_unit_format(d1_g)}`
    - 理論最小秤量極限: `{auto_unit_format(ideal_min_w)}`

    **2. 稱量性能判定**
    - 實測標準差 (STD): `{auto_unit_format(std_g) if std_g > 0 else "N/A"}`
    - **法規判定最小秤量 (MinW):** `{auto_unit_format(usp_min_w)}`

    **3. 應用合規判定**
    - 客戶設定淨重: `{auto_unit_format(snw_g)}`
    - **當前安全係數 (SF):** `{current_sf:.2f}` (目標要求: {user_sf})
    - **最終結論:** `{"✅ 符合 USP 41 規範" if current_sf >= 1 else "❌ 不符合 USP 41 規範"}`
    ---
    *註：本報告基於 2026/02/01 生效之 USP 官方章節計算。*
    """
    st.markdown(summary_md)
