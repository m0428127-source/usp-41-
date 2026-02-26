import streamlit as st

# --- 1. 工具函數 (顯示邏輯優化) ---
def format_dynamic(value):
    """ 根據數值自動修剪，如果輸入 0.1 就顯示 0.1，不補多餘的 0 """
    if value == 0: return "0"
    # 使用 .7f 計算後，去掉右側多餘的 0 與點
    return f"{value:.7f}".rstrip('0').rstrip('.')

def auto_unit_format(g_value):
    """ 報告與指標卡使用的單位格式化 """
    abs_val = abs(g_value)
    if abs_val == 0: return "0 g"
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
st.caption("工程師實測 / 業務快速提案 專業工具版 (Official Feb 1, 2026)")

# --- 3. 初始化 Session State ---
if 'user_std_input' not in st.session_state:
    st.session_state.user_std_input = None
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

# 修正的可讀數清單
d_base_options = [1.0, 0.5, 0.2, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
d_converted = [float(convert_from_g(x, display_unit)) for x in d_base_options]

# 選擇分度值 (d)
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

# 自動更新 Std 預設值
if active_d_g != st.session_state.last_active_d:
    st.session_state.user_std_input = float(convert_from_g(active_d_g * 0.8, display_unit))
    st.session_state.last_active_d = active_d_g

st.markdown("---")
col_snw, col_std = st.columns(2)
with col_snw:
    # 內部高精度輸入，顯示時會根據 format_dynamic 處理
    snw_raw = st.number_input(f"客戶設定最小淨重量 ({display_unit})", 
                              value=float(convert_from_g(0.02, display_unit)), 
                              format="%.7f")
    snw_g = convert_to_g(snw_raw, display_unit)

with col_std:
    if has_std == "手動輸入實測 Std":
        std_raw = st.number_input(f"重複性實測標準差 Std ({display_unit})", 
                                  value=st.session_state.user_std_input, 
                                  format="%.7f", key="std_in")
        st.session_state.user_std_input = std_raw
        std_g = convert_to_g(std_raw, display_unit)
    else:
        st.info("ℹ️ 模式：機台理論極限預估")
        std_g = 0

# --- 5. 核心計算 ---
s_limit = 0.41 * d1_g
is_corrected = std_g < s_limit
effective_s = max(std_g, s_limit)

usp_min_w = 2000 * effective_s
ideal_min_w = 2000 * s_limit
current_sf = snw_g / usp_min_w if usp_min_w > 0 else 0

# --- 6. 專業結論面板 ---
st.divider()
st.markdown("### 🏁 專業評估結論")

if current_sf >= user_sf:
    st.success(f"🛡️ **安全狀態：優良** | 當前實測 SF: **{current_sf:.2f}**")
elif current_sf >= 1:
    st.warning(f"⚠️ **安全狀態：高風險** | 已達法規底線，但低於安全係數目標。")
else:
    st.error(f"❌ **安全狀態：不合規** | 客戶目標重量小於法規判定之最小秤量！")

# 指標卡補充 (動態顯示位數)
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("機台理想最小秤重量", auto_unit_format(ideal_min_w))
    st.caption("基於 $0.41d$ 理論底線")

with c2:
    st.metric("機台實際最小秤重量", auto_unit_format(usp_min_w))
    st.caption("⚠️ 已修正" if is_corrected else "✅ 實測計算")

with c3:
    st.metric("客戶設定最小淨重量", auto_unit_format(snw_g), 
              delta=f"SF: {current_sf:.2f}", 
              delta_color="normal" if current_sf >= 1 else "inverse")
    st.caption("Smallest Net Weight")

# --- 7. 美化報告摘要 (含一鍵複製功能) ---
st.divider()
st.markdown("### 📄 專業評估報告摘要")
st.info("下方內容可直接複製，用於 E-mail 或客戶提案簡報：")

# 建構純文字報告內容
copyable_report = f"""【USP 41 專業評估報告 - 2026 Edition】
------------------------------------------
評估結果：{"✅ 符合法規" if current_sf >= 1 else "❌ 不符合法規"}
安全水位：{"🛡️ 充足" if current_sf >= user_sf else "⚠️ 建議提升天平等級"}

[設備規格]
- 天平分度值 (d): {auto_unit_format(d1_g)}
- 理論最小秤量極限 (0.41d): {auto_unit_format(ideal_min_w)}

[稱量性能]
- 重複性實測標準差 (Std): {auto_unit_format(std_g) if std_g > 0 else "N/A (理論預估)"}
- 判定最小秤重量 (MinW): {auto_unit_format(usp_min_w)}

[應用判定]
- 客戶設定最小淨重 (SNW): {auto_unit_format(snw_g)}
- 實際安全係數 (SF): {current_sf:.2f} (目標要求: {user_sf})
------------------------------------------
※ 備註：依據 USP <41>，最小秤重量不應包含皮重容器。
"""

# 使用 st.code 實現一鍵複製
st.code(copyable_report, language="text")

with st.expander("📘 查看詳細判定邏輯 (USP <41> / <1251>)"):
    st.write(f"""
    - **判定公式**：$2s / m \le 0.10\%$
    - **Std 修正**：實測 Std ({format_dynamic(convert_from_g(std_g, display_unit))}) 
      {" < " if is_corrected else " > "} 修正門檻 ({format_dynamic(convert_from_g(s_limit, display_unit))})
    - **最終計算用有效 Std**：{format_dynamic(convert_from_g(effective_s, display_unit))} {display_unit}
    """)
