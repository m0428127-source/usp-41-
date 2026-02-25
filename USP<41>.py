import streamlit as st

# --- 工具函數：單位自動轉換 ---
def format_weight(g_value):
    if g_value < 1.0:
        return f"{g_value * 1000:.2f} mg"
    return f"{g_value:.4f} g"

# 設定網頁標題與風格
st.set_page_config(page_title="USP <41> & <1251> 專業合規工具", layout="wide")
st.title("⚖️ USP 〈41〉 & 〈1251〉 天平測試合規工作站")
st.caption("依據標準：USP-NF 〈41〉 & 〈1251〉 (Official Feb 1, 2026)")

# --- 側邊欄：檢查前作為 (Environment & Qualification) ---
with st.sidebar:
    st.header("🔍 1. 檢查前作為 (Pre-check)")
    st.markdown("依據 USP 〈1251〉 規範，請先確認環境與設備狀態：")
    
    env_surface = st.checkbox("水平且非磁性的穩固表面 (Level & Nonmagnetic) [cite: 328, 329]")
    env_location = st.checkbox("遠離氣流、門窗、震動源與熱源 [cite: 331, 332]")
    env_static = st.checkbox("濕度控制適當或已具備除靜電措施 [cite: 340, 501]")
    balance_status = st.checkbox("天平已預熱並完成水平調整 [cite: 345, 372]")
    
    if not (env_surface and env_location and env_static and balance_status):
        st.warning("⚠️ 環境檢核未完成，測試結果可能不具法律效力。")
    else:
        st.success("✅ 環境檢查完成，準備執行測試。")

    st.divider()
    st.header("📋 2. 天平基本規格 (g)")
    balance_type = st.selectbox("天平類型", ["單一量程", "多區間 (Multi-interval)", "多量程 (Multiple range)"])
    max_cap_g = st.number_input("全機最大容量 Max Capacity (g)", value=220.0, format="%.4f")
    is_manufacturing = st.sidebar.checkbox("用於製造用途 (Manufacturing)? [cite: 571]")

# --- 主頁面：動態量程設計 ---
if is_manufacturing:
    st.error("🚨 **法規邊界提醒**：USP 〈41〉 的範圍不涵蓋「製造用」天平。請確認您的用途是否為分析流程。 [cite: 571]")
else:
    # 根據天平類型動態生成輸入區
    ranges_to_test = 1
    if balance_type == "多量程 (Multiple range)":
        ranges_to_test = st.number_input("預計使用的量程數量 (USP 規定每個量程都要測)", min_value=1, max_value=3, value=1)
        st.info("💡 **多量程提醒**：若需進入較粗量程，請使用預載物 (Preload) 或皮重容器。 ")

    # 建立量程數據存儲
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
        # 計算結果顯示
        st.subheader("🏁 診斷判定報告")
        
        for idx, data in enumerate(range_data):
            st.markdown(f"#### 📍 量程 {idx+1} (d = {data['d']:.5f} g) 診斷結果")
            
            # 法規基準計算 (單位 g)
            rep_min_limit = 0.1000 # [cite: 584]
            rep_max_limit = max_cap_g * 0.05 # 
            acc_min_limit = max_cap_g * 0.05 # [cite: 608]
            
            # 理論最小重量限制 (s = 0.41d) [cite: 591, 592]
            theoretical_min_weight = (2 * 0.41 * data['d']) / 0.001
            
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                st.write("**1. 重複性砝碼適宜性**")
                if data['rep_w'] < rep_min_limit - 0.000001:
                    st.error(f"❌ 失敗：砝碼重量需 ≥ 100 mg [cite: 584]。")
                elif data['rep_w'] > rep_max_limit + 0.000001:
                    st.error(f"❌ 失敗：超過全量程 5% ({format_weight(rep_max_limit)}) 。")
                else:
                    st.success(f"✅ 合規：擬用 {format_weight(data['rep_w'])}。")
                
                # 多量程點位提醒 
                if balance_type == "多量程 (Multiple range)" and idx > 0:
                    st.warning("⚠️ **工程師提醒**：測此量程前，請先放置預載物 (Preload) 並歸零。")

            with res_col2:
                st.write("**2. 準確度砝碼適宜性**")
                if data['acc_w'] < acc_min_limit - 0.000001:
                    st.error(f"❌ 失敗：需在 5% 至 100% 容量之間 [cite: 608]。")
                elif data['acc_w'] > max_cap_g + 0.000001:
                    st.error(f"❌ 失敗：超過最大量程。")
                else:
                    st.success(f"✅ 合規：擬用 {format_weight(data['acc_w'])}。")
                st.caption(f"💡 砝碼 MPE 應 < {0.05/3:.4f}% ({format_weight(data['acc_w']*0.05/100/3)}) ")

            # 最小重量診斷
            if data['snw'] < theoretical_min_weight:
                st.error(f"🛑 **能力不符**：最小淨重需求 ({format_weight(data['snw'])}) 低於物理極限 ({format_weight(theoretical_min_weight)})。 [cite: 592]")
            elif data['snw'] < theoretical_min_weight * 2:
                st.warning(f"⚠️ **建議**：建議採用安全係數 2.0，將操作下限設為 {format_weight(theoretical_min_weight*2)} 以上。 [cite: 458]")
            else:
                st.success(f"✅ **匹配**：天平能力足以應付此量程之秤重需求。")
            
            st.divider()

# --- 專業建議區塊 (基於 USP 1251) ---
st.subheader("📑 工程師溝通指南 (Professional Guidance)")
with st.expander("為什麼要這樣測？ (法律依據參考)"):
    st.markdown("""
    * **關於多量程 (Multiple Range)**：USP 〈41〉 規定必須在每個使用的量程執行測試。為了進入較粗的量程，必須先在秤盤放置「預載物」(Preload) 並按 Tare 。
    * **關於標準差 (s)**：如果實測出的 $s < 0.41d$，則必須以 $0.41d$ 代替計算最小重量，這是因為數位顯示器本身的四捨五入誤差 (Rounding error) [cite: 442, 591]。
    * **安全係數 (Safety Factor)**：USP 〈1251〉 建議，環境或操作人員的不同會影響重複性，建議在穩定的實驗室環境使用 **SF=2** [cite: 458]。
    """)

st.info("💡 **下一步工作建議**：如果診斷結果顯示合規，您可以開始進行 10 次重複性秤重，並將實測標準差填入校正報告中。")
