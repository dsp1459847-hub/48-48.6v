import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="MAYA v48.8 - 18 Layer Universal Matrix", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .live-res { background: #1e293b; color: #fbbf24; padding: 10px; border-radius: 10px; text-align: center; border: 2px solid #fbbf24; }
    .universal-box { background: #0f172a; color: #10b981; padding: 15px; border-radius: 12px; text-align: center; border: 2px solid #10b981; font-weight: bold; font-size: 18px; margin-bottom: 20px; }
    .grid-square { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; max-width: 400px; margin: 10px auto; }
    .grid-item { background: #ffffff; color: #1e40af; padding: 12px; border-radius: 8px; font-size: 20px; font-weight: bold; text-align: center; border: 2px solid #bfdbfe; }
    .worst-badge { background: #fee2e2; color: #b91c1c; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin: 2px; border: 1px solid #fecaca; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v48.8 (18-Layer Universal Common Scanner)")

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
    wa, wb, wgaps = find_worst_gaps_90(df, idx, base_col)
    
    extra_hatao = set()
    for i in range(10):
        extra_hatao.add(f"{wa}{i}")
        extra_hatao.add(f"{i}{wb}")
        
    v48_stable = [j for j in target_36 if j not in extra_hatao]
    
    prev_actual_val = str(df.iloc[idx - 1].get(base_col, 0)).split('.')[0] if (idx - 1) >= 0 else "0"
    p32_set = generate_32_patterns(prev_actual_val)
    
    common_numbers = sorted(list(set([n for n in v48_stable if n in p32_set])))
    uniq_v48 = sorted(list(set([n for n in v48_stable if n not in p32_set])))
    uniq_p32 = sorted(list(set([n for n in p32_set if n not in v48_stable])))
    
    return {
        "t16": v48_stable[:16],
        "t9": v48_stable[:9],
        "common": common_numbers,
        "uniq_v48": uniq_v48,
        "uniq_p32": uniq_p32,
        "wgaps": wgaps
    }

# --- DASHBOARD CONTROL ---
uploaded_file = st.file_uploader("📂 Upload Excel Data Sheet", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    sel_date = st.selectbox("📅 Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    
    shifts_list = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    
    # --- 18-LAYER UNIVERSAL SCANNER CRUNCHING ---
    # Is block mein hum saari 6 shifts aur unke 3 tiers ka data ek sath nikaal rahe hain
    all_numbers_frequency = {}
    
    for s in shifts_list:
        res_shift = calculate_v48_logic(df, idx, s)
        
        # Jodne ke liye teeno Tiers ko combine karenge (18 layers tracking)
        for n in res_shift['common']:
            all_numbers_frequency[n] = all_numbers_frequency.get(n, 0) + 1
        for n in res_shift['uniq_v48']:
            all_numbers_frequency[n] = all_numbers_frequency.get(n, 0) + 1
        for n in res_shift['uniq_p32']:
            all_numbers_frequency[n] = all_numbers_frequency.get(n, 0) + 1

    # Filter out numbers jo shifts ke andar heavy density overlap par hain
    # High frequency check (Jaise jo numbers 4 ya usse zyada shifts ke patterns me overlap ho rhe hain)
    universal_commons = [k for k, v in all_numbers_frequency.items() if v >= 4]
    universal_commons = sorted(universal_commons)
    
    # --- DISPLAYING THE UNIVERSAL MATRIX RESULTS ---
    st.markdown(f"""
    <div class="universal-box">
         🛡️ UNIVERSAL CROSS-COMMON MATRIX: Selected Date ({sel_date}) par shifts ke overlapping se Total **{len(universal_commons)}** Jodis Filter hui hain.
    </div>
    """, unsafe_allow_html=True)
    
    if universal_commons:
        st.write("**💎 Universal High-Overlap Jodis (Minimum 4+ Shift Crossings):**")
        st.code(", ".join(universal_commons))
    else:
        st.warning("Is date par koi bhi high density universal common number nahi mila.")
        
    # --- SINGLE SHIFT DETAIL VIEW ---
    st.divider()
    st.subheader("🎰 Individual Shift Verification Panel")
    selected_view_shift = st.selectbox("Select Shift to view Tiers:", options=shifts_list)
    
    res_dict = calculate_v48_logic(df, idx, selected_view_shift)
    
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        st.info(f"💎 **{selected_view_shift} - Common Tiers**")
        st.write(res_dict['common'] if res_dict['common'] else "No Commons")
    with tc2:
        st.success(f"📦 **{selected_view_shift} - Unique V48 Gaps**")
        st.write(res_dict['uniq_v48'])
    with tc3:
        st.warning(f"🌀 **{selected_view_shift} - Unique 32-Pattern**")
        st.write(res_dict['uniq_p32'])

    # --- THE COMPREHENSIVE BACKTEST TABLE FOR UNIVERSAL TIER ---
    st.divider()
    st.subheader("📜 10-Day Universal Super-Filter Backtest Tracker")
    st.caption("Yeh table track karti hai ki un 18 layers ke cross filtration se jo universal numbers nikle, unhone aage kya hit diya.")
    
    hist = []
    for i in range(max(0, idx - 10), idx + 1):
        # Calculate universal frequency for row 'i'
        row_freq = {}
        for s in shifts_list:
            r_shift = calculate_v48_logic(df, i, s)
            for n in r_shift['common']: row_freq[n] = row_freq.get(n, 0) + 1
            for n in r_shift['uniq_v48']: row_freq[n] = row_freq.get(n, 0) + 1
            for n in r_shift['uniq_p32']: row_freq[n] = row_freq.get(n, 0) + 1
            
        row_universal = [k for k, v in row_freq.items() if v >= 4]
        
        # Check hitting across all shifts for that specific day
        hit_details = []
        for s in shifts_list:
            actual_val = str(df.iloc[i].get(s, "XX")).split('.')[0]
            if actual_val.isdigit():
                av_pad = str(int(actual_val)).zfill(2)
                if av_pad in row_universal:
                    hit_details.append(f"{s}:{av_pad}")
                    
        hist.append({
            "Date": df.iloc[i]['DATE'],
            "Universal Generated Count": len(row_universal),
            "Universal Numbers Set": ", ".join(row_universal) if row_universal else "None",
            "Universal Hits Found On Same Day": ", ".join(hit_details) if hit_details else "❌"
        })
        
    st.table(pd.DataFrame(hist))
        
