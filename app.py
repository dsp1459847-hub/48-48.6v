import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="MAYA v48.6 - Freeze Matrix", layout="wide")

st.markdown("""
    <style>
    .live-res { background: #0f172a; color: #38bdf8; padding: 15px; border-radius: 12px; text-align: center; border: 2px solid #38bdf8; margin-bottom: 20px; }
    .metric-card { background: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #3b82f6; }
    .freeze-badge { background: #e0f2fe; color: #0369a1; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v48.6 (Calculation Freeze & Consistency Engine)")

# --- FIXED 32 CORE PATTERNS GENERATOR ---
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

# --- GAP SCANNER (STATIC DEPENDENCY) ---
def find_worst_gaps_90(df, idx, col):
    gap_scores = {}
    for g in range(1, 91):
        if idx - g - 10 < 0: continue
        score = 0
        for check in range(idx-10, idx):
            if check - g < 0: continue
            pred = str(df.iloc[check-g].get(col, "XX")).split('.')[0]
            act = str(df.iloc[check].get(col, "XX")).split('.')[0]
            if pred.isdigit() and act.isdigit() and pred == act: score += 1
        gap_scores[g] = score
    
    worst_gaps = sorted(gap_scores, key=gap_scores.get)[:5]
    bad_a, bad_b = [], []
    for wg in worst_gaps:
        val = str(df.iloc[idx-wg].get(col, 0)).split('.')[0]
        if val.isdigit():
            bad_a.append(int(val)//10)
            bad_b.append(int(val)%10)
    return max(set(bad_a), key=bad_a.count) if bad_a else 0, max(set(bad_b), key=bad_b.count) if bad_b else 5, worst_gaps

# --- FREEZE CORE ALGORITHM ---
# Ab yeh function sirf selected shift aur target row ke respect me calculation freeze rakhega
def calculate_m_engine_frozen(df, target_idx, current_loop_idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # LEVEL 1: Step Extraction (Strict tracking from current loop pointer)
    val = 0
    for i in range(1, 15):
        if current_loop_idx - i >= 0:
            raw = df.iloc[current_loop_idx-i].get(base_col, 0)
            if str(raw).isdigit() and int(raw) > 0:
                val = int(raw); break
                
    d1, d2 = val // 10, val % 10
    pa = (d1 + 1) % 10 if d1 != d2 else (d1 + 5) % 10
    pb = (d2 + 1) % 10
    ra, rb = (pa + 5) % 10, (pb + 5) % 10
    
    blocked = set()
    for a in {pa, ra}:
        for i in range(10): blocked.add(f"{a}{i}")
    for b in {pb, rb}:
        for i in range(10): blocked.add(f"{i}{b}")
        
    v48_base = [str(i).zfill(2) for i in range(100) if str(i).zfill(2) not in blocked]
    wa, wb, _ = find_worst_gaps_90(df, current_loop_idx, base_col)
    
    v48_stable = [j for j in v48_base if not (j.startswith(str(wa)) or j.endswith(str(wb)))]
    
    # 32-Pattern Extraction from accurate historical shift row
    prev_res = str(df.iloc[current_loop_idx-1].get(base_col, 0)).split('.')[0] if current_loop_idx - 1 >= 0 else "0"
    p32_set = generate_32_patterns(prev_res)
    
    common = [n for n in v48_stable if n in p32_set]
    uniq_v48 = [n for n in v48_stable if n not in p32_set]
    uniq_p32 = [n for n in p32_set if n not in v48_stable]
    
    return {"common": common, "uniq_v48": uniq_v48, "uniq_p32": uniq_p32, "v48_all": v48_stable}

# --- APPLICATION DASHBOARD ---
uploaded_file = st.file_uploader("📂 Upload Master Excel File", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    sel_date = st.selectbox("📅 Select Analysis Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    target_s = st.selectbox("🎰 Target Shift Group:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    live_val = str(df.iloc[idx].get(target_s, "XX")).split('.')[0]
    
    st.markdown(f'<div class="live-res">🎯 SELECTED TARGET RESULT: <span style="font-size:32px;">{live_val}</span></div>', unsafe_allow_html=True)
    
    # Target date predictions calculation
    data_sets = calculate_m_engine_frozen(df, idx, idx, target_s)
    
    # Display panel
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-card" style="border-top-color:#ef4444;"><h4>💎 High-Power Common (Frozen)</h4></div>', unsafe_allow_html=True)
        st.write(f"Count: **{len(data_sets['common'])}**")
        st.code(", ".join(data_sets['common']) if data_sets['common'] else "No Commons")
    with c2:
        st.markdown('<div class="metric-card" style="border-top-color:#10b981;"><h4>📦 Unique V48 Gaps</h4></div>', unsafe_allow_html=True)
        st.write(f"Count: **{len(data_sets['uniq_v48'])}**")
        st.code(", ".join(data_sets['uniq_v48'][:15]))
    with c3:
        st.markdown('<div class="metric-card" style="border-top-color:#f59e0b;"><h4>🌀 Unique 32-Pattern</h4></div>', unsafe_allow_html=True)
        st.write(f"Count: **{len(data_sets['uniq_p32'])}**")
        st.code(", ".join(data_sets['uniq_p32'][:15]))

    # --- NO-DEVIATION STRICT BACKTEST ENGINE ---
    st.divider()
    st.subheader("📊 Static 15-Day History Match Verification")
    st.caption("Yeh table real-time calculation lock karke check karti hai, history se values check karne par numbers badlenge nahi.")
    
    b_records = []
    c_hits, v_hits, p_hits = 0, 0, 0
    total_eval_days = 0
    
    # Static alignment validation loop
    for i in range(max(0, idx - 15), idx + 1):
        total_eval_days += 1
        # Passing current loop point as isolated pointer
        m_sets = calculate_m_engine_frozen(df, idx, i, target_s)
        
        flags = {"common": "❌", "v48": "❌", "p32": "❌"}
        
        # Next 4 shifts strict simulation
        for step in range(1, 5):
            if i + step >= len(df): continue
            f_res = str(df.iloc[i + step].get(target_s, "XX")).split('.')[0]
            if f_res.isdigit():
                f_num = str(int(f_res)).zfill(2)
                if f_num in m_sets['common']: flags['common'] = f"🎯 Hit (S{step})"
                if f_num in m_sets['uniq_v48']: flags['v48'] = f"✅ Hit (S{step})"
                if f_num in m_sets['uniq_p32']: flags['p32'] = f"⚡ Hit (S{step})"
        
        if "Hit" in flags['common']: c_hits += 1
        if "Hit" in flags['v48']: v_hits += 1
        if "Hit" in flags['p32']: p_hits += 1
        
        b_records.append({
            "History Date": df.iloc[i]['DATE'],
            "Historical Value": str(df.iloc[i].get(target_s, "XX")).split('.')[0],
            "Common Output": flags['common'],
            "V48 Output": flags['v48'],
            "32-Pattern Output": flags['p32']
        })
        
    c_p = round((c_hits / total_eval_days) * 100, 1) if total_eval_days else 0
    v_p = round((v_hits / total_eval_days) * 100, 1) if total_eval_days else 0
    p_p = round((p_hits / total_eval_days) * 100, 1) if total_eval_days else 0
    
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Locked Common Hit Rate", f"{c_p}%")
    sc2.metric("Locked V48 Hit Rate", f"{v_p}%")
    sc3.metric("Locked 32-Pattern Hit Rate", f"{p_p}%")
    
    st.table(pd.DataFrame(b_records))
      
