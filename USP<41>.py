import streamlit as st

# --- 工具函數 ---
def smart_format(value):
    if value == 0: return "0"
    formatted = f"{value:.7g}"
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')
    return formatted

def format_weight_with_unit(g_value, display_unit):
    """根據當前單位智慧顯示"""
    val = convert_from_g(g_value, display_unit)
    return f"{smart_format(val)} {display_unit}"

def convert_to_g(value, unit):
    if unit == "mg": return value / 1000
    if unit == "kg": return value * 1000
    return value

def convert_from_g(value, unit):
    if unit == "mg": return value * 1000
    if unit == "kg": return value / 1000
    return value

# 設定網頁
st.set_page_config(page_title="USP <41> & <1251> 專業合規工作站", layout="wide")
st.title("⚖️ USP 〈41〉 & 〈1251〉 天平測試合規工作站")

# --- 側邊欄 ---
with st.sidebar:
    st.header("⚙️ 全域設定")
    display_unit = st.selectbox("偏好顯示單位", ["g", "mg", "kg"], index=0)
    
    st.divider()
    st.header("📋 天平基本規格")
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間 (Multi-interval)", "DU多量程 (Multiple range)"])
    raw_max_cap = st.number_input(f"最大秤量 ({display_unit})", value=convert_from_g(220.0, display_unit), step=0.0000001, format="%.7f")
    max_cap_g = convert_to_g(raw_max_cap, display_unit)
    is_manufacturing = st.checkbox("用於製造用途 (Manufacturing)?")

# --- 主頁面邏輯 ---
if is_manufacturing:
    st.error("🚨 **法規提醒**：USP 〈41〉 不涵蓋製造用天平。")
else:
    range_data = []
    # 這裡保留您的 expander 設計
    with st.expander("📥 測試參數輸入 (即時合規檢查)", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        
        if balance_type == "DU多量程 (Multiple range)":
            with col_a:
                d1 = st.number_input(f"分度值 d1 ({display_unit})", value=convert_from_g(0.00001, display_unit), format="%.7f")
                d2 = st.number_input(f"分度值 d2 ({display_unit})", value=convert_from_g(0.0001, display_unit), format="%.7f")
                snw1 = st.number_input(f"預期淨重 1 ({display_unit})", value=convert_from_g(0.02, display_unit), format="%.7f")
                snw2 = st.number_input(f"預期淨重 2 ({display_unit})", value=convert_from_g(0.2, display_unit), format="%.7f")
            with col_b:
                std1 = st.number_input(f"標準差 STD1 ({display_unit})", value=convert_from_g(0.000008, display_unit), format="%.7f")
                std2 = st.number_input(f"標準差 STD2 ({display_unit})", value=convert_from_g(0.00008, display_unit), format="%.7f")
                rep_w_raw = st.number_input(f"重複性砝碼 ({display_unit})", value=convert_from_g(0.1, display_unit), format="%.7f")
                # 即時檢查
                rep_w_g = convert_to_g(rep_w_raw, display_unit)
                if not (0.1 <= rep_w_g <= max_cap_g * 0.05):
                    st.error(f"⚠️ 砝碼不符 USP! 建議: {smart_format(convert_from_g(0.1, display_unit))}~{smart_format(convert_from_g(max_cap_g*0.05, display_unit))}")
                else:
                    st.caption("✅ 區間合規")
            with col_c:
                acc_w_raw = st.number_input(f"準確度砝碼 ({display_unit})", value=convert_from_g(200.0, display_unit), format="%.7f")
                # 即時檢查
                acc_w_g = convert_to_g(acc_w_raw, display_unit)
                if not (max_cap_g * 0.05 <= acc_w_g <= max_cap_g):
                    st.error(f"⚠️ 砝碼不符 USP! 建議: {smart_format(convert_from_g(max_cap_g*0.05, display_unit))}~{smart_format(convert_from_g(max_cap_g, display_unit))}")
                else:
                    st.caption("✅ 區間合規")
            
            range_data.append({"d": convert_to_g(d1, display_unit), "std": convert_to_g(std1, display_unit), "snw": convert_to_g(snw1, display_unit), "rep_w": rep_w_g, "acc_w": acc_w_g})
            range_data.append({"d": convert_to_g(d2, display_unit), "std": convert_to_g(std2, display_unit), "snw": convert_to_g(snw2, display_unit), "rep_w": rep_w_g, "acc_w": acc_w_g})

        else:
            # 單一量程邏輯
            with col_a:
                d_val = st.number_input(f"分度值 d ({display_unit})", value=convert_from_g(0.0001, display_unit), format="%.7f")
                snw_val = st.number_input(f"預期淨重 ({display_unit})", value=convert_from_g(0.02, display_unit), format="%.7f")
            with col_b:
                std_val = st.number_input(f"標準差 STD ({display_unit})", value=convert_from_g(0.00008, display_unit), format="%.7f")
                rep_w_raw = st.number_input(f"重複性砝碼 ({display_unit})", value=convert_from_g(0.1, display_unit), format="%.7f")
                rep_w_g = convert_to_g(rep_w_raw, display_unit)
                if not (0.1 <= rep_w_g <= max_cap_g * 0.05):
                    st.error("⚠️ 砝碼超出 5% Max 建議區間")
            with col_c:
                acc_w_raw = st.number_input(f"準確度砝碼 ({display_unit})", value=convert_from_g(200.0, display_unit), format="%.7f")
                acc_w_g = convert_to_g(acc_w_raw, display_unit)
                if not (max_cap_g * 0.05 <= acc_w_g <= max_cap_g):
                    st.error("⚠️ 砝碼超出 5%~100% Max 建議區間")
            
            range_data.append({"d": convert_to_g(d_val, display_unit), "std": convert_to_g(std_val, display_unit), "snw": convert_to_g(snw_val, display_unit), "rep_w": rep_w_g, "acc_w": acc_w_g})

    # --- 執行診斷按鈕 ---
    if st.button("🚀 執行全面合規性診斷"):
        st.subheader("🏁 USP 〈41〉 設備適宜性診斷報告")
        for idx, data in enumerate(range_data):
            # 原始計算邏輯
            s_threshold_g = 0.41 * data['d']
            calc_std_g = max(data['std'], s_threshold_g)
            actual_min_weight_g = 2000 * calc_std_g
            ideal_snw_g = 2000 * 0.41 * data['d']
            safety_factor = data['snw'] / actual_min_weight_g if actual_min_weight_g > 0 else 0

            st.markdown(f"### 📍 量程 {idx+1} 診斷結果 (d = {format_weight_with_unit(data['d'], display_unit)})")
            
            # 1. 雙欄報告 (保留您最愛的設計)
            diag_col1, diag_col2 = st.columns(2)
            with diag_col1:
                st.info("#### 1. 重複性測試要求")
                is_rep_ok = 0.1 <= data['rep_w'] <= max_cap_g * 0.05
                st.markdown(f"* 允收標準：$2 \\times s / m_{{SNW}} \\le 0.10\\%$\n* 關鍵限制：$s$ 需 $\ge {smart_format(convert_from_g(s_threshold_g, display_unit))} {display_unit}$")
                if is_rep_ok: st.success(f"✅ 擬用砝碼：{format_weight_with_unit(data['rep_w'], display_unit)} (符合規範)")
                else: st.error(f"❌ 擬用砝碼：{format_weight_with_unit(data['rep_w'], display_unit)} (規格不符)")

            with diag_col2:
                st.info("#### 2. 準確度測試要求")
                is_acc_ok = max_cap_g * 0.05 <= data['acc_w'] <= max_cap_g
                st.markdown(f"* 允收標準：誤差 $\le 0.05\\%$\n* 砝碼限制：$U$ 需 $\le {smart_format(data['acc_w'] * (0.05/100)/3)} g$")
                if is_acc_ok: st.success(f"✅ 擬用砝碼：{format_weight_with_unit(data['acc_w'], display_unit)} (符合規範)")
                else: st.error(f"❌ 擬用砝碼：{format_weight_with_unit(data['acc_w'], display_unit)} (規格不符)")

            # 2. 關鍵判定 (您的四欄位設計)
            st.markdown("#### 🛡️ 關鍵秤量能力判定")
            res_c1, res_c2, res_c3, res_c4 = st.columns(4)
            res_c1.metric("最小淨重 (理想)", format_weight_with_unit(ideal_snw_g, display_unit))
            res_c2.metric("最小秤重 (實際)", format_weight_with_unit(actual_min_weight_g, display_unit))
            res_c3.metric("客戶預期淨重", format_weight_with_unit(data['snw'], display_unit))
            res_c4.metric("安全係數 (SF)", f"{safety_factor:.2f}")

            if data['snw'] >= actual_min_weight_g:
                st.success(f"✅ **最終判定：符合秤量需求**")
            else:
                st.error(f"❌ **最終判定：不符合需求**")
            st.divider()
