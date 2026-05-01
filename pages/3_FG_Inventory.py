# ═══ TAB 2 — CFA STOCK vs OPEN ORDERS (SAP/Oracle Enterprise UI) ══════════════
with tab2:

    # ── SAP/Oracle Enterprise CSS ───────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

    /* ── SAP Enterprise Shell ── */
    .sap-shell {
        font-family: 'IBM Plex Sans', sans-serif;
        color: #1a2332;
    }

    /* ── Section Header Bar (like SAP Fiori tile headers) ── */
    .sap-section-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, #0a2540 0%, #0d3060 100%);
        border-left: 4px solid #0070f3;
        padding: 10px 18px;
        margin: 14px 0 10px 0;
        border-radius: 0 4px 4px 0;
    }
    .sap-section-bar .sap-title {
        font-size: 12px;
        font-weight: 700;
        color: #e8f1ff;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        font-family: 'IBM Plex Mono', monospace;
    }
    .sap-section-bar .sap-badge {
        background: #0070f3;
        color: #fff;
        font-size: 10px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 2px;
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 0.5px;
    }

    /* ── KPI Tiles (SAP Fiori Key Figure tiles) ── */
    .sap-kpi-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 8px;
        margin-bottom: 14px;
    }
    .sap-kpi-tile {
        background: #fff;
        border: 1px solid #c8d3e0;
        border-top: 3px solid #4a90d9;
        border-radius: 3px;
        padding: 12px 14px 10px;
        position: relative;
    }
    .sap-kpi-tile.critical { border-top-color: #bb3322; background: #fff8f8; }
    .sap-kpi-tile.warning  { border-top-color: #e07b00; background: #fffcf5; }
    .sap-kpi-tile.success  { border-top-color: #1e8a3f; background: #f5fff8; }
    .sap-kpi-tile.info     { border-top-color: #0070f3; }
    .sap-kpi-tile.neutral  { border-top-color: #5a6a7a; }

    .sap-kpi-label {
        font-size: 10px;
        font-weight: 600;
        color: #6b7c93;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .sap-kpi-value {
        font-size: 22px;
        font-weight: 700;
        color: #0d1f38;
        font-family: 'IBM Plex Mono', monospace;
        line-height: 1;
        letter-spacing: -0.5px;
    }
    .sap-kpi-tile.critical .sap-kpi-value { color: #bb3322; }
    .sap-kpi-tile.warning  .sap-kpi-value { color: #a05800; }
    .sap-kpi-tile.success  .sap-kpi-value { color: #1e7a38; }
    .sap-kpi-sub {
        font-size: 10px;
        color: #8a9bb0;
        margin-top: 4px;
        font-family: 'IBM Plex Mono', monospace;
    }

    /* ── Formula Bar (like SAP formula/calculation strip) ── */
    .sap-formula-strip {
        background: #f0f4f9;
        border: 1px solid #c8d3e0;
        border-left: 3px solid #0070f3;
        border-radius: 0 3px 3px 0;
        padding: 8px 16px;
        margin-bottom: 12px;
        font-size: 11px;
        font-family: 'IBM Plex Mono', monospace;
        color: #4a5a6a;
        display: flex;
        gap: 6px;
        align-items: center;
        flex-wrap: wrap;
    }
    .sap-formula-strip .f-tag {
        background: #0070f3;
        color: #fff;
        padding: 1px 7px;
        border-radius: 2px;
        font-weight: 600;
        font-size: 10px;
    }
    .sap-formula-strip .f-op {
        color: #0070f3;
        font-weight: 700;
        font-size: 13px;
    }
    .sap-formula-strip .f-note {
        color: #8a9bb0;
        font-size: 10px;
        font-style: italic;
    }

    /* ── STN Mode Toggle (like SAP segmented button) ── */
    .sap-mode-strip {
        background: #f0f4f9;
        border: 1px solid #c8d3e0;
        border-radius: 3px;
        padding: 10px 14px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 14px;
        flex-wrap: wrap;
    }
    .sap-mode-label {
        font-size: 11px;
        font-weight: 600;
        color: #3a4a5a;
        font-family: 'IBM Plex Sans', sans-serif;
        white-space: nowrap;
    }
    .sap-mode-pill {
        display: inline-block;
        font-size: 10px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 2px;
        font-family: 'IBM Plex Mono', monospace;
    }
    .sap-mode-pill.with-stn    { background: #e6f0ff; color: #0050b3; border: 1px solid #a0c0f0; }
    .sap-mode-pill.without-stn { background: #fff4e6; color: #8a4500; border: 1px solid #f0c070; }

    /* ── Fill Rate Panel ── */
    .sap-fill-panel {
        background: #fff;
        border: 1px solid #c8d3e0;
        border-radius: 3px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .sap-fill-panel-title {
        font-size: 11px;
        font-weight: 700;
        color: #3a4a5a;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        border-bottom: 1px solid #e0e8f0;
        padding-bottom: 8px;
        margin-bottom: 10px;
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .sap-fill-row {
        display: grid;
        grid-template-columns: 180px 1fr 70px 100px 90px;
        align-items: center;
        gap: 10px;
        padding: 7px 0;
        border-bottom: 1px solid #f0f4f9;
    }
    .sap-fill-row:last-child { border-bottom: none; }
    .sap-fill-cfa-name {
        font-size: 11px;
        font-weight: 600;
        color: #1a2332;
        font-family: 'IBM Plex Sans', sans-serif;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .sap-fill-bar-wrap {
        background: #e8edf4;
        border-radius: 2px;
        height: 10px;
        position: relative;
    }
    .sap-fill-bar-inner {
        height: 10px;
        border-radius: 2px;
        transition: width 0.3s ease;
    }
    .sap-fill-pct {
        font-size: 11px;
        font-weight: 700;
        font-family: 'IBM Plex Mono', monospace;
        text-align: right;
    }
    .sap-fill-avail {
        font-size: 10px;
        color: #6b7c93;
        font-family: 'IBM Plex Mono', monospace;
        text-align: right;
    }
    .sap-fill-short {
        font-size: 10px;
        font-weight: 700;
        text-align: right;
        font-family: 'IBM Plex Mono', monospace;
    }

    /* ── Status chips ── */
    .sap-chip {
        display: inline-block;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 2px;
        font-family: 'IBM Plex Mono', monospace;
        white-space: nowrap;
    }
    .sap-chip.ok       { background: #e6f5ec; color: #1a6b35; border: 1px solid #9dd5b0; }
    .sap-chip.warn     { background: #fff4e0; color: #8a4500; border: 1px solid #f0c070; }
    .sap-chip.critical { background: #fdecea; color: #9a1f1f; border: 1px solid #f0a0a0; }

    /* ── Expiry Heatmap (SAP ALV-style) ── */
    .sap-heatmap-wrap {
        background: #fff;
        border: 1px solid #c8d3e0;
        border-radius: 3px;
        overflow: hidden;
    }
    .sap-hm-header {
        display: grid;
        grid-template-columns: 160px repeat(5, 1fr);
        background: #1a3050;
        color: #c8daf0;
        font-size: 10px;
        font-weight: 700;
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        padding: 0;
    }
    .sap-hm-header-cell {
        padding: 8px 10px;
        border-right: 1px solid #254065;
        text-align: center;
    }
    .sap-hm-header-cell:first-child { text-align: left; }
    .sap-hm-row {
        display: grid;
        grid-template-columns: 160px repeat(5, 1fr);
        border-bottom: 1px solid #e8edf4;
    }
    .sap-hm-row:last-child { border-bottom: none; }
    .sap-hm-row:hover { background: #f5f8fc; }
    .sap-hm-cell {
        padding: 7px 10px;
        font-size: 11px;
        font-family: 'IBM Plex Mono', monospace;
        text-align: center;
        border-right: 1px solid #e8edf4;
    }
    .sap-hm-cell:first-child { text-align: left; font-weight: 600; color: #1a2332; font-family: 'IBM Plex Sans', sans-serif; font-size: 11px; }
    .sap-hm-total-row {
        display: grid;
        grid-template-columns: 160px repeat(5, 1fr);
        background: #f0f4f9;
        border-top: 2px solid #c8d3e0;
    }
    .sap-hm-total-cell {
        padding: 8px 10px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'IBM Plex Mono', monospace;
        text-align: center;
        border-right: 1px solid #d0dae4;
        color: #1a2332;
    }
    .sap-hm-total-cell:first-child { text-align: left; }

    /* ── Batch panel (SAP detail panel) ── */
    .sap-detail-panel {
        background: #f8fafd;
        border: 1px solid #c8d3e0;
        border-left: 4px solid #0070f3;
        border-radius: 0 3px 3px 0;
        padding: 14px 18px;
        margin-bottom: 12px;
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .sap-detail-panel .dp-title {
        font-size: 11px;
        font-weight: 700;
        color: #0050b3;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 10px;
    }
    .sap-batch-row {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 5px 0;
        border-bottom: 1px solid #e8edf4;
    }
    .sap-batch-row:last-child { border-bottom: none; }

    /* ── Telegram section ── */
    .sap-action-bar {
        background: #f0f4f9;
        border: 1px solid #c8d3e0;
        border-radius: 3px;
        padding: 10px 16px;
        margin-top: 14px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Force light background for this tab's dataframes */
    [data-testid="stTabs"] [data-baseweb="tab-panel"] {
        background: #f5f8fc !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── STN Mode Selector ───────────────────────────────────────────────────────
    st.markdown('<div class="sap-mode-strip">', unsafe_allow_html=True)
    col_mode_label, col_mode_sel, col_mode_cfa = st.columns([1.2, 1.5, 1.5])
    with col_mode_label:
        st.markdown('<div class="sap-mode-label">📐 Availability Calculation Mode</div>', unsafe_allow_html=True)
    with col_mode_sel:
        stn_mode = st.selectbox(
            "stn_mode",
            ["With STN In-Transit", "Without STN In-Transit"],
            label_visibility="collapsed",
            key="tab2_stn_mode"
        )
    with col_mode_cfa:
        sel_cfa2 = st.selectbox(
            "cfa2",
            ["All CFAs"] + cfa_warehouses,
            label_visibility="collapsed",
            key="tab2_cfa_filter"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Derived values based on STN mode ───────────────────────────────────────
    include_stn = (stn_mode == "With STN In-Transit")

    if include_stn:
        _total_avail_tab2 = cfa_fg + stn_cfa_qty
        _diff_tab2 = _total_avail_tab2 - open_so_qty
        _formula_stn_note = '<span class="f-tag">FG + STN</span>'
        _avail_label = "FG + STN In-Transit"
    else:
        _total_avail_tab2 = cfa_fg
        _diff_tab2 = cfa_fg - open_so_qty
        _formula_stn_note = '<span class="f-tag">FG Only</span>'
        _avail_label = "FG Stock Only"

    # ── Formula Strip ──────────────────────────────────────────────────────────
    _stn_part = ' <span class="f-op">+</span> <span class="f-tag">STN In-Transit</span>' if include_stn else ' <span class="f-note">(STN excluded)</span>'
    st.markdown(f"""
    <div class="sap-formula-strip">
        <span class="f-tag">DIFF</span>
        <span class="f-op">=</span>
        <span class="f-tag">CFA FG Stock</span>
        {_stn_part}
        <span class="f-op">−</span>
        <span class="f-tag">Open PO Qty</span>
        <span class="f-note">· Excl. Cancelled & Closed SOs</span>
        &nbsp;|&nbsp;
        <span style="color:#0070f3;font-weight:700;">Mode: {stn_mode}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Tiles ──────────────────────────────────────────────────────────────
    _diff_cls = "success" if _diff_tab2 >= 0 else "critical"
    _diff_icon = "▲" if _diff_tab2 >= 0 else "▼"
    st.markdown(f"""
    <div class="sap-kpi-grid">
        <div class="sap-kpi-tile info">
            <div class="sap-kpi-label">CFA FG Stock</div>
            <div class="sap-kpi-value">{cfa_fg:,.0f}</div>
            <div class="sap-kpi-sub">At CFA warehouses</div>
        </div>
        <div class="sap-kpi-tile {'info' if include_stn else 'neutral'}">
            <div class="sap-kpi-label">STN In-Transit</div>
            <div class="sap-kpi-value" style="{'color:#0070f3' if include_stn else 'color:#8a9bb0'}">{stn_cfa_qty:,.0f}</div>
            <div class="sap-kpi-sub">{'Included in calc' if include_stn else 'Excluded from calc'}</div>
        </div>
        <div class="sap-kpi-tile info">
            <div class="sap-kpi-label">{_avail_label}</div>
            <div class="sap-kpi-value">{_total_avail_tab2:,.0f}</div>
            <div class="sap-kpi-sub">Effective available qty</div>
        </div>
        <div class="sap-kpi-tile warning">
            <div class="sap-kpi-label">Open PO Qty</div>
            <div class="sap-kpi-value">{open_so_qty:,.0f}</div>
            <div class="sap-kpi-sub">Excl. Cancelled & Closed</div>
        </div>
        <div class="sap-kpi-tile {_diff_cls}">
            <div class="sap-kpi-label">Net Diff ({stn_mode})</div>
            <div class="sap-kpi-value">{_diff_icon} {abs(_diff_tab2):,.0f}</div>
            <div class="sap-kpi-sub">{'Surplus ▲' if _diff_tab2 >= 0 else 'Shortfall ▼'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Data Processing (same as before, respecting STN mode) ──────────────────
    df_cfa = df_fg[df_fg["Warehouse"].astype(str).apply(is_cfa)].copy() if "Warehouse" in df_fg.columns else pd.DataFrame()
    if sel_cfa2 != "All CFAs" and not df_cfa.empty:
        df_cfa = df_cfa[df_cfa["Warehouse"].astype(str) == sel_cfa2]
    if search and not df_cfa.empty:
        df_cfa = df_cfa[df_cfa.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]

    if not df_cfa.empty and "Item SKU" in df_cfa.columns:
        fg_agg = df_cfa.groupby(["Item SKU","Warehouse"]).agg(
            Item_Name=("Item Name","first"), Category=("Category","first"),
            FG_Stock=("Qty Available","sum"), Shelf_Life=("Shelf Life %","mean")
        ).reset_index()
        fg_agg.columns = ["Item SKU","CFA Warehouse","Item Name","Category","FG Stock","Shelf Life %"]
        fg_agg["Shelf Life %"] = fg_agg["Shelf Life %"].round(1)
    else:
        fg_agg = pd.DataFrame(columns=["Item SKU","CFA Warehouse","Item Name","Category","FG Stock","Shelf Life %"])

    stn_agg = pd.DataFrame(columns=["Item SKU","CFA Warehouse","STN In-Transit","STN Transfers"])
    if not df_stn.empty:
        fg_code_col = next((c for c in df_stn.columns if "fg code" in c.lower()), None) or \
                      next((c for c in df_stn.columns if "code" in c.lower() or "sku" in c.lower()), None)
        to_wh_col   = next((c for c in df_stn.columns if "to warehouse" in c.lower()), None)
        stat_col    = next((c for c in df_stn.columns if c.lower() == "status"), None)
        qty_col_stn = next((c for c in df_stn.columns if c.lower() == "qty"), None)
        if fg_code_col and to_wh_col and stat_col and qty_col_stn:
            stn_filt = df_stn[
                df_stn[to_wh_col].astype(str).apply(is_cfa) &
                df_stn[stat_col].astype(str).str.strip().str.lower().isin(STN_OPEN_STATUSES)
            ].copy()
            if sel_cfa2 != "All CFAs": stn_filt = stn_filt[stn_filt[to_wh_col].astype(str) == sel_cfa2]
            if search: stn_filt = stn_filt[stn_filt.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
            if not stn_filt.empty:
                stn_filt["_sku"] = stn_filt[fg_code_col].astype(str).str.strip()
                stn_filt["_wh"]  = stn_filt[to_wh_col].astype(str).str.strip()
                stn_agg = stn_filt.groupby(["_sku","_wh"]).agg(
                    STN_In_Transit=(qty_col_stn,"sum"), STN_Transfers=(qty_col_stn,"count")
                ).reset_index()
                stn_agg.columns = ["Item SKU","CFA Warehouse","STN In-Transit","STN Transfers"]

    so_agg = pd.DataFrame(columns=["Item SKU","CFA Warehouse","Open PO Qty","Open Orders"])
    if not df_sos.empty and "SO Status" in df_sos.columns:
        sku_col_so  = next((c for c in df_sos.columns if "product sku" in c.lower()), None)
        wh_col_so   = next((c for c in df_sos.columns if c.lower() == "warehouse"), None)
        qty_col_so  = next((c for c in df_sos.columns if "order qty" in c.lower()), None)
        val_col_so  = next((c for c in df_sos.columns if "total amount" in c.lower()), None)
        if sku_col_so and wh_col_so and qty_col_so:
            sos_open = df_sos[~df_sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES)].copy()
            sos_open = sos_open[sos_open[wh_col_so].astype(str).apply(is_cfa)]
            if sel_cfa2 != "All CFAs": sos_open = sos_open[sos_open[wh_col_so].astype(str) == sel_cfa2]
            if search: sos_open = sos_open[sos_open.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
            if not sos_open.empty:
                sos_open["_sku"] = sos_open[sku_col_so].astype(str).str.strip()
                sos_open["_wh"]  = sos_open[wh_col_so].astype(str).str.strip()
                agg_dict = {"Open PO Qty": (qty_col_so,"sum"), "Open Orders": (qty_col_so,"count")}
                if val_col_so: agg_dict["Open PO Value (₹)"] = (val_col_so,"sum")
                so_agg = sos_open.groupby(["_sku","_wh"]).agg(**agg_dict).reset_index()
                so_agg.columns = ["Item SKU","CFA Warehouse"] + list(agg_dict.keys())

    merged = fg_agg.copy() if not fg_agg.empty else pd.DataFrame(
        columns=["Item SKU","CFA Warehouse","Item Name","Category","FG Stock","Shelf Life %"]
    )
    if not stn_agg.empty:
        merged = merged.merge(stn_agg, on=["Item SKU","CFA Warehouse"], how="outer")
    else:
        merged["STN In-Transit"] = 0
        merged["STN Transfers"]  = 0

    if not so_agg.empty:
        merged = merged.merge(so_agg, on=["Item SKU","CFA Warehouse"], how="outer")
    else:
        merged["Open PO Qty"] = 0
        merged["Open Orders"] = 0

    if merged.empty:
        st.warning("⚠️ No CFA data found.")
    else:
        merged["FG Stock"]       = merged["FG Stock"].fillna(0)
        merged["STN In-Transit"] = merged["STN In-Transit"].fillna(0)
        merged["STN Transfers"]  = merged["STN Transfers"].fillna(0).astype(int)
        merged["Open PO Qty"]    = merged["Open PO Qty"].fillna(0)
        merged["Open Orders"]    = merged["Open Orders"].fillna(0).astype(int)
        merged["Shelf Life %"]   = merged["Shelf Life %"].fillna(0.0).round(1)
        if "Open PO Value (₹)" in merged.columns:
            merged["Open PO Value (₹)"] = merged["Open PO Value (₹)"].fillna(0)
        merged = merged[merged["CFA Warehouse"].astype(str).apply(is_cfa)]

        # KEY: Total Available changes based on mode
        if include_stn:
            merged["Total Available"] = merged["FG Stock"] + merged["STN In-Transit"]
        else:
            merged["Total Available"] = merged["FG Stock"]

        merged["Diff"] = merged["Total Available"] - merged["Open PO Qty"]

        fg_name_map = df_fg.drop_duplicates("Item SKU").set_index("Item SKU")[["Item Name","Category"]].to_dict("index") \
            if "Item SKU" in df_fg.columns else {}
        def fill_name(row):
            if pd.isna(row.get("Item Name")) or str(row.get("Item Name","")) == "":
                info = fg_name_map.get(str(row["Item SKU"]).strip(), {})
                row["Item Name"] = info.get("Item Name", row["Item SKU"])
                row["Category"]  = info.get("Category", "")
            return row
        merged = merged.apply(fill_name, axis=1)
        merged = merged.sort_values("Diff", ascending=True)

        t_fg   = merged["FG Stock"].sum()
        t_stn  = merged["STN In-Transit"].sum()
        t_po   = merged["Open PO Qty"].sum()
        t_diff = merged["Diff"].sum()

        # ── Fill Rate Calculation (respects STN mode) ─────────────────────────
        today_ts = pd.Timestamp(datetime.today().date())
        fill_rows = []
        for cfa_wh in sorted(merged["CFA Warehouse"].dropna().astype(str).unique()):
            cfa_m    = merged[merged["CFA Warehouse"] == cfa_wh]
            total_po = cfa_m["Open PO Qty"].sum()
            fulfillable = cfa_m.apply(lambda r: min(r["Total Available"], r["Open PO Qty"]), axis=1).sum()
            fill_pct = min((fulfillable / total_po * 100) if total_po > 0 else 100.0, 100.0)
            fill_rows.append({
                "CFA": cfa_wh,
                "Fill Rate %": round(fill_pct, 1),
                "Total Available": cfa_m["Total Available"].sum(),
                "Open PO Qty": total_po,
                "Shortfall SKUs": int((cfa_m["Diff"] < 0).sum())
            })
        fill_df = pd.DataFrame(fill_rows).sort_values("Fill Rate %", ascending=True) if fill_rows else pd.DataFrame()

        expiry_rows = []
        if not df_cfa.empty and "Expiry Date" in df_cfa.columns:
            exp_data = df_cfa[["Warehouse","Qty Available","Expiry Date"]].copy()
            exp_data["Expiry Date"]  = pd.to_datetime(exp_data["Expiry Date"], errors="coerce")
            exp_data["days_to_exp"]  = (exp_data["Expiry Date"] - today_ts).dt.days
            for cfa_wh in sorted(exp_data["Warehouse"].dropna().astype(str).unique()):
                cfa_e = exp_data[exp_data["Warehouse"] == cfa_wh]
                expiry_rows.append({
                    "CFA":        cfa_wh,
                    "Expired":    cfa_e[cfa_e["days_to_exp"] < 0]["Qty Available"].sum(),
                    "< 30 days":  cfa_e[cfa_e["days_to_exp"].between(0,30,  inclusive="both")]["Qty Available"].sum(),
                    "31–60 days": cfa_e[cfa_e["days_to_exp"].between(31,60, inclusive="both")]["Qty Available"].sum(),
                    "61–90 days": cfa_e[cfa_e["days_to_exp"].between(61,90, inclusive="both")]["Qty Available"].sum(),
                    "> 90 days":  cfa_e[cfa_e["days_to_exp"] > 90]["Qty Available"].sum(),
                })
        expiry_df = pd.DataFrame(expiry_rows) if expiry_rows else pd.DataFrame()

        # ── Layout: Fill Rate | Expiry Heatmap ────────────────────────────────
        col_fill, col_exp = st.columns([1, 1.7], gap="medium")

        with col_fill:
            st.markdown(f"""
            <div class="sap-section-bar">
                <span class="sap-title">📊 Fill Rate by CFA</span>
                <span class="sap-badge">Mode: {'FG+STN' if include_stn else 'FG Only'}</span>
            </div>
            """, unsafe_allow_html=True)

            if fill_df.empty:
                st.info("No open PO data for CFA warehouses.")
            else:
                fill_html = '<div class="sap-fill-panel">'
                fill_html += '<div class="sap-fill-panel-title">CFA Warehouse Fill Rates</div>'
                for _, fr in fill_df.iterrows():
                    pct   = float(fr["Fill Rate %"])
                    avl   = float(fr["Total Available"])
                    po    = float(fr["Open PO Qty"])
                    short = int(fr["Shortfall SKUs"])
                    if pct >= 90:
                        bar_c = "#1e8a3f"; pct_c = "#1a6b35"; chip_cls = "ok"
                        chip_lbl = f"✔ {pct:.1f}%"
                    elif pct >= 60:
                        bar_c = "#e07b00"; pct_c = "#a05800"; chip_cls = "warn"
                        chip_lbl = f"⚠ {pct:.1f}%"
                    else:
                        bar_c = "#bb3322"; pct_c = "#9a1f1f"; chip_cls = "critical"
                        chip_lbl = f"✖ {pct:.1f}%"
                    short_html = f'<span class="sap-chip critical">{short} short</span>' if short > 0 else ""
                    fill_html += f"""
                    <div class="sap-fill-row">
                        <div class="sap-fill-cfa-name" title="{fr['CFA']}">{fr['CFA']}</div>
                        <div>
                            <div class="sap-fill-bar-wrap">
                                <div class="sap-fill-bar-inner" style="width:{min(pct,100):.1f}%;background:{bar_c};"></div>
                            </div>
                        </div>
                        <div class="sap-fill-pct" style="color:{pct_c};">{chip_lbl}</div>
                        <div class="sap-fill-avail">Avail: {avl:,.0f}</div>
                        <div class="sap-fill-short">PO: {po:,.0f}&nbsp;{short_html}</div>
                    </div>
                    """
                fill_html += '</div>'
                st.markdown(fill_html, unsafe_allow_html=True)

        with col_exp:
            st.markdown("""
            <div class="sap-section-bar">
                <span class="sap-title">🔥 Expiry Heatmap by CFA</span>
                <span class="sap-badge">Qty by Window</span>
            </div>
            """, unsafe_allow_html=True)

            if expiry_df.empty:
                st.info("No expiry data.")
            else:
                buckets  = ["Expired", "< 30 days", "31–60 days", "61–90 days", "> 90 days"]
                bkt_cols = ["#9a1f1f", "#bb3322", "#a05800", "#7a6000", "#1e7a38"]
                bkt_bg   = [
                    ("rgba(187,51,34,{:.2f})", "#fde8e8"),
                    ("rgba(187,51,34,{:.2f})", "#fff0ee"),
                    ("rgba(224,123,0,{:.2f})",  "#fff6e8"),
                    ("rgba(200,160,0,{:.2f})",  "#fffbe8"),
                    ("rgba(30,138,63,{:.2f})",  "#edfaef"),
                ]
                max_vals = {b: max(expiry_df[b].max(), 1) for b in buckets}

                hm_html = '<div class="sap-heatmap-wrap"><div class="sap-hm-header">'
                hm_html += '<div class="sap-hm-header-cell">CFA</div>'
                for b in buckets:
                    hm_html += f'<div class="sap-hm-header-cell">{b}</div>'
                hm_html += '</div>'

                for _, er in expiry_df.sort_values("< 30 days", ascending=False).iterrows():
                    hm_html += '<div class="sap-hm-row">'
                    hm_html += f'<div class="sap-hm-cell">{er["CFA"]}</div>'
                    for b, bc, (bg_fmt, _fallback) in zip(buckets, bkt_cols, bkt_bg):
                        val       = float(er[b])
                        intensity = val / max_vals[b] if max_vals[b] > 0 else 0
                        alpha     = min(0.15 + intensity * 0.75, 0.90)
                        cell_bg   = bg_fmt.format(alpha) if val > 0 else "transparent"
                        val_str   = f"{val:,.0f}" if val > 0 else "—"
                        text_c    = bc if val > 0 else "#c8d3e0"
                        hm_html  += f'<div class="sap-hm-cell" style="background:{cell_bg};color:{text_c};font-weight:{"700" if val>0 else "400"};">{val_str}</div>'
                    hm_html += '</div>'

                hm_html += '<div class="sap-hm-total-row">'
                hm_html += '<div class="sap-hm-total-cell">TOTAL</div>'
                for b, bc in zip(buckets, bkt_cols):
                    hm_html += f'<div class="sap-hm-total-cell" style="color:{bc};">{expiry_df[b].sum():,.0f}</div>'
                hm_html += '</div></div>'
                st.markdown(hm_html, unsafe_allow_html=True)

        st.markdown('<hr style="border:none;border-top:1px solid #c8d3e0;margin:16px 0;">', unsafe_allow_html=True)

        # ── Fill Rate mapped back to merged ───────────────────────────────────
        if not fill_df.empty:
            fill_rate_map = dict(zip(fill_df["CFA"], fill_df["Fill Rate %"]))
            merged["Fill Rate %"] = merged["CFA Warehouse"].map(fill_rate_map).fillna(0.0)
        else:
            merged["Fill Rate %"] = 0.0

        # ── Batch lookup ──────────────────────────────────────────────────────
        batch_lookup = {}
        if not df_cfa.empty and "Item SKU" in df_cfa.columns:
            for (sku, wh), grp in df_cfa.groupby(["Item SKU","Warehouse"]):
                batches = []
                for _, r in grp.iterrows():
                    exp = r.get("Expiry Date", None)
                    batches.append({
                        "Batch No":    str(r.get("Batch No","—")) if "Batch No" in r.index else "—",
                        "Qty":         float(r.get("Qty Available", 0)),
                        "Shelf Life %": round(float(r.get("Shelf Life %", 0)), 1),
                        "Expiry Date": exp.strftime("%d-%b-%Y") if pd.notna(exp) else "—",
                    })
                batch_lookup[(str(sku).strip(), str(wh).strip())] = batches

        def shelf_label(row):
            key = (str(row["Item SKU"]).strip(), str(row["CFA Warehouse"]).strip())
            n   = len(batch_lookup.get(key, []))
            avg = row.get("Shelf Life %", 0)
            return f"{avg:.1f}%  ·  {n} batch{'es' if n>1 else ''}" if n else f"{avg:.1f}%"
        merged["Shelf Life"] = merged.apply(shelf_label, axis=1)

        disp_cols = ["Item Name","Item SKU","Category","CFA Warehouse","FG Stock",
                     "STN In-Transit","STN Transfers","Shelf Life","Fill Rate %",
                     "Open PO Qty","Open Orders","Total Available","Diff"]
        if "Open PO Value (₹)" in merged.columns:
            disp_cols.insert(disp_cols.index("Diff"), "Open PO Value (₹)")
        disp_cols = [c for c in disp_cols if c in merged.columns]
        df_disp   = merged[disp_cols].copy()

        # ── Batch Panel ───────────────────────────────────────────────────────
        if "batch_sel_tab2" not in st.session_state:
            st.session_state["batch_sel_tab2"] = None
        sel_key    = st.session_state.get("batch_sel_tab2")
        lookup_key = (sel_key[0], sel_key[2]) if sel_key and len(sel_key) == 3 else None
        batches_show = batch_lookup.get(lookup_key, []) if lookup_key else []

        st.markdown(f"""
        <div class="sap-section-bar">
            <span class="sap-title">📦 SKU · CFA Availability Detail</span>
            <span class="sap-badge">{len(df_disp):,} SKUs  ·  Mode: {'FG+STN' if include_stn else 'FG Only'}</span>
        </div>
        """, unsafe_allow_html=True)

        if sel_key and batches_show:
            batch_df  = pd.DataFrame(batches_show).sort_values("Shelf Life %", ascending=True)
            wh_label  = sel_key[2] if len(sel_key) > 2 else ""
            sku_label = sel_key[0]
            batch_rows_html = ""
            for _, b in batch_df.iterrows():
                pct   = float(b["Shelf Life %"])
                bar_w = max(2, int(pct))
                if pct > 60:   bar_c = "#1e8a3f"; txt_c = "#1a6b35"
                elif pct > 30: bar_c = "#e07b00"; txt_c = "#a05800"
                else:          bar_c = "#bb3322"; txt_c = "#9a1f1f"
                batch_rows_html += f"""
                <div class="sap-batch-row">
                    <span style="min-width:130px;color:#3a4a5a;font-family:'IBM Plex Mono',monospace;font-size:11px;">{b['Batch No']}</span>
                    <div style="flex:1;background:#e8edf4;border-radius:2px;height:10px;max-width:260px;">
                        <div style="width:{bar_w}%;background:{bar_c};height:10px;border-radius:2px;"></div>
                    </div>
                    <span style="min-width:52px;text-align:right;color:{txt_c};font-weight:700;font-family:'IBM Plex Mono',monospace;font-size:11px;">{pct:.1f}%</span>
                    <span style="min-width:90px;text-align:right;color:#6b7c93;font-family:'IBM Plex Mono',monospace;font-size:11px;">{b['Qty']:,.0f} units</span>
                    <span style="min-width:100px;color:#8a9bb0;font-size:11px;">Exp: {b['Expiry Date']}</span>
                </div>"""
            st.markdown(f"""
            <div class="sap-detail-panel">
                <div class="dp-title">📋 Batch Shelf Life — {wh_label} &nbsp;/&nbsp; <span style="font-family:'IBM Plex Mono',monospace;">{sku_label}</span>
                    &nbsp;<span style="background:#e6f0ff;color:#0050b3;border:1px solid #a0c0f0;padding:2px 8px;border-radius:2px;font-size:10px;">{len(batch_df)} batches</span>
                </div>
                {batch_rows_html}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#f8fafd;border:1px dashed #c8d3e0;border-radius:3px;
                        padding:12px 18px;margin-bottom:12px;text-align:center;
                        color:#8a9bb0;font-size:11px;font-family:'IBM Plex Sans',sans-serif;">
                ↕ Select a row in the table below to view batch-level shelf life &amp; expiry breakdown
            </div>
            """, unsafe_allow_html=True)

        # ── Export + Table ────────────────────────────────────────────────────
        df_export = merged[[
            "Item Name","Item SKU","Category","CFA Warehouse","FG Stock",
            "STN In-Transit","STN Transfers","Shelf Life %","Fill Rate %",
            "Open PO Qty","Open Orders","Total Available","Diff"
        ] + (["Open PO Value (₹)"] if "Open PO Value (₹)" in merged.columns else [])].copy()
        buf2 = io.BytesIO()
        with pd.ExcelWriter(buf2, engine="openpyxl") as w:
            df_export.to_excel(w, index=False, sheet_name="CFA Analysis")

        hc1, hc2 = st.columns([3, 1])
        with hc2:
            st.download_button(
                "⬇  Export Excel", buf2.getvalue(),
                "CFA_Stock_Analysis.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        def colour_row_sap(row):
            d = row.get("Diff", 0)
            if pd.isna(d): return [""] * len(row)
            if d < 0:      return ["background-color:#fdecea; color:#7a1a1a"] * len(row)
            tot = row.get("Total Available", 1)
            if tot > 0 and d / max(tot, 1) < 0.15:
                return ["background-color:#fff8ec; color:#6a3a00"] * len(row)
            return ["background-color:#f0fbf4; color:#0f4a22"] * len(row)

        col_cfg = {
            "FG Stock":       st.column_config.NumberColumn("FG Stock",        format="%.0f"),
            "STN In-Transit": st.column_config.NumberColumn("STN In-Transit 🚚", format="%.0f",
                              help="Included in Total Available only when mode = 'With STN In-Transit'"),
            "STN Transfers":  st.column_config.NumberColumn("# STNs",          format="%d"),
            "Shelf Life":     st.column_config.TextColumn("Shelf Life 📦",     help="avg · N batches"),
            "Fill Rate %":    st.column_config.ProgressColumn("Fill Rate % 🎯", min_value=0, max_value=100, format="%.1f%%"),
            "Open PO Qty":    st.column_config.NumberColumn("Open PO Qty",     format="%.0f"),
            "Open Orders":    st.column_config.NumberColumn("# Orders",         format="%d"),
            "Total Available":st.column_config.NumberColumn("Total Available",  format="%.0f",
                              help="FG + STN (if mode = With STN) or FG only"),
            "Diff":           st.column_config.NumberColumn("Diff ✅",          format="%.0f"),
        }
        if "Open PO Value (₹)" in df_disp.columns:
            col_cfg["Open PO Value (₹)"] = st.column_config.NumberColumn("PO Value (₹)", format="%.0f")

        event = st.dataframe(
            df_disp.style.apply(colour_row_sap, axis=1),
            use_container_width=True, height=480,
            hide_index=False, column_config=col_cfg,
            on_select="rerun", selection_mode="single-row",
            key="cfa_table"
        )
        selected_rows = event.selection.get("rows", []) if hasattr(event, "selection") else []
        if selected_rows:
            r = df_disp.iloc[selected_rows[0]]
            new_key = (
                str(r["Item SKU"]).strip(),
                str(r.get("Item Name","")).strip(),
                str(r["CFA Warehouse"]).strip()
            )
            if st.session_state.get("batch_sel_tab2") != new_key:
                st.session_state["batch_sel_tab2"] = new_key
                st.rerun()

        # ── CFA Breakdown Expanders ───────────────────────────────────────────
        st.markdown(f"""
        <div class="sap-section-bar" style="margin-top:18px;">
            <span class="sap-title">🏭 Breakdown by CFA Warehouse</span>
            <span class="sap-badge">Expand to drill down</span>
        </div>
        """, unsafe_allow_html=True)
        for cfa_wh in sorted(df_disp["CFA Warehouse"].dropna().astype(str).unique()):
            cfa_data = df_disp[df_disp["CFA Warehouse"] == cfa_wh]
            c_fg   = cfa_data["FG Stock"].sum()
            c_stn  = cfa_data["STN In-Transit"].sum()
            c_po   = cfa_data["Open PO Qty"].sum()
            c_diff = cfa_data["Diff"].sum()
            c_short = int((cfa_data["Diff"] < 0).sum())
            stn_part = f"  +STN {c_stn:,.0f}" if include_stn else ""
            label = (f"🏭  {cfa_wh}   ·   FG {c_fg:,.0f}{stn_part}  −  PO {c_po:,.0f}  =  Diff {c_diff:+,.0f}"
                     f"   {'⚠ ' + str(c_short) + ' shortfall' if c_short else '✔ Healthy'}")
            with st.expander(label, expanded=False):
                st.dataframe(
                    cfa_data.style.apply(colour_row_sap, axis=1),
                    use_container_width=True,
                    height=min(60 + len(cfa_data) * 36, 420),
                    hide_index=True, column_config=col_cfg
                )

        # ── Telegram ─────────────────────────────────────────────────────────
        st.markdown("""
        <div class="sap-section-bar" style="margin-top:18px;">
            <span class="sap-title">📬 Send CFA Report to Telegram</span>
        </div>
        """, unsafe_allow_html=True)
        _tok = st.session_state.get("tg_token", "")
        _cid = st.session_state.get("tg_chat_id", "")
        if not _tok or not _cid:
            st.warning("⚠️ Enter Bot Token and Chat ID in the sidebar to enable Telegram sending.")
        else:
            if st.button("📬  Send CFA Shortfall Report to Telegram", use_container_width=True, key="tg_cfa_btn"):
                _central = {}
                if not df_fg.empty and "Warehouse" in df_fg.columns:
                    _c_rows = df_fg[df_fg["Warehouse"].astype(str).str.strip() == "Central"].copy()
                    if not _c_rows.empty:
                        _central = _c_rows.groupby("Item SKU")["Qty Available"].sum().to_dict()
                _msg = build_cfa_telegram(merged, _central)
                _ok, _err = _tg_send(_tok, _cid, _msg)
                if _ok: st.success("✅ CFA Shortfall report sent to Telegram!")
                else:   st.error(f"❌ Failed to send: {_err}")
