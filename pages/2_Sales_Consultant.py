import streamlit as st

# --- 1. 工具函數 ---
def format_dynamic(value):
    """ 強制動態修剪，輸入 0.1 顯示 0.1，輸入 0.02 顯示 0.02 """
    if value is None or value == 0: return "0"
    # 使用 .7f 展開後去掉末尾 0
    formatted = f"{value:.7f}".rstrip('0').rstrip('.')
    return formatted if formatted != "" else "0"

def auto_unit_format(g_value):
    """ 自動轉換單位並套用動態格式 """
    abs_val = abs(g_value)
    if abs_val == 0: return f"0 {display_unit}"
    if abs_val < 0.001: return f"{format_dynamic(g_value * 1000)} mg"
    elif abs_val >= 1000: return f"{format_dynamic(g_value / 1000)} kg"
    else: return f"{format_dynamic(g_value)} g"

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

# --- 3. 初始化 Session State ---
if 'snw_val' not in st.session_state:
    st.session_state.snw_val = 0.02 # 預設初始值
if 'last_active_d' not in st.session_state:
    st.session_state.last_active_d = None

# --- 4. 側邊欄 ---
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("顯示單位", ["g", "mg", "kg"], index=0)
    st.divider()
    st.header("🔍 USP 1251 環境檢查")
    st.checkbox("天平放置於穩固、水平檯面")
    st.checkbox("環境受控，且遠離直接氣流")

st.markdown("### 1️⃣ 設定規格與需求")
col1, col2 = st.columns(2)
with col1:
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間", "DU_多量程"])
    user_sf = st.select_slider("目標安全係數 (SF)", options=list(range(1, 11)), value=2)
with col2:
    has_std = st.radio("評估模式", ["手動輸入實測 Std", "無數據 (理論預估)"])

# 分度值清單
d_base_options = [1.0, 0.5, 0.2, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
d_converted = [float(convert_from_g(x, display_unit)) for x in d_base_options]

if balance_type in ["DR_多區間", "DU_多量程"]:
    c1, c2 = st.columns(2)
    with c1: 
        d1_val = st.select_slider(f"d1 (精細) ({display_unit})", options=d_converted, value=d_converted[5], format_func=format_dynamic)
        d1_g = convert_to_g(d1_val, display_unit)
    with c2: 
        d2_val = st.select_slider(f"d2 (寬鬆) ({display_unit})", options=d_converted, value=d_converted[4], format_func=format_dynamic)
        d2_g = convert_to_g(d2_val, display_unit)
    active_d_g = d1_g
else:
    d_val = st.select_slider(f"分度值 d ({display_unit})", options=d_converted, value=d_converted[4], format_func=format_dynamic)
    active_d_g = convert_to_g(d_val, display_unit)
    d1_g = active_d_g

st.markdown("---")
# --- 數據輸入區與防呆 ---
col_snw, col_std = st.columns(2)

with col_snw:
    is_snw_unknown = st.checkbox("尚未決定最小淨重量")
    if not is_snw_unknown:
        # 使用 format_dynamic 處理呈現，並限制 min_value 確保不為 0 或負
        snw_raw = st.number_input(f"客戶設定最小淨重量 ({display_unit})", 
                                  min_value=0.0000001, 
                                  value=convert_from_g(0.02, display_unit),
                                  format="%.7f", step=0.01)
        snw_g = convert_to_g(snw_raw, display_unit)
    else:
        snw_g = None

with col_std:
    if has_std == "手動輸入實測 Std":
        # 預設 Std 初始值隨 d 變動，但限制最小不得為 0
        default_std = convert_from_g(active_d_g * 0.8, display_unit)
        std_raw = st.number_input(f"重複性實測標準差 Std ({display_unit})", 
                                  min_value=0.0000001,
                                  value=default_std,
                                  format="%.7f", step=0.0001)
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

# 計算安全係數 (若勾選尚未決定，則為 None)
current_sf = snw_g / usp_min_w if (snw_g is not None and usp_min_w > 0) else None

# --- 6. 結論顯示區 ---
st.divider()
st.markdown("### 🏁 專業評估結論")

if is_snw_unknown:
    st.info("💡 目前已計算出機台最小秤量門檻。請於左側輸入「客戶設定最小淨重量」以進行 SF 判定。")
else:
    if current_sf >= user_sf:
        st.success(f"🛡️ **安全狀態：優良** | 當前實測 SF: **{current_sf:.2f}**")
    elif current_sf >= 1:
        st.warning(f"⚠️ **安全狀態：高風險** | 已達法規底線，但低於安全係數目標。")
    else:
        st.error(f"❌ **安全狀態：不合規** | 客戶目標重量小於法規判定之最小秤量！")

# 指標卡 (若 SNW 未知，則第三張卡片顯示待定)
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("機台理想最小秤重量", auto_unit_format(ideal_min_w))
    st.caption("基於 $0.41d$ 理論底線")
with c2:
    st.metric("機台實際最小秤重量", auto_unit_format(usp_min_w))
    st.caption("⚠️ 已修正" if is_corrected else "✅ 實測計算")
with c3:
    if not is_snw_unknown:
        st.metric("客戶設定最小淨重量", auto_unit_format(snw_g), 
                  delta=f"SF: {current_sf:.2f}" if current_sf else None, 
                  delta_color="normal" if current_sf and current_sf >= 1 else "inverse")
        st.caption("Smallest Net Weight")
    else:
        st.metric("客戶設定最小淨重量", "待定")
        st.caption("尚未輸入 SNW")

# --- 7. 報告摘要 (含一鍵複製) ---
st.divider()
st.markdown("### 📄 專業評估報告摘要")

if is_snw_unknown:
    sf_text = "待決定最小淨重後計算"
    snw_text = "待定"
    result_text = "待定 (請輸入 SNW 以判定)"
else:
    sf_text = f"{current_sf:.2f}"
    snw_text = auto_unit_format(snw_g)
    result_text = "✅ 符合法規" if current_sf >= 1 else "❌ 不符合法規"

copyable_report = f"""【USP 41 專業評估報告 - 2026 Edition】
------------------------------------------
評估結果：{result_text}
天平分度值 (d): {auto_unit_format(d1_g)}
理論最小秤量極限 (0.41d): {auto_unit_format(ideal_min_w)}
重複性實測標準差 (Std): {auto_unit_format(std_g) if std_g > 0 else "N/A (理論預估)"}
判定最小秤重量 (MinW): {auto_unit_format(usp_min_w)}
客戶設定最小淨重 (SNW): {snw_text}
實際安全係數 (SF): {sf_text} (目標要求: {user_sf})
------------------------------------------
※ 備註：依據 USP <41>，最小秤重量不應包含皮重容器。
"""

st.code(copyable_report, language="text")

with st.expander("📘 詳細判定邏輯"):
    st.write(f"- 判定門檻 (0.41d): {format_dynamic(convert_from_g(s_limit, display_unit))} {display_unit}")
    st.write(f"- 有效 Std 值: {format_dynamic(convert_from_g(effective_s, display_unit))} {display_unit}")
