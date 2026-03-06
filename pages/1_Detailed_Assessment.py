import streamlit as st

# --- 1. 工具函數 (維持原邏輯) ---
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
st.set_page_config(page_title="USP <41> & <1251> 專業工作站", layout="centered") # 手機建議 centered
st.title("⚖️ USP 〈41〉 & 〈1251〉 天平測試合規工作站")
st.caption("依據標準：USP-NF 〈41〉 & 〈1251〉 (Official Feb 1, 2026)")

# --- 3. 側邊欄：顯示設定 ---
with st.sidebar:
    st.header("⚙️ 偏好設定")
    display_unit = st.selectbox("偏好顯示單位", ["g", "mg", "kg"], index=0)
    st.divider()
    st.markdown("### 📘 指引模式")
    st.info("本工具將引導您依序完成設備規格、流程需求及測試數據輸入，最後產出合規診斷報告。")

# --- 4. 流程第一步：📋 基本規格與環境檢核 ---
st.markdown("### 📋 1️⃣ 基本規格與環境檢核")
with st.container(border=True):
    col_a, col_b = st.columns([1.5, 1])
    with col_a:
        balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間 (Multi-interval)", "DU_多量程 (Multiple range)"])
    with col_b:
        is_manufacturing = st.toggle("用於製造用途 (Manufacturing)?", value=False)
    
    # 規格參數
    p_step = 0.0000001
    p_format = "%.7g"
    raw_max_cap = st.number_input(f"天平最大秤重量 Max Capacity ({display_unit})", value=float(convert_from_g(220.0, display_unit)), step=p_step, format=p_format)
    max_cap_g = convert_to_g(raw_max_cap, display_unit)

    # 可讀數選擇 (手機友善：Select Slider)
    d_base_options = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001]
    d_converted_options = [float(smart_format(convert_from_g(x, display_unit))) for x in d_base_options]
    
    if balance_type == "DU_多量程 (Multiple range)":
        d1_raw = st.select_slider(f"選擇天秤可讀數 d1 ({display_unit})", options=d_converted_options, value=d_converted_options[5])
        d2_raw = st.select_slider(f"選擇天秤可讀數 d2 ({display_unit})", options=d_converted_options, value=d_converted_options[4])
        d1_g, d2_g = convert_to_g(d1_raw, display_unit), convert_to_g(d2_raw, display_unit)
    else:
        d_raw = st.select_slider(f"選擇天秤可讀數 d ({display_unit})", options=d_converted_options, value=d_converted_options[4])
        d_g = convert_to_g(d_raw, display_unit)

    # 環境檢核清單 (折疊以縮短手機長度)
    with st.expander("🔍 點擊展開：USP 〈1251〉 環境與設備預檢"):
        env_surface = st.checkbox("水平且非磁性的穩固表面 (Level & Nonmagnetic)")
        env_location = st.checkbox("遠離氣流、門窗、震動源與熱源")
        env_static = st.checkbox("濕度控制適當或已具備除靜電措施")
        balance_status = st.checkbox("天平已預熱並完成水平調整")
        if not (env_surface and env_location and env_static and balance_status):
            st.warning("⚠️ 環境檢核未完成，量測不穩定風險提高。")

# --- 5. 流程第二步：🎯 秤量目標與流程要求 ---
st.markdown("### 🎯 2️⃣ 秤量目標與流程要求 (Process Requirement)")
with st.container(border=True):
    if balance_type == "DU_多量程 (Multiple range)":
        snw1_raw = st.number_input(f"預期最小淨重 SNW ({display_unit}) - 量程 1", value=float(convert_from_g(0.02, display_unit)), format=p_format)
        snw2_raw = st.number_input(f"預期最小淨重 SNW ({display_unit}) - 量程 2", value=float(convert_from_g(0.2, display_unit)), format=p_format)
        snw1_g, snw2_g = convert_to_g(snw1_raw, display_unit), convert_to_g(snw2_raw, display_unit)
    else:
        snw_raw = st.number_input(f"您預期最小淨重 SNW ({display_unit})", value=float(convert_from_g(0.02, display_unit)), format=p_format)
        snw_g = convert_to_g(snw_raw, display_unit)

# --- 6. 流程第三步：📊 現場測試數據填入 ---
st.markdown("### 📊 3️⃣ 現場測試數據 (Repeatability & Accuracy)")
with st.container(border=True):
    if balance_type == "DU_多量程 (Multiple range)":
        std1_raw = st.number_input(f"實測標準差 STD1 ({display_unit}) - 量程 1", value=float(convert_from_g(0.000008, display_unit)), format=p_format)
        std2_raw = st.number_input(f"實測標準差 STD2 ({display_unit}) - 量程 2", value=float(convert_from_g(0.00008, display_unit)), format=p_format)
        std1_g, std2_g = convert_to_g(std1_raw, display_unit), convert_to_g(std2_raw, display_unit)
    else:
        std_raw = st.number_input(f"實測重複性標準差 STD ({display_unit})", value=float(convert_from_g(0.00008, display_unit)), format=p_format)
        std_g = convert_to_g(std_raw, display_unit)
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        rep_w_raw = st.number_input(f"重複性測試砝碼重量 ({display_unit})", value=float(convert_from_g(0.1, display_unit)), format=p_format)
    with col_w2:
        acc_w_raw = st.number_input(f"準確度測試砝碼重量 ({display_unit})", value=float(convert_from_g(200.0, display_unit)), format=p_format)
    
    rep_w_g = convert_to_g(rep_w_raw, display_unit)
    acc_w_g = convert_to_g(acc_w_raw, display_unit)

# --- 整合數據 ---
range_data = []
if balance_type == "DU_多量程 (Multiple range)":
    range_data.append({"d": d1_g, "std": std1_g, "snw": snw1_g, "rep_w": rep_w_g, "acc_w": acc_w_g, "label": "量程 1"})
    range_data.append({"d": d2_g, "std": std2_g, "snw": snw2_g, "rep_w": rep_w_g, "acc_w": acc_w_g, "label": "量程 2"})
else:
    range_data.append({"d": d_g, "std": std_g, "snw": snw_g, "rep_w": rep_w_g, "acc_w": acc_w_g, "label": "單一量程"})

# --- 7. 診斷與結果報告 ---
st.divider()
if not is_manufacturing:
    if st.button("🚀 產出合規性診斷報告", use_container_width=True, type="primary"):
        st.subheader("🏁 設備適宜性診斷結果")
        
        for idx, data in enumerate(range_data):
            s_threshold_g = 0.41 * data['d']
            rep_min_g, rep_max_g = 0.100, max_cap_g * 0.05
            acc_min_g, acc_max_g = max_cap_g * 0.05, max_cap_g
            mpe_limit_ratio = (0.05 / 100) / 3 
            mpe_absolute_g = data['acc_w'] * mpe_limit_ratio
            actual_min_weight_g = 2000 * max(data['std'], s_threshold_g)
            safety_factor = data['snw'] / actual_min_weight_g if actual_min_weight_g > 0 else 0

            with st.container(border=True):
                st.markdown(f"#### 📍 {data['label']} 診斷 (d = {auto_unit_format(data['d'])})")
                
                # 合規狀態摘要 (手機核心重點)
                if data['snw'] >= actual_min_weight_g:
                    st.success(f"**判定：符合需求** (SNW {auto_unit_format(data['snw'])} $\ge$ MinW {auto_unit_format(actual_min_weight_g)})")
                else:
                    st.error(f"**判定：不合規** (SNW {auto_unit_format(data['snw'])} < MinW {auto_unit_format(actual_min_weight_g)})")
                
                # 關鍵數據 (使用 Metric)
                m1, m2, m3 = st.columns(3)
                m1.metric("實際 MinW", auto_unit_format(actual_min_weight_g))
                m2.metric("預期 SNW", auto_unit_format(data['snw']))
                m3.metric("安全係數 SF", f"{safety_factor:.2f}")

                # 詳細檢查 (摺疊起來，想看的人再看)
                with st.expander("📋 查看詳細檢查項 (Repeatability & Accuracy)"):
                    st.write("**1. 重複性檢查 (Repeatability)**")
                    st.write(f"- 砝碼符合範圍: {'✅' if rep_min_g <= data['rep_w'] <= rep_max_g else '❌'}")
                    st.write(f"- $0.41d$ 修正界限: {auto_unit_format(s_threshold_g)}")
                    
                    st.write("**2. 準確度檢查 (Accuracy)**")
                    st.write(f"- 砝碼符合範圍: {'✅' if acc_min_g <= data['acc_w'] <= acc_max_g else '❌'}")
                    st.write(f"- 證書 U 需 $\le$ {auto_unit_format(mpe_absolute_g)}")

else:
    st.info("💡 目前選擇為「製造用途」，請參照內部質量管理體系(QMS)規範執行，本工具僅提供分析用途診斷。")

# --- 8. 腳註說明 ---
st.markdown("---")
with st.expander("📑 專業名詞說明 (USP 〈41〉 & 〈1251〉)"):
    st.info("""
    * **SNW (Minimum weight SNW)**: 基於機台可讀數 $d$ 的理論極限值 ($2000 \times 0.41d$)。
    * **MinW (Minimum weight)**: 依據實測 STD 算得之最小秤重量。若實測 STD < $0.41d$，則以 $0.41d$ 代入。
    * **SF (Safety Factor)**: USP 〈1251〉 建議安全係數應 $\ge 2$，以緩衝環境波動。
    """)
