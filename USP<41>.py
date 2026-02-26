import streamlit as st

# --- 工具函數：智慧格式化 (支援高精度且自動去零) ---
def smart_format(value):
    """將數值轉換為字串，自動去掉末尾無意義的 0，支援極小值顯示"""
    if value == 0:
        return "0"
    # 使用 Python 的 format 函數，最高支援到小數點後 7 位
    # 'g' 格式會自動處理有效位數並移除末尾的 0
    return f"{value:.7g}".rstrip('0').rstrip('.') if '.' in f"{value:.7g}" else f"{value:.7g}"

def format_weight_with_unit(g_value):
    """判斷單位並格式化顯示"""
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
    # 移除固定格式，改用 step 控制精度
    max_cap_g = st.number_input("天平最大秤重量 Max Capacity (g)", value=220.0, step=0.0000001)
    is_manufacturing = st.checkbox("用於製造用途 (Manufacturing)?")

# --- 主頁面邏輯 ---
if is_manufacturing:
    st.error("🚨 **法規邊界提醒**：USP 〈41〉 範圍不涵蓋「製造用」天平。請確認用途是否為分析流程。")
else:
    ranges_to_test = 1
    if balance_type == "DU多量程 (Multiple range)":
        ranges_to_test = st.number_input("預計使用的量程數量", min_value=1, max_value=3, value=1)
        st.info("💡 **多量程提醒**：若需進入較粗量程，請使用預載物 (Preload)。")

    # 數據輸入區
    range_data = []
    for i in range(ranges_to_test):
        with st.expander(f"📥 量程 {i+1} 測試參數輸入", expanded=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                # 設定 step 為 0.0000001 以支援到小數點後 7 位，且不設定 format 強制補 0
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
            # 1. 重複性與準確度砝碼範圍判定
            rep_min_g, rep_max_g = 0.1000, max_cap_g * 0.05
            acc_min_g, acc_max_g = max_cap_g * 0.05, max_cap_g
            
            # 2. 核心計算邏輯
            # A. 最小淨重量 (Smallest Net Weight) -> 理想極限狀態
            ideal_snw_g = 2000 * 0.41 * data['d']
            
            # B. 最小秤重量 (Minimum Weight) -> 依據實測 STD 判定
            calculation_base = max(data['std'], 0.41 * data['d'])
            actual_min_weight_g = 2000 * calculation_base

            st.markdown(f"### 📍 量程 {idx+1} 診斷結果 (d = {smart_format(data['d'])} g)")
            
            # --- 雙欄報告 ---
            diag_col1, diag_col2 = st.columns(2)
            with diag_col1:
                st.info("#### 1. 重複性測試 (Repeatability)")
                st.markdown(f"""
                * **砝碼合規區間**：`{format_weight_with_unit(rep_min_g)}` ~ `{format_weight_with_unit(rep_max_g)}`
                * **擬用砝碼**：`{format_weight_with_unit(data['rep_w'])}` {"✅" if rep_min_g <= data['rep_w'] <= rep_max_g else "❌"}
                """)
            with diag_col2:
                st.info("#### 2. 準確度測試 (Accuracy)")
                st.markdown(f"""
                * **砝碼合規區間**：`{format_weight_with_unit(acc_min_g)}` ~ `{format_weight_with_unit(acc_max_g)}`
                * **擬用砝碼**：`{format_weight_with_unit(data['acc_w'])}` {"✅" if acc_min_g <= data['acc_w'] <= acc_max_g else "❌"}
                """)

            # --- 關鍵重量判定區 ---
            st.markdown("#### 🛡️ 關鍵秤量能力判定")
            res_c1, res_c2, res_c3 = st.columns(3)
            
            with res_c1:
                st.metric("最小淨重量 (理想狀態)", format_weight_with_unit(ideal_snw_g))
                st.caption(f"公式: $2000 \\times 0.41 \\times {smart_format(data['d'])}$")
                
            with res_c2:
                st.metric("最小秤重量 (實測合規)", format_weight_with_unit(actual_min_weight_g))
                st.caption(f"基準值: {smart_format(calculation_base)} g")
                
            with res_c3:
                if data['user_snw'] < actual_min_weight_g:
                    st.error(f"❌ **判定：不符合需求**\n\n客戶需求 ({format_weight_with_unit(data['user_snw'])}) 低於實測最小秤重量。")
                elif data['user_snw'] < actual_min_weight_g * 2:
                    st.warning(f"⚠️ **判定：建議增加安全係數**\n\n符合法規，但建議設為 {format_weight_with_unit(actual_min_weight_g * 2)} (SF=2)。")
                else:
                    st.success(f"✅ **判定：符合秤量需求**\n\n天平表現優於客戶需求。")
            
            st.divider()

# --- 底部法規導引 ---
st.subheader("📑 工程師筆記")
with st.expander("名詞定義與邏輯說明"):
    st.markdown(f"""
    * **最小淨重量 (Smallest Net Weight)**：基於天平分度值 $d$ 的理論極限。
    * **最小秤重量 (Minimum Weight)**：基於重複性實測標準差 $s$。若 $s < 0.41d$，則以 $0.41d$ 代替。
    * **判定標準**：日常秤量之淨重（Net Weight）必須 $\ge$ 最小秤重量。
    """)
