import streamlit as st

# --- 1. 工具函數 (保持核心邏輯) ---
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

# --- 2. 網頁配置 (針對手機優化) ---
st.set_page_config(page_title="USP <41> 合規指引", layout="centered")
st.title("⚖️ USP 〈41〉 天平測試合規指引")
st.caption("依據標準：USP-NF 〈41〉 (2026.02.01 Official Edition)")

# 全域顯示單位設定
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("顯示單位", ["g", "mg", "kg"], index=0)

# --- 3. 第一步：天平規格與即時法規導引 ---
st.markdown("### 📋 1️⃣ 天平規格與法規導引")
with st.container(border=True):
    # 天平類型選擇
    balance_type = st.selectbox(
        "選擇天平類型", 
        ["單一量程", "DR_多區間 (Multi-interval)", "DU_多量程 (Multiple range)"]
    )
    
    # 💡 關鍵法規導引：根據選擇顯示不同提醒
    if "DR" in balance_type:
        st.warning("⚠️ **DR 類型測試須知**：\n依據 USP <41>，DR 僅須測試其**最精細量程 (Finest range)**。若您的量測過程中涉及雙量程轉換的準確性需求，建議請選擇 **DU 類型**。")
    elif "DU" in balance_type:
        st.info("ℹ️ **DU 類型測試須知**：\nDU 視為兩組獨立天平，法規要求須分別針對「細量程」與「粗量程」進行數據輸入與判定。")

    raw_max_cap = st.number_input(f"天平最大秤量 Max Capacity ({display_unit})", value=float(convert_from_g(220.0, display_unit)))
    max_cap_g = convert_to_g(raw_max_cap, display_unit)

    # 41 規範：砝碼區間預檢
    rep_min, rep_max = 0.100, max_cap_g * 0.05
    acc_min, acc_max = max_cap_g * 0.05, max_cap_g
    
    st.markdown(f"""
    **🔍 USP <41> 砝碼重量建議：**
    - **重複性測試**：{auto_unit_format(rep_min)} ~ {auto_unit_format(rep_max)}
    - **準確度測試**：{auto_unit_format(acc_min)} ~ {auto_unit_format(acc_max)}
    """)

# --- 4. 第二步：測試數據輸入 (手機垂直排版) ---
st.markdown("### 📊 2️⃣ 執行測試並填入數據")
with st.container(border=True):
    d_opts = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001]
    d_vals = [float(smart_format(convert_from_g(x, display_unit))) for x in d_opts]
    
    # 擬用砝碼檢核
    c1, c2 = st.columns(2)
    with c1:
        rep_w_raw = st.number_input(f"重複性砝碼 ({display_unit})", value=float(convert_from_g(0.1, display_unit)))
    with c2:
        acc_w_raw = st.number_input(f"準確度砝碼 ({display_unit})", value=float(convert_from_g(200.0, display_unit)))
    
    rep_w_g = convert_to_g(rep_w_raw, display_unit)
    acc_w_g = convert_to_g(acc_w_raw, display_unit)

    # 數據輸入邏輯
    ranges = []
    if "DU" in balance_type:
        st.markdown("---")
        st.markdown("**量程 1 (細量程)**")
        d1 = st.select_slider("可讀數 d1", options=d_vals, value=d_vals[5], key="d1")
        std1 = st.number_input("實測標準差 STD1", value=float(convert_from_g(0.000008, display_unit)), key="s1")
        snw1 = st.number_input("預期最小淨重 SNW1", value=float(convert_from_g(0.02, display_unit)), key="snw1")
        
        st.markdown("---")
        st.markdown("**量程 2 (粗量程)**")
        d2 = st.select_slider("可讀數 d2", options=d_vals, value=d_vals[4], key="d2")
        std2 = st.number_input("實測標準差 STD2", value=float(convert_from_g(0.00008, display_unit)), key="s2")
        snw2 = st.number_input("預期最小淨重 SNW2", value=float(convert_from_g(0.2, display_unit)), key="snw2")
        
        ranges = [{"d": convert_to_g(d1, display_unit), "std": convert_to_g(std1, display_unit), "snw": convert_to_g(snw1, display_unit), "lbl": "量程 1 (Fine)"},
                  {"d": convert_to_g(d2, display_unit), "std": convert_to_g(std2, display_unit), "snw": convert_to_g(snw2, display_unit), "lbl": "量程 2 (Coarse)"}]
    else:
        lbl = "細量程" if "DR" in balance_type else "單一量程"
        d = st.select_slider(f"可讀數 d ({lbl})", options=d_vals, value=d_vals[4])
        std = st.number_input(f"實測標準差 STD", value=float(convert_from_g(0.00008, display_unit)))
        snw = st.number_input(f"預期最小淨重 SNW", value=float(convert_from_g(0.02, display_unit)))
        ranges = [{"d": convert_to_g(d, display_unit), "std": convert_to_g(std, display_unit), "snw": convert_to_g(snw, display_unit), "lbl": lbl}]

# --- 5. 第三步：產出判定報告 ---
st.divider()
if st.button("🚀 產出合規判定報告", use_container_width=True, type="primary"):
    st.subheader("🏁 USP 〈41〉 設備診斷報告")
    
    # 砝碼合規性先判斷
    is_w_ok = (rep_min <= rep_w_g <= rep_max) and (acc_min <= acc_w_g <= acc_max)
    if is_w_ok:
        st.success("✅ 測試砝碼選用：符合 USP <41> 規範區間")
    else:
        st.error("❌ 測試砝碼選用：重量超出 USP <41> 規定區間")

    for r in ranges:
        s_limit = 0.41 * r['d']
        actual_min_w = 2000 * max(r['std'], s_limit)
        sf = r['snw'] / actual_min_w if actual_min_w > 0 else 0
        
        with st.container(border=True):
            st.markdown(f"#### 📍 {r['lbl']} (d = {auto_unit_format(r['d'])})")
            
            # 總結判定
            if r['snw'] >= actual_min_w:
                st.success(f"**判定：符合需求**")
            else:
                st.error(f"**判定：不合規 (SNW 過小)**")
            
            # 手機版指標卡
            m1, m2, m3 = st.columns(3)
            m1.metric("法定 MinW", auto_unit_format(actual_min_w))
            m2.metric("需求 SNW", auto_unit_format(r['snw']))
            m3.metric("安全係數", f"{sf:.2f}")
            
            # 技術細節
            with st.expander("🔍 詳閱技術細節 (包含 0.41d 修正)"):
                st.write(f"- 實測標準差: {auto_unit_format(r['std'])}")
                st.write(f"- 0.41d 修正界限: {auto_unit_format(s_limit)}")
                if r['std'] < s_limit:
                    st.caption("ℹ️ 標準差過小，已依法規強制採用 0.41d 進行計算。")
                
                # 準確度 MPE 提醒
                mpe_limit = acc_w_g * (0.05/100/3)
                st.write(f"**準確度檢核：**")
                st.write(f"- 砝碼 `{auto_unit_format(acc_w_g)}` 證書 U 須 ≤ `{auto_unit_format(mpe_limit)}` (0.05% 的 1/3)")

st.caption("本工具依據 USP 〈41〉 2026 修正版邏輯開發，僅供合規性評估參考。")
