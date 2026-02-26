import streamlit as st

# --- 工具函數：智慧格式化 (支援高精度且自動去零) ---
def smart_format(value):
    if value == 0:
        return "0"
    # 使用 %.7g 格式化，這會保留最多 7 位有效數字並自動去掉末尾的零，避免科學記號
    formatted = f"{value:.7g}"
    return formatted

# --- 新增：自動單位轉換顯示函數 (優化診斷報告閱讀體驗) ---
def auto_unit_format(g_value):
    """
    依據數值大小自動切換顯示單位：
    < 0.001g (1mg) -> 顯示為 mg
    >= 1000g -> 顯示為 kg
    其餘 -> 顯示為 g
    """
    abs_val = abs(g_value)
    if abs_val == 0:
        return "0 g"
    
    if abs_val < 0.001:
        return f"{smart_format(g_value * 1000)} mg"
    elif abs_val >= 1000:
        return f"{smart_format(g_value / 1000)} kg"
    else:
        return f"{smart_format(g_value)} g"

# --- 單位換算工具 (供輸入端使用) ---
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

# --- 側邊欄：1. 檢查前作為 (Pre-check) ---
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("偏好輸入單位", ["g", "mg", "kg"], index=0)
    
    st.divider()
    st.header("🔍 1. 檢查前作為 (Pre-check)")
    st.markdown("依據 USP 〈1251〉 規範，請先確認環境與設備狀態：")
    
    env_surface = st.checkbox("水平且非磁性的穩固表面 (Level & Nonmagnetic)")
    env_location = st.checkbox("遠離氣流、門窗、震動源與熱源")
    env_static = st.checkbox("濕度控制適當或已具備除靜電措施")
    balance_status = st.checkbox("天平已預熱並完成水平調整")
    
    if not (env_surface and env_location and env_static and balance_status):
        st.warning("⚠️ 依循 USP<1251> 環境檢核未完成，量測不穩定風險提高。")
    else:
        st.success("✅ 依循 USP<1251> 環境檢查完成，準備執行測試。")

    st.divider()
    st.header(f"📋 2. 天平基本規格")
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間 (Multi-interval)", "DU多量程 (Multiple range)"])
    
    # 定義通用的極小步進值與格式，支援高精度且自動去零
    p_step = 0.0000001
    p_format = "%.7g"
    
    raw_max_cap = st.number_input(
        f"天平最大秤重量 Max Capacity ({display_unit})", 
        value=float(convert_from_g(220.0, display_unit)), 
        step=p_step,
        format=p_format
    )
    max_cap_g = convert_to_g(raw_max_cap, display_unit)
    is_manufacturing = st.checkbox("用於製造用途 (Manufacturing)?")

# --- 主頁面邏輯 ---
if is_manufacturing:
    st.error("🚨 **法規邊界提醒**：USP 〈41〉 的範圍不涵蓋「製造用」天平。請確認您的用途是否為分析流程。")
else:
    range_data = []

    # --- 數據輸入區 ---
    with st.expander(f"📥 測試參數輸入 ({display_unit})", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        
        if balance_type == "DU多量程 (Multiple range)":
            with col_a:
                d1_raw = st.number_input(f"實際分度值 d1 ({display_unit}) - 量程 1", value=float(convert_from_g(0.00001, display_unit)), step=p_step, format=p_format)
                d2_raw = st.number_input(f"實際分度值 d2 ({display_unit}) - 量程 2", value=float(convert_from_g(0.0001, display_unit)), step=p_step, format=p_format)
                snw1_raw = st.number_input(f"客戶預期最小淨重 ({display_unit}) - 量程 1", value=float(convert_from_g(0.02, display_unit)), step=p_step, format=p_format)
                snw2_raw = st.number_input(f"客戶預期最小淨重 ({display_unit}) - 量程 2", value=float(convert_from_g(0.2, display_unit)), step=p_step, format=p_format)
            with col_b:
                std1_raw = st.number_input(f"實際量測標準差 STD1 ({display_unit}) - 量程 1", value=float(convert_from_g(0.000008, display_unit)), step=p_step, format=p_format)
                std2_raw = st.number_input(f"實際量測標準差 STD2 ({display_unit}) - 量程 2", value=float(convert_from_g(0.00008, display_unit)), step=p_step, format=p_format)
                rep_w_raw = st.number_input(f"重複性測試砝碼重量 ({display_unit}) (共用)", value=float(convert_from_g(0.1, display_unit)), step=p_step, format=p_format)
                rep_w_g = convert_to_g(rep_w_raw, display_unit)
            with col_c:
                acc_w_raw = st.number_input(f"準確度測試砝碼重量 ({display_unit}) (共用)", value=float(convert_from_g(200.0, display_unit)), step=p_step, format=p_format)
                acc_w_g = convert_to_g(acc_w_raw, display_unit)
            
            range_data.append({"d": convert_to_g(d1_raw, display_unit), "std": convert_to_g(std1_raw, display_unit), "snw": convert_to_g(snw1_raw, display_unit), "rep_w": rep_w_g, "acc_w": acc_w_g})
            range_data.append({"d": convert_to_g(d2_raw, display_unit), "std": convert_to_g(std2_raw, display_unit), "snw": convert_to_g(snw2_raw, display_unit), "rep_w": rep_w_g, "acc_w": acc_w_g})
        
        else:
            with col_a:
                d_raw = st.number_input(f"實際分度值 d ({display_unit})", value=float(convert_from_g(0.0001, display_unit)), step=p_step, format=p_format)
                snw_raw = st.number_input(f"客戶預期最小淨重 ({display_unit})", value=float(convert_from_g(0.02, display_unit)), step=p_step, format=p_format)
            with col_b:
                std_raw = st.number_input(f"重複性實際量測標準差 STD ({display_unit})", value=float(convert_from_g(0.00008, display_unit)), step=p_step, format=p_format)
                rep_w_raw = st.number_input(f"重複性測試砝碼重量 ({display_unit})", value=float(convert_from_g(0.1, display_unit)), step=p_step, format=p_format)
                rep_w_g = convert_to_g(rep_w_raw, display_unit)
            with col_c:
                acc_w_raw = st.number_input(f"準確度測試砝碼重量 ({display_unit})", value=float(convert_from_g(200.0, display_unit)), step=p_step, format=p_format)
                acc_w_g = convert_to_g(acc_w_raw, display_unit)
            
            range_data.append({"d": convert_to_g(d_raw, display_unit), "std": convert_to_g(std_raw, display_unit), "snw": convert_to_g(snw_raw, display_unit), "rep_w": rep_w_g, "acc_w": acc_w_g})

    # --- 執行診斷按鈕 ---
    if st.button("🚀 執行全面合規性診斷"):
        st.subheader("🏁 USP 〈41〉 設備適宜性診斷報告")
        
        for idx, data in enumerate(range_data):
            # 核心邏輯計算
            s_threshold_g = 0.41 * data['d']
            ideal_snw_g = 2000 * 0.41 * data['d']
            calculation_base = max(data['std'], 0.41 * data['d'])
            actual_min_weight_g = 2000 * calculation_base
            safety_factor = data['snw'] / actual_min_weight_g if actual_min_weight_g > 0 else 0

            # 報告標題：使用智慧單位轉換
            st.markdown(f"### 📍 量程 {idx+1} 診斷結果 (d = {auto_unit_format(data['d'])})")
            
            diag_col1, diag_col2 = st.columns(2)

            with diag_col1:
                st.info("#### 1. 重複性測試要求 (Repeatability)")
                st.markdown(f"""
                * **關鍵限制**：若 $s < {auto_unit_format(s_threshold_g)}$ ($0.41d$)，以該值計算。
                * **擬用砝碼**：`{auto_unit_format(data['rep_w'])}`
                """)

            with diag_col2:
                st.info("#### 2. 準確度測試要求 (Accuracy)")
                mpe_absolute_g = data['acc_w'] * ((0.05 / 100) / 3)
                st.markdown(f"""
                * **擬用砝碼**：`{auto_unit_format(data['acc_w'])}`
                * **砝碼證書 U 須** $\le {auto_unit_format(mpe_absolute_g)}$
                """)

            st.markdown(f"#### 🛡️ 關鍵秤量能力判定")
            res_c1, res_c2, res_c3, res_c4 = st.columns(4)
            # 數值顯示端全部改用 auto_unit_format 以獲得最佳閱讀體驗
            res_c1.metric("最小淨重量 (理想)", auto_unit_format(ideal_snw_g))
            res_c2.metric("最小秤重量 (實際)", auto_unit_format(actual_min_weight_g))
            res_c3.metric("客戶預期最小淨重量", auto_unit_format(data['snw']))
            res_c4.metric("安全係數 (SF)", f"{safety_factor:.2f}")

            if data['snw'] >= actual_min_weight_g:
                st.success(f"✅ **符合需求** ({auto_unit_format(data['snw'])} $\ge$ {auto_unit_format(actual_min_weight_g)})")
            else:
                st.error(f"❌ **不符合需求** ({auto_unit_format(data['snw'])} < {auto_unit_format(actual_min_weight_g)})")
            st.divider()

st.subheader("📑 專業評估指標說明")
st.info("""
* **單位說明**: 報告中數值會自動依據大小切換單位 (mg/g/kg) 以利閱讀。
* **最小秤重量 (Actual MinW)**: 依據現場 STD 算得。若實測 STD 優於 $0.41d$，法規強制以 $0.41d$ 計算。
* **判定基準**: 當「客戶預期最小淨重」 $\ge$ 「實際最小秤重量」時，判定為符合需求。
""")
