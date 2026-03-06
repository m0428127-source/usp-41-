import streamlit as st

# --- 工具函數 ---
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

# 設定網頁標題與風格
st.set_page_config(page_title="USP <41> & <1251> 專業合規工作站", layout="wide")
st.title("⚖️ USP 〈41〉 & 〈1251〉 天平測試合規工作站")
st.caption("依據標準：USP-NF 〈41〉 & 〈1251〉 (Official Feb 1, 2026)")

# --- 側邊欄：1. 檢查前作為 (Pre-check) ---
with st.sidebar:
    st.header("⚙️ 顯示設定")
    display_unit = st.selectbox("偏好顯示單位", ["g", "mg", "kg"], index=0)
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

# --- 主頁面邏輯 ---
range_data = []
p_step = 0.0000001
p_format = "%.7g"

# --- 數據輸入區 ---
with st.expander(f"📥 測試參數輸入 ({display_unit})", expanded=True):
    tab_base, tab_process, tab_std, tab_acc = st.tabs([
        "📋 天平基本規格", "🎯 Process requirement", "📊 重複性測試", "🎯 準確性測試"
    ])
    
    with tab_base:
        balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間 (Multi-interval)", "DU_多量程 (Multiple range)"])
        raw_max_cap = st.number_input(f"天平最大秤重量 Max Capacity ({display_unit})", value=float(convert_from_g(220.0, display_unit)), step=p_step, format=p_format)
        max_cap_g = convert_to_g(raw_max_cap, display_unit)
        is_manufacturing = st.checkbox("用於製造用途 (Manufacturing)?")

        d_base_options = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001]
        d_converted_options = [float(smart_format(convert_from_g(x, display_unit))) for x in d_base_options]

        if balance_type == "DU_多量程 (Multiple range)":
            d1_slider = st.select_slider(f"選擇天秤可讀數值 d1 ({display_unit})", options=d_converted_options, value=d_converted_options[5])
            d1_raw = st.number_input(f"天秤可讀數 d1 ({display_unit}) - 量程 1", value=d1_slider, step=p_step, format=p_format)
            d2_slider = st.select_slider(f"選擇天秤可讀數值 d2 ({display_unit})", options=d_converted_options, value=d_converted_options[4])
            d2_raw = st.number_input(f"天秤可讀數 d2 ({display_unit}) - 量程 2", value=d2_slider, step=p_step, format=p_format)
            d1_g, d2_g = convert_to_g(d1_raw, display_unit), convert_to_g(d2_raw, display_unit)
        else:
            d_slider = st.select_slider(f"選擇天秤可讀數值 d ({display_unit})", options=d_converted_options, value=d_converted_options[4])
            d_raw = st.number_input(f"天秤可讀數 d ({display_unit})", value=d_slider, step=p_step, format=p_format)
            d_g = convert_to_g(d_raw, display_unit)

    if not is_manufacturing:
        with tab_process:
            if balance_type == "DU_多量程 (Multiple range)":
                snw1_raw = st.number_input(f"您預期最小淨重 ({display_unit}) - 量程 1", value=float(convert_from_g(0.02, display_unit)), step=p_step, format=p_format)
                snw2_raw = st.number_input(f"您預期最小淨重 ({display_unit}) - 量程 2", value=float(convert_from_g(0.2, display_unit)), step=p_step, format=p_format)
                snw1_g, snw2_g = convert_to_g(snw1_raw, display_unit), convert_to_g(snw2_raw, display_unit)
            else:
                snw_raw = st.number_input(f"您預期最小淨重 ({display_unit})", value=float(convert_from_g(0.02, display_unit)), step=p_step, format=p_format)
                snw_g = convert_to_g(snw_raw, display_unit)

        with tab_std:
            if balance_type == "DU_多量程 (Multiple range)":
                std1_raw = st.number_input(f"實際量測標準差 STD1 ({display_unit}) - 量程 1", value=float(convert_from_g(0.000008, display_unit)), step=p_step, format=p_format)
                std2_raw = st.number_input(f"實際量測標準差 STD2 ({display_unit}) - 量程 2", value=float(convert_from_g(0.00008, display_unit)), step=p_step, format=p_format)
                std1_g, std2_g = convert_to_g(std1_raw, display_unit), convert_to_g(std2_raw, display_unit)
            else:
                std_raw = st.number_input(f"重複性實際量測標準差 STD ({display_unit})", value=float(convert_from_g(0.00008, display_unit)), step=p_step, format=p_format)
                std_g = convert_to_g(std_raw, display_unit)
            rep_w_raw = st.number_input(f"重複性測試砝碼重量 ({display_unit})", value=float(convert_from_g(0.1, display_unit)), step=p_step, format=p_format)
            rep_w_g = convert_to_g(rep_w_raw, display_unit)

        with tab_acc:
            acc_w_raw = st.number_input(f"準確度測試砝碼重量 ({display_unit})", value=float(convert_from_g(200.0, display_unit)), step=p_step, format=p_format)
            acc_w_g = convert_to_g(acc_w_raw, display_unit)

        if balance_type == "DU_多量程 (Multiple range)":
            range_data.append({"d": d1_g, "std": std1_g, "snw": snw1_g, "rep_w": rep_w_g, "acc_w": acc_w_g, "label": "量程 1"})
            range_data.append({"d": d2_g, "std": std2_g, "snw": snw2_g, "rep_w": rep_w_g, "acc_w": acc_w_g, "label": "量程 2"})
        else:
            range_data.append({"d": d_g, "std": std_g, "snw": snw_g, "rep_w": rep_w_g, "acc_w": acc_w_g, "label": "量程"})

# --- 執行診斷按鈕 ---
if not is_manufacturing and st.button("🚀 執行全面合規性診斷", use_container_width=True):
    st.subheader("🏁 USP 〈41〉 設備適宜性診斷報告")
    for idx, data in enumerate(range_data):
        s_threshold_g = 0.41 * data['d']
        rep_min_g, rep_max_g = 0.100, max_cap_g * 0.05
        acc_min_g, acc_max_g = max_cap_g * 0.05, max_cap_g
        
        # 核心邏輯修正：考慮 1/3 * 0.05%
        mpe_limit_ratio = (0.05 / 100) / 3 
        mpe_absolute_g = data['acc_w'] * mpe_limit_ratio
        
        actual_min_weight_g = 2000 * max(data['std'], s_threshold_g)
        safety_factor = data['snw'] / actual_min_weight_g if actual_min_weight_g > 0 else 0

        with st.container(border=True):
            st.markdown(f"### 📍 {data['label']} 診斷結果 (d = {auto_unit_format(data['d'])})")
            diag_col1, diag_col2 = st.columns(2)
            with diag_col1:
                st.info("#### 1. 重複性測試要求 (Repeatability)")
                is_rep_ok = rep_min_g <= data['rep_w'] <= rep_max_g
                st.markdown(f"""
                **【法規規格要求】**
                * **砝碼區間**：`{auto_unit_format(rep_min_g)}` ~ `{auto_unit_format(rep_max_g)}`
                * **允收標準**：$2 \\times s / m_{{SNW}} \\le 0.10\\%$
                * **關鍵限制**：若 $s < {auto_unit_format(s_threshold_g)}$ ($0.41d$)，計算時需以該值取代。
                """)
                if is_rep_ok: st.success(f"**【實測對比判斷】**\n\n* 擬用砝碼：`{auto_unit_format(data['rep_w'])}` (✅ 符合規範)")
                else: st.error(f"**【實測對比判斷】**\n\n* 擬用砝碼：`{auto_unit_format(data['rep_w'])}` (❌ 規格不符)")

            with diag_col2:
                st.info("#### 2. 準確度測試要求 (Accuracy)")
                is_acc_ok = acc_min_g <= data['acc_w'] <= acc_max_g
                st.markdown(f"""
                **【法規規格要求】**
                * **砝碼區間**：`{auto_unit_format(acc_min_g)}` ~ `{auto_unit_format(acc_max_g)}`
                * **允收標準**：誤差 $\le 0.05\\%$
                * **砝碼限制**：$MPE$ 或 $U$ 需小於 **{mpe_limit_ratio*100:.4f}\\%** (即 0.05% 的 1/3)。
                """)
                if is_acc_ok: st.success(f"**【實測對比判斷】**\n\n* 擬用砝碼：`{auto_unit_format(data['acc_w'])}` (✅ 符合規範)")
                else: st.error(f"**【實測對比判斷】**\n\n* 擬用砝碼：`{auto_unit_format(data['acc_w'])}` (❌ 規格不符)")
                st.caption(f"💡 砝碼重量為 {auto_unit_format(data['acc_w'])}，證書擴展不確定度 $U$ 須 $\le {auto_unit_format(mpe_absolute_g)}$")

            st.markdown(f"#### 🛡️ 關鍵秤量能力判定")
            res_c1, res_c2, res_c3, res_c4 = st.columns(4)
            res_c1.metric("最小淨重量 (理想 0.41d)", auto_unit_format(2000 * s_threshold_g))
            res_c2.metric("最小秤重量 (實際 MinW)", auto_unit_format(actual_min_weight_g))
            res_c3.metric("您預期最小淨重量", auto_unit_format(data['snw']))
            res_c4.metric("安全係數 (SF)", f"{safety_factor:.2f}")

            if data['snw'] >= actual_min_weight_g:
                st.success(f"✅ **{data['label']} 判定：符合秤量需求** (預期 {auto_unit_format(data['snw'])} $\ge$ 實際 {auto_unit_format(actual_min_weight_g)})")
            else:
                st.error(f"❌ **{data['label']} 判定：不符合需求** (預期 {auto_unit_format(data['snw'])} < 實際 {auto_unit_format(actual_min_weight_g)})")
        st.divider()

st.subheader("📑 專業評估指標說明")
st.info("""
* **理想最小秤重量 (Minimum weight SNW)**: 基於機台可讀數 $d$ 的理論最優值，代表天平在無環境干擾下的極限。
* **最小秤重量 (Minimum weight MinW)**: 依據現場重複性測試 (STD) 算得之真實值。若實測 STD 優於 $0.41d$，則法規強制以 $0.41d$ 計算。
* **判定基準**: 當「預期最小淨重」 $\ge$ 「最小秤重量」時，該量程判定為「符合秤量需求」。
* **安全係數 (Safety Factor)**: 反映用戶秤量目標相對於法規底線的裕度。USP 〈1251〉 建議安全係數應 $\ge 2$ 以確保製程穩定。
""")
