import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="MAYA v49.9 - 45 Day Deep Engine", layout="wide")

# --- 32 PATTERNS ENGINE ---
def generate_32_patterns(base_val):
    if not str(base_val).isdigit():
        return set()
    val = int(base_val)
    a, b = val // 10, val % 10
    patterns = set()
    
    shifts = [
        (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1),
        (2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (-2, -2), (2, -2), (-2, 2),
        (5, 0), (0, 5), (5, 5), (5, 1), (1, 5), (5, -1), (-1, 5),
        (5, 2), (2, 5), (5, -2), (-2, 5), (3, 0), (0, 3), (3, 3), (-3, -3), (0, 0)
    ]
    for sa, sb in shifts:
        patterns.add(f"{(a + sa) % 10}{(b + sb) % 10}")
    return patterns

# --- WORST GAPS SCANNER (STRICT PAST LOCK) ---
def find_worst_gaps_90(df, idx, col):
    gap_scores = {}
    for g in range(1, 91):
        if (idx - 1) - g - 10 < 0: continue
        score = 0
        for check in range(idx - 11, idx):
            if check - g < 0 or check == idx: continue
            pred = str(df.iloc[check-g].get(col, "XX")).split('.')[0]
            act = str(df.iloc[check].get(col, "XX")).split('.')[0]
            if pred.isdigit() and act.isdigit() and pred == act:
                score += 1 
        gap_scores[g] = score
    
    worst_gaps = sorted(gap_scores, key=gap_scores.get)[:5]
    bad_andar, bad_bahar = [], []
    for wg in worst_gaps:
        if (idx - 1) - wg >= 0:
            val = str(df.iloc[(idx - 1) - wg].get(col, 0)).split('.')[0]
            if val.isdigit():
                bad_andar.append(int(val)//10)
                bad_bahar.append(int(val)%10)
            
    final_a = max(set(bad_andar), key=bad_andar.count) if bad_andar else 0
    final_b = max(set(bad_bahar), key=bad_bahar.count) if bad_bahar else 5
    return final_a, final_b, worst_gaps

# --- ADVANCED LOGIC WITH STRICT BOUNDARY LOCK ---
def calculate_v48_logic(df, idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    val = 0
    for i in range(1, 15):
        if idx - i >= 0:
            raw = df.iloc[idx-i].get(base_col, 0)
            if str(raw).isdigit() and int(raw) > 0:
                val = int(raw)
                break
                
    d1, d2 = val // 10, val % 10
    pa = (d1 + 1) % 10 if d1 != d2 else (d1 + 5) % 10
    pb = (d2 + 1) % 10
    ra, rb = (pa + 5) % 10, (pb + 5) % 10
    
    blocked_64 = set()
    for a in {pa, ra}:
        for i in range(10): blocked_64.add(f"{a}{i}")
    for b in {pb, rb}:
        for i in range(10): blocked_64.add(f"{i}{b}")
    
    target_36 = [str(i).zfill(2) for i in range(100) if str(i).zfill(2) not in blocked_64]
    wa, wb, _ = find_worst_gaps_90(df, idx, base_col)
    
    extra_hatao = set()
    for i in range(10):
        extra_hatao.add(f"{wa}{i}")
        extra_hatao.add(f"{i}{wb}")
        
    v48_stable = [j for j in target_36 if j not in extra_hatao]
    
    prev_actual_val = str(df.iloc[idx - 1].get(base_col, 0)).split('.')[0] if (idx - 1) >= 0 else "0"
    p32_set = generate_32_patterns(prev_actual_val)
    
    common_numbers = [n for n in v48_stable if n in p32_set]
    uniq_v48 = [n for n in v48_stable if n not in p32_set]
    uniq_p32 = [n for n in p32_set if n not in v48_stable]
    
    return {"common": common_numbers, "uniq_v48": uniq_v48, "uniq_p32": uniq_p32}

# --- PROCESS CORE INVERSE MATRIX ---
def calculate_inverse_universe(df, idx, shifts_list):
    all_num_freq = {}
    for s in shifts_list:
        res_shift = calculate_v48_logic(df, idx, s)
        for n in res_shift['common']: all_num_freq[n] = all_num_freq.get(n, 0) + 1
        for n in res_shift['uniq_v48']: all_num_freq[n] = all_num_freq.get(n, 0) + 1
        for n in res_shift['uniq_p32']: all_num_freq[n] = all_num_freq.get(n, 0) + 1

    universal_commons = [k for k, v in all_num_freq.items() if v >= 4]
    full_universe = [str(x).zfill(2) for x in range(100)]
    remaining_pool = sorted([num for num in full_universe if num not in universal_commons])
    
    return remaining_pool, sorted(universal_commons)

# --- 4-TIER REMAINING POOL EXTRACTION ---
def calculate_4_tiers_from_pool(pool, df, idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    prev_val = str(df.iloc[idx-1].get(base_col, 0)).split('.')[0] if idx-1 >=0 else "0"
    p_num = int(prev_val) if prev_val.isdigit() else 0
    lead_digit = str(p_num // 10)
    end_digit = str(p_num % 10)
    
    t16 = [num for num in pool if num.startswith(lead_digit) or num.endswith(end_digit)]
    if len(t16) < 16:
        fillers = [x for x in pool if x not in t16]
        t16.extend(fillers[:16 - len(t16)])
    t16 = sorted(t16[:16])
    
    t9 = [n for n in t16 if (int(n)//10 + int(n)%10) % 2 == 0]
    if len(t9) < 9:
        fillers = [x for x in t16 if x not in t9]
        t9.extend(fillers[:9 - len(t9)])
    t9 = sorted(t9[:9])
    
    t5 = [n for n in t9 if (int(n) % 5 == 0 or int(n) % 3 == 0)]
    if len(t5) < 5:
        fillers = [x for x in t9 if x not in t5]
        t5.extend(fillers[:5 - len(t5)])
    t5 = sorted(t5[:5])
    
    t1 = [t5[0]] if t5 else ["00"]
    return t16, t9, t5, t1

# --- 4-TIER BLOCKED POOL EXTRACTION ---
def calculate_blocked_pool_tiers(blocked_pool, df, idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    prev_val = str(df.iloc[idx-1].get(base_col, 0)).split('.')[0] if idx-1 >= 0 else "0"
    p_num = int(prev_val) if prev_val.isdigit() else 0
    a_dig, b_dig = str(p_num // 10), str(p_num % 10)
    
    b25 = [num for num in blocked_pool if (num.startswith(a_dig) or num.endswith(b_dig) or 
                                           num.startswith(str((int(a_dig)+5)%10)) or num.endswith(str((int(b_dig)+5)%10)))]
    if len(b25) < 25:
        fillers = [x for x in blocked_pool if x not in b25]
        b25.extend(fillers[:25 - len(b25)])
    b25 = sorted(b25[:25])
    
    b16 = [n for n in b25 if (int(n) % 2 == 0 or int(n) % 3 == 0)]
    if len(b16) < 16:
        fillers = [x for x in b25 if x not in b16]
        b16.extend(fillers[:16 - len(b16)])
    b16 = sorted(b16[:16])
    
    b9 = [n for n in b16 if (int(n)//10 + int(n)%10) % 2 != 0]
    if len(b9) < 9:
        fillers = [x for x in b16 if x not in b9]
        b9.extend(fillers[:9 - len(b9)])
    b9 = sorted(b9[:9])
    
    b1 = [b9[0]] if b9 else ["00"]
    return b25, b16, b9, b1

# --- DASHBOARD CONTROL ---
uploaded_file = st.file_uploader("📂 Upload Excel Data Sheet", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    all_dates = df['DATE'].astype(str).unique().tolist()
    
    # Sidebar controllers
    st.sidebar.header("🎛️ Layout Controllers")
    box_size = st.sidebar.slider("Chakor Box Size (Font Size)", min_value=14, max_value=36, value=22)
    grid_columns_count = st.sidebar.slider("Grid Columns Count", min_value=4, max_value=12, value=10)
    
    st.markdown(f"""
        <style>
        .live-res {{ background: #1e293b; color: #fbbf24; padding: 10px; border-radius: 10px; text-align: center; border: 2px solid #fbbf24; }}
        .universal-box {{ background: #0f172a; color: #38bdf8; padding: 15px; border-radius: 12px; text-align: center; border: 2px solid #38bdf8; font-weight: bold; font-size: 20px; margin-bottom: 20px; }}
        .summary-bar {{ background: #f8fafc; padding: 12px; border-radius: 8px; border-left: 5px solid #ef4444; margin: 15px 0; font-weight: bold; font-size: 18px; color: #1e293b; }}
        
        .grid-square-dynamic {{ display: grid; grid-template-columns: repeat({grid_columns_count}, 1fr); gap: 10px; width: 100%; margin: 15px 0; }}
        .chakor-item-remaining {{ background: #dcfce7; color: #15803d; padding: 12px; border-radius: 8px; font-size: {box_size}px; font-weight: bold; text-align: center; border: 2px solid #bbf7d0; }}
        .chakor-item-blocked {{ background: #fee2e2; color: #b91c1c; padding: 12px; border-radius: 8px; font-size: {box_size}px; font-weight: bold; text-align: center; border: 2px solid #fecaca; }}
        </style>
        """, unsafe_allow_html=True)

    sel_date = st.selectbox("📅 Date Selection:", options=all_dates[::-1])
    target_s = st.selectbox("🎰 Target Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    shifts_list = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    
    # Run base calculations
    remaining_target_pool, universal_blocked_pool = calculate_inverse_universe(df, idx, shifts_list)
    r16, r9, r5, r1 = calculate_4_tiers_from_pool(remaining_target_pool, df, idx, target_s)
    b25, b16, b9, b1 = calculate_blocked_pool_tiers(universal_blocked_pool, df, idx, target_s)

    # --- DROPDOWN SELECTORS BLOCK ---
    st.write("---")
    st.subheader("🎯 STRICT MATRIX FILTER CONTROLLERS")
    col_sel1, col_sel2 = st.columns(2)
    
    with col_sel1:
        e1_option = st.selectbox("🟢 Engine 1 Selection (Remaining Groups):", 
                                 options=["Stable 16", "Super Hit 9", "VVIP 5", "Single Core 1", "Full Pool (35 Jodis)"])
    with col_sel2:
        e2_option = st.selectbox("🔴 Engine 2 Selection (Blocked Groups):", 
                                 options=["Stable 25", "Stable 16", "Super Hit 9", "Single Core 1", "Full Pool (65 Jodis)"])

    e1_map = {"Full Pool (35 Jodis)": remaining_target_pool, "Stable 16": r16, "Super Hit 9": r9, "VVIP 5": r5, "Single Core 1": r1}
    e2_map = {"Full Pool (65 Jodis)": universal_blocked_pool, "Stable 25": b25, "Stable 16": b16, "Super Hit 9": b9, "Single Core 1": b1}
    
    active_e1_array = e1_map[e1_option]
    active_e2_array = e2_map[e2_option]

    # Display dynamic grids
    st.markdown(f'<div class="summary-bar" style="border-left-color: #10b981;">🟢 Active Target: {e1_option} ({len(active_e1_array)} Jodis Active)</div>', unsafe_allow_html=True)
    g_html = '<div class="grid-square-dynamic">'
    for num in active_e1_array: g_html += f'<div class="chakor-item-remaining">{num}</div>'
    st.markdown(g_html+'</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="summary-bar">🚫 Active Blocked Target: {e2_option} ({len(active_e2_array)} Jodis Active)</div>', unsafe_allow_html=True)
    g_html = '<div class="grid-square-dynamic">'
    for num in active_e2_array: g_html += f'<div class="chakor-item-blocked">{num}</div>'
    st.markdown(g_html+'</div>', unsafe_allow_html=True)

    # --- STRICT DRIVEN SYNCHRONIZED 45-DAY BACKTEST TABLE ---
    st.write("---")
    st.subheader("📜 Strict Synchronized 45-Day History Validation Backtest")
    st.caption(f"Yeh table aapke dropdown selection ke mutabik strictly piche ke **45 dino** ka deep matrix scan display karegi.")
    
    hist = []
    # Loop range strictly extended up to max 45 points backwards
    for i in range(max(0, idx - 45), idx + 1):
        row_rem, row_blk = calculate_inverse_universe(df, i, shifts_list)
        
        # Calculate dynamic historical sub-slices strictly locked inside row context
        hr16, hr9, hr5, hr1 = calculate_4_tiers_from_pool(row_rem, df, i, target_s)
        hb25, hb16, hb9, hb1 = calculate_blocked_pool_tiers(row_blk, df, i, target_s)
        
        h_e1_map = {"Full Pool (35 Jodis)": row_rem, "Stable 16": hr16, "Super Hit 9": hr9, "VVIP 5": hr5, "Single Core 1": hr1}
        h_e2_map = {"Full Pool (65 Jodis)": row_blk, "Stable 25": hb25, "Stable 16": hb16, "Super Hit 9": hb9, "Single Core 1": hb1}
        
        loop_e1_target_set = h_e1_map[e1_option]
        loop_e2_target_set = h_e2_map[e2_option]
        
        rem_passed, blk_passed = [], []
        for s in shifts_list:
            if s in df.columns:
                val = str(df.iloc[i].get(s, "XX")).split('.')[0]
                if val.isdigit():
                    v_pad = str(int(val)).zfill(2)
                    
                    # Exact dynamic alignment check matching dropdown slices
                    if v_pad in loop_e1_target_set:
                        rem_passed.append(f"<span style='color:#16a34a; font-weight:bold;'>{s}:{v_pad}</span>")
                    if v_pad in loop_e2_target_set:
                        blk_passed.append(f"<span style='color:#16a34a; font-weight:bold;'>{s}:{v_pad}</span>")
                        
        hist.append({
            "History Date": f"<b>{df.iloc[i]['DATE']}</b>",
            f"🟢 Remaining ({len(loop_e1_target_set)} Jodis) Pass": ", ".join(rem_passed) if rem_passed else "<b>None</b>",
            f"🔴 Blocked ({len(loop_e2_target_set)} Jodis) Pass": ", ".join(blk_passed) if blk_passed else "<b>None</b>"
        })
        
    df_hist = pd.DataFrame(hist)
    st.write(df_hist.to_html(escape=False, index=False), unsafe_allow_html=True)

    # --- MASTER EXPLORER UTILITY MODULE ---
    st.write("---")
    st.subheader("🔍 DATA TRANSITION EXPLORER MATRIX")
    search_num = st.text_input("Enter 2-Digit number to search inside universes (e.g. 05):", value="")
    if search_num:
        s_pad = str(search_num).zfill(2)
        in_rem = "🟢 HAAN (Remaining Pool Mein Hai)" if s_pad in remaining_target_pool else "❌ NAHI"
        in_blk = "🔴 HAAN (Blocked Overlaps Mein Hai)" if s_pad in universal_blocked_pool else "❌ NAHI"
        st.write(f"Number **{s_pad}** status for selected date:")
        st.write(f"Engine 1 Cluster: {in_rem}")
        st.write(f"Engine 2 Cluster: {in_blk}")
    
