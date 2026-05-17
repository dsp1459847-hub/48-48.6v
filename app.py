import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="MAYA v48.0 - Next Day Predictor", layout="wide")

# Custom CSS for UI
st.markdown("""
    <style>
    .live-res { background: #1e293b; color: #fbbf24; padding: 12px; border-radius: 10px; text-align: center; border: 2px solid #fbbf24; margin-bottom: 15px; }
    .target-box { background: #0f172a; color: #38bdf8; padding: 12px; border-radius: 10px; text-align: center; border: 2px solid #38bdf8; margin-bottom: 15px; font-weight: bold; }
    .grid-square { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; max-width: 400px; margin: 10px auto; }
    .grid-item { background: #ffffff; color: #1e40af; padding: 12px; border-radius: 8px; font-size: 20px; font-weight: bold; text-align: center; border: 2px solid #bfdbfe; }
    .worst-badge { background: #fee2e2; color: #b91c1c; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin: 2px; border: 1px solid #fecaca; }
    .total-summary { background: #f8fafc; padding: 12px; border-radius: 8px; border-left: 5px solid #10b981; margin: 15px 0; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v48.0 (Next-Day Prediction & Value Lock Engine)")

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

# --- WORST GAPS SCANNER (90 GAPS) ---
def find_worst_gaps_90(df, idx, col):
    gap_scores = {}
    for g in range(1, 91):
        if idx - g - 10 < 0: continue
        score = 0
        for check in range(idx-10, idx):
            if check - g < 0: continue
            pred = str(df.iloc[check-g].get(col, "XX")).split('.')[0]
            act = str(df.iloc[check].get(col, "XX")).split('.')[0]
            if pred.isdigit() and act.isdigit() and pred == act:
                score += 1 
        gap_scores[g] = score
    
    worst_gaps = sorted(gap_scores, key=gap_scores.get)[:5]
    
    bad_andar = []
    bad_bahar = []
    for wg in worst_gaps:
        if idx - wg >= 0:
            val = str(df.iloc[idx-wg].get(col, 0)).split('.')[0]
            if val.isdigit():
                bad_andar.append(int(val)//10)
                bad_bahar.append(int(val)%10)
            
    final_a = max(set(bad_andar), key=bad_andar.count) if bad_andar else 0
    final_b = max(set(bad_bahar), key=bad_bahar.count) if bad_bahar else 5
    return final_a, final_b, worst_gaps

# --- CORE LOGIC WITH 1-STEP DATE FORWARD LOCK ---
def calculate_v48_next_day(df, base_idx, shift):
    """
    base_idx: Jis din ka data available hai (e.g., 15 Tarikh)
    Calculation poori tarah base_idx par chalegi, jo agle din (16 Tarikh) ke liye valid hogi.
    """
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # Code 37 Base (64 Jodis) scanning backwards from base_idx
    val = 0
    for i in range(0, 14): # Khade din se lekar piche tak scan
        if base_idx - i >= 0:
            raw = df.iloc[base_idx-i].get(base_col, 0)
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
    
    # Worst 90-Gap Filter based on base_idx
    wa, wb, wgaps = find_worst_gaps_90(df, base_idx, base_col)
    
    extra_hatao = set()
    for i in range(10):
        extra_hatao.add(f"{wa}{i}")
        extra_hatao.add(f"{i}{wb}")
        
    v48_stable = [j for j in target_36 if j not in extra_hatao]
    
    # 32-Pattern Generation from base_idx result
    current_actual_val = str(df.iloc[base_idx].get(base_col, 0)).split('.')[0]
    p32_set = generate_32_patterns(current_actual_val)
    
    # Segregation Tiers
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

# --- DASHBOARD INTERFACE ---
uploaded_file = st.file_uploader("📂 Upload Excel Data Sheet", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    # Date selection dropdown
    all_dates = df['DATE'].astype(str).unique().tolist()
    sel_date = st.selectbox("📅 Select Current Data Date:", options=all_dates[::-1])
    target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    base_idx = df[df['DATE'].astype(str) == sel_date].index[0]
    
    # Finding next date for target label display
    next_date_str = "Next Shift/Day"
    if base_idx + 1 < len(df):
        next_date_str = str(df.iloc[base_idx + 1]['DATE'])
        
    # --- LIVE RESULTS DISPLAY WITH CLEAR TARGETING ---
    live_val = str(df.iloc[base_idx].get(target_s, "XX")).split('.')[0]
    st.markdown(f'<div class="live-res">📂 Selected Base Date ({sel_date}) Result: <span style="font-size:24px; font-weight:bold;">{live_val}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="target-box">🚀 PREDICTION TARGET FOR DATE: <span style="font-size:26px; color:#fbbf24;">{next_date_str}</span></div>', unsafe_allow_html=True)

    # --- CALCULATE WITH ISOLATED NEXT-DAY LOGIC ---
    res_dict = calculate_v48_next_day(df, base_idx, target_s)

    st.divider()
    st.write(f"⚠️ **Worst Gaps Found (Based on {sel_date}):** " + " ".join([f'<span class="worst-badge">Gap-{g}</span>' for g in res_dict['wgaps']]), unsafe_allow_html=True)

    # --- TOTAL JODIS COUNTER MATRIX ---
    c_count = len(res_dict['common'])
    v_count = len(res_dict['uniq_v48'])
    p_count = len(res_dict['uniq_p32'])
    st.markdown(f'<div class="total-summary"> Northampton Matrix: Common ({c_count}) + Unique V48 ({v_count}) + Unique 32-Pattern ({p_count}) = {c_count + v_count + p_count} Active Jodis</div>', unsafe_allow_html=True)

    # --- ORIGINAL SQUARE 16 & SQUARE 9 BOXES ---
    col_left, col_right = st.columns(2)
    with col_left:
        st.write(f"**✅ Stable Target for {next_date_str} (Square 16)**")
        grid_html = '<div class="grid-square">'
        for j in res_dict['t16']: grid_html += f'<div class="grid-item">{j}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    with col_right:
        st.write(f"**💎 Super Hit for {next_date_str} (Square 9)**")
        grid_html = '<div class="grid-square" style="grid-template-columns: repeat(3, 1fr);">'
        for j in res_dict['t9']: grid_html += f'<div class="grid-item" style="background:#fff7ed; color:#9a3412; border-color:#fed7aa;">{j}</div>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- UNICORN TEAMS LISTS ---
    st.divider()
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        st.info("💎 **Common Tiers**")
        st.write(res_dict['common'] if res_dict['common'] else "No Commons")
    with tc2:
        st.success("📦 **Unique V48 Gaps**")
        st.write(res_dict['uniq_v48'])
    with tc3:
        st.warning("🌀 **Unique 32-Pattern**")
        st.write(res_dict['uniq_p32'])

    # --- PERFECT ALIGNED BACKTEST ENGINE ---
    st.divider()
    st.subheader("📜 10-Day Strict Next-Day Verification Backtest")
    st.caption("Yeh history table 1-step date forward rule par locked hai. Har row pichle din ka data uthakar agle din ke result ko match karegi.")
    
    hist = []
    # Loop chalaenge history test karne ke liye
    for i in range(max(0, base_idx - 10), base_idx + 1):
        if i + 1 >= len(df): continue # Agla din nahi hai toh skip karein
        
        # Calculate prediction using day 'i' as base
        h_res = calculate_v48_next_day(df, i, target_s)
        
        # Target day (i+1) ka real result kya khula, check karein
        target_date_real = df.iloc[i + 1]['DATE']
        actual_opened_raw = str(df.iloc[i + 1].get(target_s, "XX")).split('.')[0]
        
        hit_common = "❌"
        hit_v48 = "❌"
        hit_p32 = "❌"
        
        if actual_opened_raw.isdigit():
            f_val = str(int(actual_opened_raw)).zfill(2)
            
            if f_val in h_res['common']: hit_common = f"🎯 {f_val} (Pass)"
            if f_val in h_res['uniq_v48']: hit_v48 = f"✅ {f_val} (Pass)"
            if f_val in h_res['uniq_p32']: hit_p32 = f"⚡ {f_val} (Pass)"
                    
        hist.append({
            "Base Data Date": df.iloc[i]['DATE'],
            "Target Predict Date": target_date_real,
            "Actual Result Opened": actual_opened_raw,
            "Common Output Status": hit_common,
            "Unique V48 Status": hit_v48,
            "Unique 32-Pattern Status": hit_p32
        })
        
    st.table(pd.DataFrame(hist))
    
