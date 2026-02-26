import streamlit as st

# --- 工具函數：智慧格式化 (支援高精度且自動去零) ---
def smart_format(value):
    """將數值轉換為字串，自動去掉末尾多餘的 0，支援極小值顯示"""
    if value == 0:
        return "0"
    # 使用 Python 的 'g' 格式化，自動處理有效位數並移除末尾 0
    formatted = f"{value:.7g}"
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')
    return formatted

def format_weight_with_unit(g_value):
    """判斷單位並智慧格式化顯示"""
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
    st.markdown("依據 USP 〈1251〉 規範，請確認環境與設備狀態：")
    
    env_surface = st.checkbox("水平且非磁性的穩固表面 (Level & Nonmagnetic)")
    env_location = st.checkbox("遠離氣流、門窗、震動源與熱源")
    env_static = st.checkbox("濕度控制適當或已具備除靜電措施")
    balance_status = st.checkbox("天平已預熱並完成水平調整")
    
    if not (env_surface and env_location and env_static and balance_status):
        st.warning("⚠️ 環境檢核未完成，量測不穩定風險提高。")
    else:
        st.success("✅ 環境檢查完成。")

    st.divider()
    st.header("📋 2. 天平基本規格")
    balance_type = st.selectbox("天平類型", ["單一量程", "DR_多區間 (Multi-interval)", "DU多量程 (Multiple range)"])
    max_cap_g = st.number_input("天平最大秤重量 Max Capacity (g)", value=220.0, step=0.0000001, format="%.7f")
    is_manufacturing = st.checkbox("用於製造用途 (Manufacturing)?")

# --- 主頁面邏輯 ---
if is_manufacturing:
    st.error("🚨 **法規邊界提醒**：USP 〈41〉 範圍不涵蓋「製造用」天平。請確認用途是否為分析流程。")
else:
    ranges_to_test = 1
    if balance_type == "DU多量程 (Multiple range)":
        ranges_to_test = st.number_input("預計使用的量程數量", min_value=1, max_value=3, value=1)

    # 數據輸入區
    range_data = []
    for i in range(ranges_to_test):
        with st.expander(f"📥 量程 {i+1} 測試參數輸入", expanded=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                d_g = st.number_input(f"實際分度值 d (g) - 量程 {i+1}", value=0.0001, step=0.0000001, format="%.7f", key=f"d_{i}")
                user_snw_g = st.number_input(f"客戶預期最小淨重 (g) - 量程 {i+1}", value=0.02, step=0.0000001, format="%.7f", key=f"snw_{i}")
            with col_b:
                std_g = st.number_input(f"重複性實際量測標準差 STD (g) - 量程 {i+1}", value=0.00008, step=0.0000001, format="%.7f", key=f"std_{i}")
                rep_w_g = st.number_input(f"重複性測試砝碼重量 (g) - 量程 {i+1}", value=0.1, step=0.0000001, format="%.7f", key=f"rep_{i}")
            with col_c:
                acc_w_g = st.number_input(f"準確度測試砝碼重量 (g) - 量程 {i+1}", value=200.0, step=0.0000001, format="%.7f", key=f"acc_{i}")
            
            range_data.append({
                "d": d_g, 
                "std": std_g,
                "user_snw": user_snw_g, 
                "rep_w": rep_w_g, 
                "acc_w": acc_w_g
            })

    # --- 執行診斷按鈕 ---
    if st.button("🚀 執行全面合規性診斷"):
        st.subheader("🏁 USP 〈41〉 設備適宜性診斷報告")
        
        for idx, data in enumerate(range_data):
            # 1. 核心計算邏輯
            # A. 最小淨重量 (Smallest Net Weight) -> 理想極限
            ideal_snw_g = 2000 * 0.41 * data['d']
            
            # B. 最小秤重量 (Minimum Weight) -> 實際合規表現 (基準取 max(std, 0.41d))
            calculation_base = max(data['std'], 0.41 * data['d'])
            actual_min_weight_g = 2000 * calculation_base
            
            # C. 安全係數 (Safety Factor) = 客戶預期 / 實際表現
            safety_factor = data['user_snw'] / actual_min_weight_g if actual_min_weight_g > 0 else 0

            st.markdown(f"### 📍 量程 {idx+1} 診斷結果 (d = {smart_format(data['d'])} g)")
            
            # --- 關鍵數據顯示區 ---
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("最小淨重量 (理想)", format_weight_with_unit(ideal_snw_g))
                st.caption("機台理想底線")
            with c2:
                st.metric("最小秤重量 (實際)", format_weight_with_unit(actual_min_weight_g))
                st.caption(f"實際合規表現")
            with c3:
                st.metric("客戶預期最小淨重", format_weight_with_unit(data['user_snw']))
                st.caption("客戶目標值")
            with c4:
                # 安全係數顏色控制
                sf_color = "normal" if safety_factor >= 1 else "inverse"
                st.metric("當前安全係數 (SF)", f"{safety_factor:.2f}", delta=f"{safety_factor-1:.2f}" if safety_factor != 1 else None, delta_color=sf_color)
                st.caption("預期 / 實際")

            # --- 最終判定區 ---
            if data['user_snw'] >= actual_min_weight_g:
                st.success(f"✅ **最終判定：符合秤量需求** (客戶需求 {smart_format(data['user_snw'])} g $\ge$ 實際表現 {smart_format(actual_min_weight_g)} g)")
            else:
                st.error(f"❌ **最終判定：不符合需求** (客戶需求 {smart_format(data['user_snw'])} g < 實際表現 {smart_format(actual_min_weight_g)} g)")

            # --- 重複性與準確度細節 ---
            with st.expander("查看詳細測試條件合規性"):
                rep_min_g, rep_max_g = 0.1000, max_cap_g * 0.05
                acc_min_g, acc_max_g = max_cap_g * 0.05, max_cap_g
                
                det_col1, det_col2 = st.columns(2)
                with det_col1:
                    st.write("**重複性測試砝碼：**")
                    st.write(f"區間：{format_weight_with_unit(rep_min_g)} ~ {format_weight_with_unit(rep_max_g)}")
                    st.write(f"擬用：{format_weight_with_unit(data['rep_w'])} {'✅' if rep_min_g <= data['rep_w'] <= rep_max_g else '❌'}")
                with det_col2:
                    st.write("**準確度測試砝碼：**")
                    st.write(f"區間：{format_weight_with_unit(acc_min_g)} ~ {format_weight_with_unit(acc_max_g)}")
                    st.write(f"擬用：{format_weight_with_unit(data['acc_w'])} {'✅' if acc_min_g <= data['acc_w'] <= acc_max_g else '❌'}")

            st.divider()

# --- 底部法規導引 ---
st.subheader("📑 專業評估指標說明")
st.info("""
* **機台理想最小秤重量 (Ideal minimum weight, IMW)**: 基於解析度 $d$ 的理論最優值，代表天平在無環境干擾下的極限。
* **最小秤重量 (Minimum weight, MinW)**: 依據現場重複性測試 (STD) 算得之真實值。若實測 STD 優於 $0.41d$，則法規強制以 $0.41d$ 計算。
* **判定基準**: 當「客戶預期最小淨重(Smallest net weight)」 $\ge$ 「最小秤重量(Mimimum weight)」時，該量程判定為「符合秤量需求」。
* **安全係數 (Safety Factor)**: 反映用戶秤量目標相對於法規底線的裕度。USP 〈1251〉 建議安全係數應 $\ge 2$ 以確保製程穩定。
""")
