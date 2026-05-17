import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="MAYA v48.7 - Total Strike Highlighter", layout="wide")

# Custom UI Styling
st.markdown("""
    <style>
    .live-res { background: #0f172a; color: #38bdf8; padding: 15px; border-radius: 12px; text-align: center; border: 2px solid #38bdf8; margin-bottom: 20px; }
    .metric-card { background: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #3b82f6; }
    .total-box { background: #f1f5f9; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; border: 1px solid #cbd5e1; }
    .hit-badge { background: #bbf7d0; color: #166534; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v48.7 (Total Count & Exact Hit Tracker)")

# --- 32 CORE PATTERNS ENGINE ---
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

# --- GAP SCANNER ---
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
        val = str(df.iloc[wg].get(col, 0)).split('.')[0] if wg < len(df) else "0"
        if val.isdigit():
            bad_a.append(int(val)//10)
            bad_b.append(int(val)%10)
    return max(set(bad_a), key=bad_a.count) if bad_a else 0, max(set(bad_b), key=bad_b.count) if bad_b else 5, worst_gaps

# --- FREEZE ADVANCED CORE ENGINE ---
def calculate_m_engine_frozen(df, current_loop_idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
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
    
    prev_res = str(df.iloc[current_loop_idx-1].get(base_col, 0)).split('.')[0] if current_loop_idx - 1 >= 0 else "0"
    p32_set = generate_32_patterns(prev_res)
    
    common = sorted(list(set([n for n in v48_stable if n in p32_set])))
    uniq_v48 = sorted(list(set([n for n in v48_stable if n not in p32_set])))
    uniq_p32 = sorted(list(set([n for n in p32_set if n not in v48_stable])))
    
    return {"common": common, "uniq_v48": uniq_v48, "uniq_p32": uniq_p32}

# --- APPLICATION CONTROLS ---
uploaded_file = st.file_uploader("📂 Upload Master Excel File", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    sel_date = st.selectbox("📅 Select Analysis Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    target_s = st.selectbox("🎰 Target Shift Group:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    live_val = str(df.iloc[idx].get(target_s, "XX")).split('.')[0]
    
    st.markdown(f'<div class="live-res">🎯 SELECTED DATE RESULT: <span style="font-size:32px;">{live_val}</span></div>', unsafe_allow_html=True)
    
    # Calculate current day sets
    current_sets = calculate_m_engine_frozen(df, idx, target_s)
    
    # Total Calculation Check
    tot_common = len(current_sets['common'])
    tot_v48 = len(current_sets['uniq_v48'])
    tot_p32 = len(current_sets['uniq_p32'])
    grand_total = tot_common + tot_v48 + tot_p32
    
    # --- TOTALS LEADERBOARD PANEL ---
    st.markdown(f"""
    <div class="total-box">
         📊 LIVE TOTAL NUMBERS COUNT: Common ({tot_common}) + Unique V48 ({tot_v48}) + Unique 32-Pattern ({tot_p32}) = Grand Active Total ({grand_total} Jodis)
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-card" style="border-top-color:#ef4444;"><h4>💎 Common Numbers</h4></div>', unsafe_allow_html=True)
        st.write(current_sets['common'] if current_sets['common'] else "No matching items")
    with c2:
        st.markdown('<div class="metric-card" style="border-top-color:#10b981;"><h4>📦 Unique V48 Numbers</h4></div>', unsafe_allow_html=True)
        st.write(current_sets['uniq_v48'])
    with c3:
        st.markdown('<div class="metric-card" style="border-top-color:#f59e0b;"><h4>🌀 Unique 32-Pattern Numbers</h4></div>', unsafe_allow_html=True)
        st.write(current_sets['uniq_p32'])

    # --- ADVANCED HIGH-LIGHTER VALIDATION HISTORY ---
    st.divider()
    st.subheader("📜 15-Day Deep Scan Match & Exact Value Discovery")
    st.caption("Yeh table real-time analysis nikaalti hai aur check karti hai ki un 4 shifts ke andar teeno tiers me se kaun sa EXACT number pass hoke nikla hai.")
    
    b_records = []
    
    for i in range(max(0, idx - 15), idx + 1):
        m_sets = calculate_m_engine_frozen(df, i, target_s)
        
        # Strings to hold matching statuses and exact hit numbers
        hit_common_num = "-"
        hit_v48_num = "-"
        hit_p32_num = "-"
        
        # Simulating Next 4 Shifts checking
        for step in range(1, 5):
            if i + step >= len(df): continue
            f_res = str(df.iloc[i + step].get(target_s, "XX")).split('.')[0]
            if f_res.isdigit():
                f_num = str(int(f_res)).zfill(2)
                
                if f_num in m_sets['common'] and hit_common_num == "-":
                    hit_common_num = f"{f_num} (S{step})"
                if f_num in m_sets['uniq_v48'] and hit_v48_num == "-":
                    hit_v48_num = f"{f_num} (S{step})"
                if f_num in m_sets['uniq_p32'] and hit_p32_num == "-":
                    hit_p32_num = f"{f_num} (S{step})"
        
        b_records.append({
            "History Date": df.iloc[i]['DATE'],
            "Base Opened Value": str(df.iloc[i].get(target_s, "XX")).split('.')[0],
            "Exact Common Hit Number": hit_common_num if hit_common_num != "-" else "❌",
            "Exact Unique V48 Hit Number": hit_v48_num if hit_v48_num != "-" else "❌",
            "Exact Unique 32-Pattern Hit Number": hit_p32_num if hit_p32_num != "-" else "❌"
        })
        
    st.table(pd.DataFrame(b_records))
            
