import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="MAYA v48.9 - High Visibility Engine", layout="wide")

# Custom CSS for Solid UI
st.markdown("""
    <style>
    .live-res { background: #1e293b; color: #fbbf24; padding: 10px; border-radius: 10px; text-align: center; border: 2px solid #fbbf24; }
    .universal-box { background: #0f172a; color: #38bdf8; padding: 15px; border-radius: 12px; text-align: center; border: 2px solid #38bdf8; font-weight: bold; font-size: 18px; margin-bottom: 20px; }
    .summary-bar { background: #f8fafc; padding: 12px; border-radius: 8px; border-left: 5px solid #ef4444; margin: 15px 0; font-weight: bold; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v48.9 (Strict Error Bypass & Bold Layout)")

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

# --- DASHBOARD CONTROL ---
uploaded_file = st.file_uploader("📂 Upload Excel Data Sheet", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    all_dates = df['DATE'].astype(str).unique().tolist()
    sel_date = st.selectbox("📅 Date:", options=all_dates[::-1])
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    
    shifts_list = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    
    # Execute Matrix Calculations
    remaining_target_pool, universal_blocked_pool = calculate_inverse_universe(df, idx, shifts_list)
    
    # Bold Strings for UI Enhancement
    bold_date = f"**{sel_date}**"
    bold_total_universe = f"**100**"
    bold_overlaps_count = f"**{len(universal_blocked_pool)}**"
    bold_active_pool_count = f"**{len(remaining_target_pool)}**"
    
    # --- TOP INTERFACE DISPLAY PANEL ---
    st.markdown(f"""
    <div class="universal-box">
         🛡️ INVERSE UNIVERSAL FILTER MODE: Selected Date ({bold_date})<br>
         Total Universe ({bold_total_universe}) - Universal Overlaps ({bold_overlaps_count}) = Active Prediction Pool ({bold_active_pool_count} Jodis Remaining)
    </div>
    """, unsafe_allow_html=True)
    
    # Formatting Jodis with Bold tag for crystal clear view
    bold_blocked_jodis = ", ".join([f"**{nj}**" for nj in universal_blocked_pool]) if universal_blocked_pool else "**No Blocked Numbers**"
    bold_remaining_jodis = ", ".join([f"**{nj}**" for nj in remaining_target_pool])
    
    st.markdown(f'<div class="summary-bar">🚫 Blocked Universal Jodis ({bold_overlaps_count}):</div>', unsafe_allow_html=True)
    st.write(bold_blocked_jodis, unsafe_allow_html=True)
    
    st.markdown(f'<div class="summary-bar" style="border-left-color: #10b981;">🎯 Active Target Remaining Jodis ({bold_active_pool_count}):</div>', unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:18px; letter-spacing:1px;'>{bold_remaining_jodis}</div>", unsafe_allow_html=True)

    # --- THE COMPREHENSIVE BACKTEST TABLE (WITH COMPLETE BYPASS FIX) ---
    st.divider()
    st.subheader("📜 10-Day Strict Inverse Universal Validation Backtest")
    st.caption("Yeh table track karti hai ki un remaining jodis ke pool me se usi same day par kaun-kaun si shifts safalta purvak pass hoke nikli hain.")
    
    hist = []
    for i in range(max(0, idx - 10), idx + 1):
        row_remaining_pool, _ = calculate_inverse_universe(df, i, shifts_list)
        
        # Dictionary structure tracking map based shift alignment
        passed_shifts_map = {s: "**❌**" for s in shifts_list}
        total_passed_count = 0
        
        # Cross checking all 6 shifts securely (Error Redundancy Proof)
        for s in shifts_list:
            if s in df.columns:
                actual_val = str(df.iloc[i].get(s, "XX")).split('.')[0]
                if actual_val.isdigit():
                    av_pad = str(int(actual_val)).zfill(2)
                    if av_pad in row_remaining_pool:
                        passed_shifts_map[s] = f"**🟢 {s} ({av_pad})**"
                        total_passed_count += 1
                    else:
                        passed_shifts_map[s] = f"**❌ {s}**"
            else:
                passed_shifts_map[s] = f"**⚠️ Missing Col**"
                    
        hist.append({
            "History Date": f"**{df.iloc[i]['DATE']}**",
            "Pool Count": f"**{len(row_remaining_pool)}**",
            "DS Status": passed_shifts_map['DS'],
            "FB Status": passed_shifts_map['FB'],
            "GB Status": passed_shifts_map['GB'],
            "GL Status": passed_shifts_map['GL'],
            "DB Status": passed_shifts_map['DB'],
            "SG Status": passed_shifts_map['SG'],
            "Total Shifts Passed": f"**{total_passed_count} / 6 Shifts**"
        })
        
    # Generating clean Streamlit table structure safely mapped
    df_hist = pd.DataFrame(hist)
    st.write(df_hist.to_html(escape=False, index=False), unsafe_allow_html=True)
    
