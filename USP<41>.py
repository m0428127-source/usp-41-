# --- 數據輸入區 (手機優化版：使用 Tabs) ---
with st.expander(f"📥 測試參數輸入 ({display_unit})", expanded=True):
    # 在手機上，Tabs 比 Columns 更容易點擊與閱讀
    tab1, tab2, tab3 = st.tabs(["📏 分度與淨重", "📊 重複性 (STD)", "🎯 準確度 (ACC)"])
    
    if balance_type == "DU_多量程 (Multiple range)":
        with tab1:
            d1_raw = st.number_input(f"實際分度值 d1 ({display_unit})", value=float(convert_from_g(0.00001, display_unit)), step=p_step, format=p_format)
            d2_raw = st.number_input(f"實際分度值 d2 ({display_unit})", value=float(convert_from_g(0.0001, display_unit)), step=p_step, format=p_format)
            snw1_raw = st.number_input(f"客戶預期最小淨重 1 ({display_unit})", value=float(convert_from_g(0.02, display_unit)), step=p_step, format=p_format)
            snw2_raw = st.number_input(f"客戶預期最小淨重 2 ({display_unit})", value=float(convert_from_g(0.2, display_unit)), step=p_step, format=p_format)
        with tab2:
            std1_raw = st.number_input(f"實際量測標準差 STD1 ({display_unit})", value=float(convert_from_g(0.000008, display_unit)), step=p_step, format=p_format)
            std2_raw = st.number_input(f"實際量測標準差 STD2 ({display_unit})", value=float(convert_from_g(0.00008, display_unit)), step=p_step, format=p_format)
            rep_w_raw = st.number_input(f"重複性測試砝碼重量 ({display_unit})", value=float(convert_from_g(0.1, display_unit)), step=p_step, format=p_format)
            rep_w_g = convert_to_g(rep_w_raw, display_unit)
        with tab3:
            acc_w_raw = st.number_input(f"準確度測試砝碼重量 ({display_unit})", value=float(convert_from_g(200.0, display_unit)), step=p_step, format=p_format)
            acc_w_g = convert_to_g(acc_w_raw, display_unit)
