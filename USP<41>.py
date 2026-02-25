import streamlit as st

# 輔助函數：格式化顯示
def format_weight(g_value)
    if g_val < 1.0:
        return f"{g_val * 1000:.2f} mg"
    return f"{g_val:.4f} g"

# 假設這些變數已從側邊欄輸入
# max_capacity, d_value, balance_type, user_rep_w_g, user_acc_w_g, m_snw_g

st.markdown("---")
st.header("🏁 USP 〈41〉 設備適宜性診斷報告")

# --- 診斷邏輯計算 ---
# 重複性限制
rep_w_min_g = 0.1000 # 100mg [cite: 276]
rep_w_max_g = max_capacity * 0.05 # 5% Max Cap [cite: 272]
s_threshold_mg = 0.41 * (d_value * 1000) # 0.41d 門檻 [cite: 283]

# 準確度限制
acc_w_min_g = max_capacity * 0.05 # 5% Max Cap [cite: 300]
acc_w_max_g = max_capacity [cite: 300]
mpe_limit_percent = (0.05 / 3) # 1/3 of 0.05% [cite: 298, 302]

# --- 報告呈現：分為兩個 Column ---
diag_col1, diag_col2 = st.columns(2)

with diag_col1:
    st.subheader("🧪 重複性測試診斷")
    
    # 1. 砝碼重量判定
    is_rep_w_ok = rep_w_min_g <= user_rep_w_g <= rep_w_max_g
    rep_status_icon = "✅" if is_rep_w_ok else "❌"
    
    st.markdown(f"""
    **{rep_status_icon} 測試砝碼選擇**
    * 擬用重量：`{user_rep_w_g:.4f} g`
    * 法規要求：`{rep_w_min_g:.1f} g` ~ `{rep_w_max_g:.4f} g`
    * **判定**：{"符合 USP <41> 區間要求" if is_rep_w_ok else "重量超出法規建議範圍"}
    """)

    # 2. 點位與標準判定
    with st.expander("點位與計算細節", expanded=True):
        if balance_type == "多量程 (Multiple range)":
            st.warning("📍 **多量程提醒**：請確認已在「每一個使用中的量程」執行測試，且進入粗量程時已放置預載物 (Preload) 。")
        
        st.info(f"💡 **0.41d 門檻**：若實測標準差 $s < {s_threshold_mg:.4f} \text{ mg}$，計算時須以 {s_threshold_mg:.4f} \text{ mg} 取代 [cite: 283, 286]。", icon="ℹ️")

with diag_col2:
    st.subheader("🎯 準確度測試診斷")

    # 1. 砝碼重量判定
    is_acc_w_ok = acc_min <= user_acc_w_g <= acc_max
    acc_status_icon = "✅" if is_acc_w_ok else "❌"

    st.markdown(f"""
    **{acc_status_icon} 測試砝碼選擇**
    * 擬用重量：`{user_acc_w_g:.4f} g`
    * 法規要求：`{acc_min:.4f} g` ~ `{acc_max:.4f} g`
    * **判定**：{"符合 USP <41> 區間要求" if is_acc_w_ok else "重量超出 5%-100% 範圍"}
    """)

    # 2. 砝碼等級判定提示
    required_mpe_g = user_acc_w_g * (mpe_limit_percent / 100)
    st.markdown(f"""
    **⚖️ 砝碼等級要求 (1/3 規則)**
    * 擬用砝碼之 $MPE$ 或 $U$ 必須小於：**{required_mpe_g:.6f} g**
    * *(請檢查您的砝碼校正證書，確保符合上述精度)* 
    """)

st.divider()

# --- 最小淨重能力預判 ---
st.subheader("🛡️ 最小淨重能力預判 (Smallest Net Weight)")
min_weight_res_g = (2 * (0.41 * d_value)) / 0.001 # 基礎極限 [cite: 282, 286]

c1, c2 = st.columns([1, 2])
with c1:
    st.metric("天平極限最小淨重", f"{min_weight_res_g*1000:.2f} mg")
with c2:
    if m_snw_g < min_weight_res_g:
        st.error(f"🚨 **警告**：客戶要求的 {m_snw_g*1000:.2f} mg 低於天平物理極限，測試必將失敗 [cite: 147, 291]。", icon="🚨")
    elif m_snw_g < min_weight_res_g * 2:
        st.warning(f"⚠️ **提醒**：需求接近極限。依據 USP <1251>，建議設定安全係數為 2，即建議最小秤量為 {min_weight_res_g*2000:.2f} mg 。", icon="⚠️")
    else:
        st.success(f"✅ **合規**：此天平性能足以支援客戶的最小淨重需求。", icon="✅")
