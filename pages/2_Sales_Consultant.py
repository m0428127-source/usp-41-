import streamlit as st
import pandas as pd

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
    with c1: d1_g = convert_to_g(st.select_slider(f"d1 ({display_unit})", options=d_converted, value=d_converted[5]), display_unit)
    with c2: d2_g = convert_to_g(st.select_slider(f"d2 ({display_unit})", options=d_converted, value=d_converted[4]), display_unit)
    active_d_g = d1_g
else:
    active_d_g = convert_to_g(st.select_slider(f"分度值 d ({display_unit})", options=d_converted, value=d_converted[4]), display_unit)
    d1_g = active_d_g

# 自動更新 STD 預設值
if active_d_g != st.session_state.last_active_d:
    st.session_state.user_std_input = float(smart_format(convert_from_g(active_d_g * 0.8, display_unit)))
    st.session_state.last_active_d = active_d_g

st.markdown("---")
col_snw, col_std = st.columns(2)
with col_snw:
    snw_g = convert_to_g(st.number_input(f"客戶目標淨重 ({display_unit})", value=float(convert_from_g(0.02, display_unit)), format="%.7g"), display_unit)

with col_std:
    if has_std == "手動輸入 STD":
        std_raw = st.number_input(f"實測標準差 STD ({display_unit})", value=st.session_state.user_std_input, format="%.7g", key="std_in")
        st.session_state.user_std_input = std_raw
        std_g = convert_to_g(std_raw, display_unit)
    else:
        st.write("模式：理論極限預估")
        std_g = 0

# --- 5. 核心計算 ---
s_limit = 0.41 * d1_g
usp_min_w = 2000 * max(std_g, s_limit)
safe_min_w = usp_min_w * user_sf
current_sf = snw_g / usp_min_w if usp_min_w > 0 else 0

# --- 6. 視覺化圖表區 ---
st.divider()
st.markdown("### 🏁 評估結論視覺化")

# 準備圖表數據
# 我們建立一個對比：法規線 vs 安全線 vs 客戶實際目標
chart_data = pd.DataFrame({
    "指標項目": ["法規底線 (SF=1)", "建議門檻 (SF={})".format(user_sf), "客戶目標"],
    "重量值 (g)": [usp_min_w, safe_min_w, snw_g]
})

# 使用 st.bar_chart 或是自定義色彩顯示
# 這裡用一個更直觀的進度條方式來模擬「安全尺」
status_color = "green" if current_sf >= user_sf else "orange" if current_sf >= 1 else "red"

# 計算目標在尺規上的位置 (以安全門檻為 100% 基準)
progress_val = min(snw_g / (safe_min_w * 1.5), 1.0) 
st.write(f"**安全狀態評級：**")
if status_color == "green": st.success(f"🛡️ 安全 (當前 SF: {current_sf:.2f})")
elif status_color == "orange": st.warning(f"⚠️ 高風險 (當前 SF: {current_sf:.2f})")
else: st.error(f"❌ 不合規 (當前 SF: {current_sf:.2f})")

# 畫出對比橫條圖
st.bar_chart(data=chart_data.set_index("指標項目"), use_container_width=True)

# 指標卡補充
c1, c2, c3 = st.columns(3)
c1.metric("法規 MinW", auto_unit_format(usp_min_w))
c2.metric(f"建議 MinW (SF={user_sf})", auto_unit_format(safe_min_w))
c3.metric("客戶目標", auto_unit_format(snw_g), delta=f"SF: {current_sf:.2f}", delta_color="normal" if current_sf >= 1 else "inverse")

st.info(f"💡 視覺化說明：藍色長條代表重量。您的目標長條必須**高於**建議門檻，才能確保在現場環境波動下依然合規。")

# --- 7. 報告摘要 ---
with st.expander("📄 查看專業文字報告"):
    summary = f"評估結果：{'✅ 合規' if current_sf >= user_sf else '❌ 建議升級'}\n機台極限：{auto_unit_format(2000*s_limit)}\n實際 MinW：{auto_unit_format(usp_min_w)}\n目標重量：{auto_unit_format(snw_g)}\n當前安全係數：{current_sf:.2f}"
    st.code(summary)
