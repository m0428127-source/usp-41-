import streamlit as st

# --- 工具函數：智慧格式化 (支援高精度且自動去零，防止科學記號) ---
def smart_format(value):
    if value == 0:
        return "0"
    formatted = f"{value:.7g}"
    return formatted

# --- 診斷報告專用自動單位轉換 ---
def auto_unit_format(g_value):
    abs_val = abs(g_value)
    if abs_val == 0:
        return "0 g"
    if abs_val < 0.001:
        return f"{smart_format(g_value * 1000)} mg"
    elif abs_val >= 1000:
        return f"{smart_format(g_value / 1000)} kg"
    else:
        return f"{smart_format(g_value)} g"

# --- 單位換算工具 ---
def convert_to_g(value, unit):
    if unit == "mg": return value / 1000
    if unit == "kg": return value * 1000
    return value

def convert_from_g(value, unit):
    if unit == "mg": return value * 1000
    if unit == "kg": return value / 1000
    return value

# 設定網頁標題與風格
st.set_page_config(page_title="USP <41> & <1251> 專業合規工作站", layout="wide")
st.title("⚖️ USP 〈41〉 & 〈1251〉 天平測試合規工作站")
st.caption("依據標準：USP-NF 〈41〉 & 〈1251〉 (Official Feb 1, 2026)")

# --- 側邊欄：環境檢查 ---
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("偏好顯示單位", ["g", "mg", "kg"], index=0)
    
    st.divider()
    st.header("🔍 1. 檢查前作為 (Pre-check)")
    env_surface = st.checkbox("水平且非磁性的穩固表面")
    env_location = st.checkbox("遠離氣流、門窗、震動源與熱源")
    env_static = st.checkbox("濕度控制適當或具備除靜電措施")
    balance_status = st.checkbox("天平已預熱並完成水平調整")
    
    if not (env_surface and env_location and env_static and balance_status):
        st.warning("⚠️ 依循 USP<1251> 環境檢核未完成。")
    else:
        st.success("✅ 環境檢查完成。")

# --- 主頁面邏輯 ---
range_data = []
p_step = 0.0000001
p_format = "%.7g"

# --- 數據輸入區 (手機優化：整合為四個分頁) ---
with st.expander(f"📥 測試參數與規格輸入 ({display_unit})", expanded=True):
    tab_base, tab_spec, tab_std, tab_acc = st.tabs([
        "⚖️ 規格基礎", 
        "📏 可讀數與淨重", 
        "📊 重複性測試", 
        "🎯 準確性測試"
    ])
    
    with tab_base:
        balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間 (Multi-interval)", "DU_多量程 (Multiple range)"])
        raw_max_cap = st.number_input(f"天平最大秤重量 Max Capacity ({display_unit})", value=float(convert_from_g(220.0, display_unit)), step=p_step, format=p_format)
        max_cap_g = convert_to_g(raw_max_cap, display_unit)
        is_manufacturing = st.checkbox("用於製造用途 (Manufacturing)?")

    if is_manufacturing:
        st.error("🚨 **法規邊界提醒**：USP 〈41〉 不涵蓋「製造用」天平。")
    else:
        if balance_type == "DU_多量程 (Multiple range)":
            with tab_spec:
                d1_raw = st.number_input(f"實際分度值 d1 ({display_unit}) - 量程 1", value=float(convert_from_g(0.00001, display_unit)), step=p_step, format=p_format)
                d2_raw = st.number_input(f"實際分度值 d2 ({display_unit}) - 量程 2", value=float(convert_from_g(0.0001, display_unit)), step=p_step, format=p_format)
                snw1_raw = st.number_input(f"客戶預期最小淨重 ({display_unit}) - 量程 1", value=float(convert_from_g(0.02, display_unit)), step=p_step, format=p_format)
                snw2_raw = st.number_input(f"客戶預期最小淨重 ({display_unit}) - 量程 2", value=float(convert_from_g(0.2, display_unit)), step=p_step, format=p_format)
            with tab_std:
                std1_raw = st.number_input(f"實際量測標準差 STD1 ({display_unit}) - 量程 1", value=float(convert_from_g(0.000008, display_unit)), step=p_step, format=p_format)
                std2_raw = st.number_input(f"實際量測標準差 STD2 ({display_unit}) - 量程 2", value=float(convert_from_g(0.00008, display_unit)), step=p_step, format=p_format)
                rep_w_raw = st.number_input(f"重複性測試砝碼重量 ({display_unit}) (共用)", value=float(convert_from_g(0.1, display_unit)), step=p_step, format=p_format)
                rep_w_g = convert_to_g(rep_w_raw, display_unit)
            with tab_acc:
                acc_w_raw = st.number_input(f"準確度測試砝碼重量 ({display_unit}) (共用)", value=float(convert_from_g(200.0, display_unit)), step=p_step, format=p_format)
                acc_w_g = convert_to_g(acc_w_raw, display_unit)
            
            range_data.append({"d": convert_to_g(d1_raw, display_unit), "std": convert_to_g(std1_raw, display_unit), "snw": convert_to_g(snw1_raw, display_unit), "rep_w": rep_w_g, "acc_w": acc_w_g, "label": "量程 1"})
            range_data.append({"d": convert_to_g(d2_raw, display_unit), "std": convert_to_g(std2_raw, display_unit), "snw": convert_to_g(snw2_raw, display_unit), "rep_w": rep_w_g, "acc_w": acc_w_g, "label": "量程 2"})
        
        else:
            with tab_spec:
                d_raw = st.number_input(f"實際分度值 d ({display_unit})", value=float(convert_from_g(0.0001, display_unit)), step=p_step, format=p_format)
                snw_raw = st.number_input(f"客戶預期最小淨重 ({display_unit})", value=float(convert_from_g(0.02, display_unit)), step=p_step, format=p_format)
            with tab_std:
                std_raw = st.number_input(f"實際量測標準差 STD ({display_unit})", value=float(convert_from_g(0.00008, display_unit)), step=p_step, format=p_format)
                rep_w_raw = st.number_input(f"重複性測試砝碼重量 ({display_unit})", value=float(convert_from_g(0.1, display_unit)), step=p_step, format=p_format)
                rep_w_g = convert_to_g(rep_w_raw, display_unit)
            with tab_acc:
                acc_w_raw = st.number_input(f"準確度測試砝碼重量 ({display_unit})", value=float(convert_from_g(200.0, display_unit)), step=p_step, format=p_format)
                acc_w_g = convert_to_g(acc_w_raw, display_unit)
            
            range_data.append({"d": convert_to_g(d_raw, display_unit), "std": convert_to_g(std_raw, display_unit), "snw": convert_to_g(snw_raw, display_unit), "rep_w": rep_w_g, "acc_w": acc_w_g, "label": "量程"})

# --- 執行診斷按鈕 ---
if not is_manufacturing and st.button("🚀 執行全面合規性診斷", use_container_width=True):
    st.subheader("🏁 USP 〈41〉 設備適宜性診斷報告")
    for idx, data in enumerate(range_data):
        s_limit = 0.41 * data['d']
        calc_std = max(data['std'], s_limit)
        min_w_g = 2000 * calc_std
        sf = data['snw'] / min_w_g if min_w_g > 0 else 0
        
        with st.container(border=True):
            current_label = data.get('label', f"量程 {idx+1}")
            st.markdown(f"### 📍 {current_label} 診斷結果 (d = {auto_unit_format(data['d'])})")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info("#### 1. 重複性測試要求")
                is_rep_ok = 0.1 <= data['rep_w'] <= max_cap_g * 0.05
                st.markdown(f"* **關鍵限制**：若 $s < {auto_unit_format(s_limit)}$ ($0.41d$)，以該值計算。")
                if is_rep_ok: st.success(f"擬用砝碼：{auto_unit_format(data['rep_w'])} (✅)")
                else: st.error(f"擬用砝碼：{auto_unit_format(data['rep_w'])} (❌)")

            with col2:
                st.info("#### 2. 準確性測試要求")
                is_acc_ok = max_cap_g * 0.05 <= data['acc_w'] <= max_cap_g
                if is_acc_ok: st.success(f"擬用砝碼：{auto_unit_format(data['acc_w'])} (✅)")
                else: st.error(f"擬用砝碼：{auto_unit_format(data['acc_w'])} (❌)")

            st.markdown(f"#### 🛡️ 關鍵秤量能力判定")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("最小秤重 (理想)", auto_unit_format(2000 * s_limit))
            c2.metric("最小秤重 (實際)", auto_unit_format(min_w_g))
            c3.metric("預期最小淨重", auto_unit_format(data['snw']))
            c4.metric("安全係數 (SF)", f"{sf:.2f}")

            if data['snw'] >= min_w_g:
                st.success(f"✅ **{current_label} 判定：符合秤量需求**")
            else:
                st.error(f"❌ **{current_label} 判定：不符合需求**")

st.divider()
st.subheader("📑 專業評估指標說明")
st.info("""
* **理想最小秤重量**: 基於機台可讀數 $d$ 的理論最優值。
* **最小秤重量 (實際)**: 依據現場重複性測試 (STD) 算得之真實值。
* **安全係數 (SF)**: 建議 $\ge 2$。公式為：`客戶預期最小淨重 / 實際最小秤重量`。
""")
