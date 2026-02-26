import streamlit as st

# --- 工具函數：智慧格式化 (支援高精度且自動去零) ---
def smart_format(value):
    if value == 0:
        return "0"
    formatted = f"{value:.7g}"
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')
    return formatted

def format_weight_with_unit(g_value):
    if g_value < 1.0:
        return f"{smart_format(g_value * 1000)} mg"
    return f"{smart_format(g_value)} g"

# 設定網頁標題與風格
st.set_page_config(page_title="USP <41> & <1251> 專業合規工作站", layout="wide")
st.title("⚖️ USP 〈41〉 & 〈1251〉 天平測試合規工作站")
st.caption("依據標準：USP-NF 〈41〉 & 〈1251〉 (Official Feb 1, 2026)")

# --- 側邊欄：1. 檢查前作為 (Pre-check) ---
with st.sidebar:
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
    st.header("📋 2. 天平基本規格 (g)")
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間 (Multi-interval)", "DU多量程 (Multiple range)"])
    max_cap_g = st.number_input("天平最大秤重量 Max Capacity (g)", value=220.0, step=0.0000001, format="%.7f")
    is_manufacturing = st.checkbox("用於製造用途 (Manufacturing)?")

# --- 主頁面邏輯 ---
if is_manufacturing:
    st.error("🚨 **法規邊界提醒**：USP 〈41〉 的範圍不涵蓋「製造用」天平。請確認您的用途是否為分析流程。")
else:
    range_data = []

    # --- 數據輸入區 ---
    with st.expander("📥 測試參數輸入", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        
        if balance_type == "DU多量程 (Multiple range)":
            with col_a:
                d1 = st.number_input("實際分度值 d1 (g) - 量程 1", value=0.00001, step=0.0000001, format="%.7f")
                d2 = st.number_input("實際分度值 d2 (g) - 量程 2", value=0.0001, step=0.0000001, format="%.7f")
                snw1 = st.number_input("客戶預期最小淨重 (g) - 量程 1", value=0.02, step=0.0000001, format="%.7f")
                snw2 = st.number_input("客戶預期最小淨重 (g) - 量程 2", value=0.2, step=0.0000001, format="%.7f")
            with col_b:
                std1 = st.number_input("實際量測標準差 STD1 (g) - 量程 1", value=0.000008, step=0.0000001, format="%.7f")
                std2 = st.number_input("實際量測標準差 STD2 (g) - 量程 2", value=0.00008, step=0.0000001, format="%.7f")
                rep_w = st.number_input("重複性測試砝碼重量 (g) (共用)", value=0.1, step=0.0000001, format="%.7f")
            with col_c:
                acc_w = st.number_input("準確度測試砝碼重量 (g) (共用)", value=200.0, step=0.0000001, format="%.7f")
            
            # 分配兩組數據，但共用砝碼
            range_data.append({"d": d1, "std": std1, "snw": snw1, "rep_w": rep_w, "acc_w": acc_w})
            range_data.append({"d": d2, "std": std2, "snw": snw2, "rep_w": rep_w, "acc_w": acc_w})
        else:
            with col_a:
                d_g = st.number_input("實際分度值 d (g)", value=0.0001, step=0.0000001, format="%.7f")
                snw_g = st.number_input("客戶預期最小淨重 (g)", value=0.02, step=0.0000001, format="%.7f")
            with col_b:
                std_g = st.number_input("重複性實際量測標準差 STD (g)", value=0.00008, step=0.0000001, format="%.7f")
                rep_w_g = st.number_input("重複性測試砝碼重量 (g)", value=0.1, step=0.0000001, format="%.7f")
            with col_c:
                acc_w_g = st.number_input("準確度測試砝碼重量 (g)", value=200.0, step=0.0000001, format="%.7f")
            
            range_data.append({"d": d_g, "std": std_g, "snw": snw_g, "rep_w": rep_w_g, "acc_w": acc_w_g})

    # --- 執行診斷按鈕 ---
    if st.button("🚀 執行全面合規性診斷"):
        st.subheader("🏁 USP 〈41〉 設備適宜性診斷報告")
        
        for idx, data in enumerate(range_data):
            # --- 計算邏輯 ---
            s_threshold_g = 0.41 * data['d']
            rep_min_g, rep_max_g = 0.1000, max_cap_g * 0.05
            acc_min_g, acc_max_g = max_cap_g * 0.05, max_cap_g
            
            ideal_snw_g = 2000 * 0.41 * data['d']
            calculation_base = max(data['std'], 0.41 * data['d'])
            actual_min_weight_g = 2000 * calculation_base
            safety_factor = data['snw'] / actual_min_weight_g if actual_min_weight_g > 0 else 0

            st.markdown(f"### 📍 量程 {idx+1} 診斷結果 (d = {smart_format(data['d'])} g)")
            
            # --- 雙欄報告 ---
            diag_col1, diag_col2 = st.columns(2)

            with diag_col1:
                st.info("#### 1. 重複性測試要求 (Repeatability)")
                is_rep_ok = rep_min_g <= data['rep_w'] <= rep_max_g
                st.markdown(f"""
                **【法規規格要求】**
                * **砝碼區間**：`{format_weight_with_unit(rep_min_g)}` ~ `{format_weight_with_unit(rep_max_g)}`
                * **允收標準**：$2 \\times s / m_{{SNW}} \\le 0.10\\%$
                * **關鍵限制**：若 $s < {smart_format(s_threshold_g * 1000)} \\text{{ mg}}$ ($0.41d$)，計算時需以該值取代。
                """)
                status_rep_text = "✅ 符合規範" if is_rep_ok else "❌ 規格不符"
                # 修正處：改用標準 if 語法避免回傳 DeltaGenerator 物件
                if is_rep_ok:
                    st.success(f"**【實測對比判斷】**\n\n* 擬用砝碼：`{format_weight_with_unit(data['rep_w'])}` ({status_rep_text})")
                else:
                    st.error(f"**【實測對比判斷】**\n\n* 擬用砝碼：`{format_weight_with_unit(data['rep_w'])}` ({status_rep_text})")

            with diag_col2:
                st.info("#### 2. 準確度測試要求 (Accuracy)")
                is_acc_ok = acc_min_g <= data['acc_w'] <= acc_max_g
                mpe_limit_ratio = (0.05 / 100) / 3 
                mpe_absolute_g = data['acc_w'] * mpe_limit_ratio
                st.markdown(f"""
                **【法規規格要求】**
                * **砝碼區間**：`{format_weight_with_unit(acc_min_g)}` ~ `{format_weight_with_unit(acc_max_g)}`
                * **允收標準**：誤差 $\le 0.05\\%$
                * **砝碼限制**：$MPE$ 或 $U$ 需小於 **{mpe_limit_ratio*100:.4f}\\%** (即 0.05% 的 1/3)。
                """)
                status_acc_text = "✅ 符合規範" if is_acc_ok else "❌ 規格不符"
                # 修正處：改用標準 if 語法
                if is_acc_ok:
                    st.success(f"**【實測對比判斷】**\n\n* 擬用砝碼：`{format_weight_with_unit(data['acc_w'])}` ({status_acc_text})")
                else:
                    st.error(f"**【實測對比判斷】**\n\n* 擬用砝碼：`{format_weight_with_unit(data['acc_w'])}` ({status_acc_text})")
                st.caption(f"💡 砝碼證書擴展不確定度 $U$ 須 $\le {smart_format(mpe_absolute_g)} \\text{{ g}}$")

            # --- 關鍵能力判定 ---
            st.markdown(f"#### 🛡️ 關鍵秤量能力判定")
            res_c1, res_c2, res_c3, res_c4 = st.columns(4)
            with res_c1:
                st.metric("最小淨重量 (理想)", format_weight_with_unit(ideal_snw_g))
            with res_c2:
                st.metric("最小秤重量 (實際)", format_weight_with_unit(actual_min_weight_g))
            with res_c3:
                st.metric("客戶預期最小淨重量", format_weight_with_unit(data['snw']))
            with res_c4:
                st.metric("安全係數 (SF)", f"{safety_factor:.2f}")

            if data['snw'] >= actual_min_weight_g:
                st.success(f"✅ **量程 {idx+1} 判定：符合秤量需求** (預期 {smart_format(data['snw'])} g $\ge$ 實際 {smart_format(actual_min_weight_g)} g)")
            else:
                st.error(f"❌ **量程 {idx+1} 判定：不符合需求** (預期 {smart_format(data['snw'])} g < 實際 {smart_format(actual_min_weight_g)} g)")
            
            st.divider()

# --- 底部說明 ---
st.subheader("📑 專業評估指南")
with st.expander("名詞解釋"):
    st.markdown("""
    * **DU多量程**：在同一個天平上有不同的解析度區段。量程 2 的測試通常需要預載皮重。
    * **0.41d 規則**：USP <41> 規定當標準差 $s$ 過小時，必須以 $0.41d$ 作為計算基礎。
    """)
