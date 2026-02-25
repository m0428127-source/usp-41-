import streamlit as st

# --- 工具函數：單位自動轉換 ---
def format_weight(g_value):
    if g_value < 1.0:
        return f"{g_value * 1000:.2f} mg"
    return f"{g_value:.4f} g"

# 設定網頁標題與風格
st.set_page_config(page_title="USP <41> & <1251> 專業合規工作站", layout="wide")
st.title("⚖️ USP 〈41〉 & 〈1251〉 天平測試合規工作站")
st.caption("工程師進階版 | 依據標準：USP-NF 〈41〉 & 〈1251〉 (Official Feb 1, 2026)")

# --- 側邊欄：檢查前作為 (Pre-check) ---
with st.sidebar:
    st.header("🔍 1. 檢查前作為 (Pre-check)")
    st.markdown("依據 USP 〈1251〉 規範，請先確認環境與設備狀態：")
    
    env_surface = st.checkbox("水平且非磁性的穩固表面 (Level & Nonmagnetic)")
    env_location = st.checkbox("遠離氣流、門窗、震動源與熱源")
    env_static = st.checkbox("濕度控制適當或已具備除靜電措施")
    balance_status = st.checkbox("天平已預熱並完成水平調整")
    
    if not (env_surface and env_location and env_static and balance_status):
        st.warning("⚠️ 環境檢核未完成，測試結果可能不具法律效力。")
    else:
        st.success("✅ 環境檢查完成，準備執行測試。")

    st.divider()
    st.header("📋 2. 天平基本規格 (g)")
    balance_type = st.selectbox("天平類型", ["單一量程", "多區間 (Multi-interval)", "多量程 (Multiple range)"])
    max_cap_g = st.number_input("全機最大容量 Max Capacity (g)", value=220.0, format="%.4f")
    is_manufacturing = st.checkbox("用於製造用途 (Manufacturing)?")

# --- 主頁面邏輯 ---
if is_manufacturing:
    st.error("🚨 **法規邊界提醒**：USP 〈41〉 的範圍不涵蓋「製造用」天平。請確認您的用途是否為分析流程。")
else:
    # 根據天平類型動態生成輸入區
    ranges_to_test = 1
    if balance_type == "多量程 (Multiple range)":
        ranges_to_test = st.number_input("預計使用的量程數量 (USP 規定每個量程都要測)", min_value=1, max_value=3, value=1)
        st.info("💡 **多量程提醒**：若需進入較粗量程，請使用預載物 (Preload) 或皮重容器。")

    range_data = []
    for i in range(ranges_to_test):
        with st.expander(f"📥 量程 {i+1} 測試參數輸入", expanded=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                d_g = st.number_input(f"實際分度值 d (g) - 量程 {i+1}", value=0.0001, format="%.5f", key=f"d_{i}")
                snw_g = st.number_input(f"客戶最小淨重 (g) - 量程 {i+1}", value=0.02, format="%.4f", key=f"snw_{i}")
            with col_b:
                rep_w_g = st.number_input(f"擬用重複性砝碼 (g) - 量程 {i+1}", value=0.1, format="%.4f", key=f"rep_{i}")
            with col_c:
                acc_w_g = st.number_input(f"擬用準確度砝碼 (g) - 量程 {i+1}", value=200.0, format="%.4f", key=f"acc_{i}")
            range_data.append({"d": d_g, "snw": snw_g, "rep_w": rep_w_g, "acc_w": acc_w_g})

    if st.button("🚀 執行全面合規性診斷"):
        st.subheader("🏁 USP 〈41〉 設備適宜性診斷報告")
        
        for idx, data in enumerate(range_data):
            st.markdown(f"### 📍 量程 {idx+1} 診斷結果 (d = {data['d']:.5f} g)")
            
            # --- 重複性與準確度：雙欄對比 ---
            diag_col1, diag_col2 = st.columns(2)

            with diag_col1:
                st.info("#### 1. 重複性測試要求 (Repeatability)")
                # 法規計算
                rep_min_limit = 0.1000 
                rep_max_limit = max_cap_g * 0.05
                is_rep_ok = rep_min_limit <= data['rep_w'] <= rep_max_limit
                
                st.markdown(f"""
                **【法規規格要求】**
                * **砝碼區間**：`{format_weight(rep_min_limit)}` ~ `{format_weight(rep_max_limit)}`
                * **允收標準**：$2 \times s / m_{{SNW}} \le 0.10\%$
                * **關鍵限制**：若 $s < {0.41 * data['d'] * 1000:.4f} \text{ mg}$ ($0.41d$)，計算時需以該值取代。
                """)
                
                # 即時判定
                status_rep = "✅ 符合規範" if is_rep_ok else "❌ 規格不符"
                st.success(f"**【實測對比判斷】**\n\n* 擬用砝碼：`{format_weight(data['rep_w'])}` ({status_rep})")
                
                if balance_type == "多量程 (Multiple range)" and idx > 0:
                    st.warning("📍 **點位提醒**：此量程測試需先放置預載物 (Preload)。")
                elif balance_type == "多區間 (Multi-interval)":
                    st.write("📍 **點位要求**：必須在最精細量程執行。")

            with diag_col2:
                st.info("#### 2. 準確度測試要求 (Accuracy)")
                # 法規計算
                acc_min_limit = max_cap_g * 0.05
                acc_max_limit = max_cap_g
                is_acc_ok = acc_min_limit <= data['acc_w'] <= acc_max_limit
                uncertainty_limit = (0.05 / 100) / 3 # 1/3 of 0.05%
                
                st.markdown(f"""
                **【法規規格要求】**
                * **砝碼區間**：`{format_weight(acc_min_limit)}` ~ `{format_weight(acc_max_limit)}`
                * **允收標準**：誤差 $\le 0.05\%$
                * **砝碼限制**：$MPE$ 或 $U$ 需小於 **{uncertainty_limit * 100:.4f}%** (即 0.05% 的 1/3)。
                """)
                
                # 即時判定
                status_acc = "✅ 符合規範" if is_acc_ok else "❌ 規格不符"
                mpe_absolute = data['acc_w'] * uncertainty_limit
                st.success(f"**【實測對比判斷】**\n\n* 擬用砝碼：`{format_weight(data['acc_w'])}` ({status_acc})")
                st.caption(f"💡 砝碼證書 $U$ 值須 $\le {mpe_absolute:.6f} \text{ g}$")

            # --- 最小淨重判定 ---
            theoretical_min_weight = (2 * 0.41 * data['d']) / 0.001
            st.markdown(f"#### 🛡️ 最小淨重能力判定 (Smallest Net Weight)")
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("天平極限下限 (s=0.41d)", format_weight(theoretical_min_weight))
            with c2:
                if data['snw'] < theoretical_min_weight:
                    st.error(f"🚨 **嚴重警告**：客戶要求 ({format_weight(data['snw'])}) 低於此天平物理極限。測試必將失敗。")
                elif data['snw'] < theoretical_min_weight * 2:
                    st.warning(f"⚠️ **操作風險**：需求接近極限。依據 USP 〈1251〉，建議至少保留 2 倍安全係數 ({format_weight(theoretical_min_weight*2)})。")
                else:
                    st.success(f"✅ **匹配成功**：天平能力足以支撐客戶需求。")
            
            st.divider()

# --- 專業建議區塊 ---
st.subheader("📑 工程師溝通指南 (Professional Guidance)")
with st.expander("為什麼要這樣測？ (法律依據參考)"):
    st.markdown("""
    * **多量程 (Multiple Range)**：必須在每個使用的量程執行測試。進入粗量程需預載物。
    * **標準差底線 (0.41d)**：數位顯示器的捨入誤差限制了最小可測標準差。
    * **1/3 規則**：確保測試用砝碼的精確度遠高於天平的允收標準 (0.05%)。
    """)
