import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="MAYA v49.4 - Aligned History Pass Engine", layout="wide")

# Custom CSS for Solid Chakor Grid & Bold Layouts
st.markdown("""
    <style>
    .live-res { background: #1e293b; color: #fbbf24; padding: 10px; border-radius: 10px; text-align: center; border: 2px solid #fbbf24; }
    .universal-box { background: #0f172a; color: #38bdf8; padding: 15px; border-radius: 12px; text-align: center; border: 2px solid #38bdf8; font-weight: bold; font-size: 20px; margin-bottom: 20px; }
    .summary-bar { background: #f8fafc; padding: 12px; border-radius: 8px; border-left: 5px solid #ef4444; margin: 15px 0; font-weight: bold; font-size: 18px; color: #1e293b; }
    .tier-bar { background: #eff6ff; padding: 10px; border-radius: 6px; border-left: 5px solid #3b82f6; margin: 10px 0; font-weight: bold; font-size: 16px; }
    
    /* Chakor Grid Components */
    .grid-square-dynamic { display: grid; grid-template-columns: repeat(10, 1fr); gap: 10px; width: 100%; margin: 15px 0; }
    .chakor-item-remaining { background: #dcfce7; color: #15803d; padding: 15px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid #bbf7d0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .chakor-item-blocked { background: #fee2e2; color: #b91c1c; padding: 15px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid #fecaca; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    /* Dynamic Tiers Formatting CSS */
    .chakor-tier-16 { background: #eff6ff; color: #1e40af; padding: 12px; border-radius: 6px; font-size: 22px; font-weight: bold; text-align: center; border: 2px solid #bfdbfe; }
    .chakor-tier-9 { background: #fef3c7; color: #92400e; padding: 12px; border-radius: 6px; font-size: 22px; font-weight: bold; text-align: center; border: 2px solid #fde68a; }
    .chakor-tier-5 { background: #f3e8ff; color: #6b21a8; padding: 12px; border-radius: 6px; font-size: 22px; font-weight: bold; text-align: center; border: 2px solid #e9d5ff; }
    .chakor-tier-1 { background: #fce7f3; color: #9d174d; padding: 15px; border-radius: 6px; font-size: 26px; font-weight: bold; text-align: center; border: 2px solid #fbcfe8; }
    
    .chakor-b-25 { background: #fef2f2; color: #991b1b; padding: 12px; border-radius: 6px; font-size: 22px; font-weight: bold; text-align: center; border: 2px solid #fecaca; }
    .chakor-b-16 { background: #fff7ed; color: #9a3412; padding: 12px; border-radius: 6px; font-size: 22px; font-weight: bold; text-align: center; border: 2px solid #fed7aa; }
    .chakor-b-9 { background: #fff9db; color: #856404; padding: 12px; border-radius: 6px; font-size: 22px; font-weight: bold; text-align: center; border: 2px solid #ffeeba; }
    .chakor-b-1 { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 6px; font-size: 26px; font-weight: bold; text-align: center; border: 2px solid #f5c6cb; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v49.4 (Strict Filtered History Engine)")

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
    sel_date = st.selectbox("📅 Date:", options=all_dates[::-1])
    target_s = st.selectbox("🎰 Select Shift for Analytics Tiers:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    shifts_list = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    
    # Calculate Double Engine Universes
    remaining_target_pool, universal_blocked_pool = calculate_inverse_universe(df, idx, shifts_list)
    
    # --- TOP INTERFACE SUMMARY PANELS ---
    st.markdown(f"""
    <div class="universal-box">
         🛡️ DOUBLE ENGINE CORE MODE: Selected Date (<b>{sel_date}</b>)<br>
         Total Universe (<b>100</b>) = Remaining Target Pool (<b>{len(remaining_target_pool)} Jodis</b>) + Blocked Overlaps Pool (<b>{len(universal_blocked_pool)} Jodis</b>)
    </div>
    """, unsafe_allow_html=True)
    
    # Render Grids Layout
    st.markdown(f'<div class="summary-bar" style="border-left-color: #10b981;">🎯 ENGINE 1: Active Target Remaining Jodis ({len(remaining_target_pool)}):</div>', unsafe_allow_html=True)
    g_rem = '<div class="grid-square-dynamic" style="grid-template-columns: repeat(10, 1fr);">'
    for j in remaining_target_pool: g_rem += f'<div class="chakor-item-remaining">{j}</div>'
    g_rem += '</div>'
    st.markdown(g_rem, unsafe_allow_html=True)
    
    st.markdown(f'<div class="summary-bar">🚫 ENGINE 2: Blocked Universal Jodis ({len(universal_blocked_pool)}):</div>', unsafe_allow_html=True)
    g_blk = '<div class="grid-square-dynamic" style="grid-template-columns: repeat(10, 1fr);">'
    for j in universal_blocked_pool: g_blk += f'<div class="chakor-item-blocked">{j}</div>'
    g_blk += '</div>'
    st.markdown(g_blk, unsafe_allow_html=True)

    # --- SCROLL DOWN: THE TWO SUB-POOL ANALYTICS GRIDS ---
    st.divider()
    st.subheader("⬇️ SCROLL DOWN: DUAL ENGINE SUB-POOL ANALYSIS SUB-GROUPS")
    
    pool_16, pool_9, pool_5, pool_1 = calculate_4_tiers_from_pool(remaining_target_pool, df, idx, target_s)
    blk_25, blk_16, blk_9, blk_1 = calculate_blocked_pool_tiers(universal_blocked_pool, df, idx, target_s)
    
    tab1, tab2 = st.tabs(["🟢 TRACKING: REMAINING POOL TIERS", "🔴 TRACKING: BLOCKED POOL TIERS"])
    
    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown('<div class="tier-bar">✅ Pool Stable (16 Jodis)</div>', unsafe_allow_html=True)
            g = '<div class="grid-square-dynamic" style="grid-template-columns: repeat(4, 1fr); gap: 6px;">'
            for n in pool_16: g += f'<div class="chakor-tier-16">{n}</div>'
            st.markdown(g+'</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="tier-bar" style="border-left-color: #f59e0b;">💎 Pool Super Hit (9 Jodis)</div>', unsafe_allow_html=True)
            g = '<div class="grid-square-dynamic" style="grid-template-columns: repeat(3, 1fr); gap: 6px;">'
            for n in pool_9: g += f'<div class="chakor-tier-9">{n}</div>'
            st.markdown(g+'</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="tier-bar" style="border-left-color: #a855f7;">🔥 Pool VVIP Target (5 Jodis)</div>', unsafe_allow_html=True)
            g = '<div class="grid-square-dynamic" style="grid-template-columns: repeat(1, 1fr); gap: 6px;">'
            for n in pool_5: g += f'<div class="chakor-tier-5">{n}</div>'
            st.markdown(g+'</div>', unsafe_allow_html=True)
        with c4:
            st.markdown('<div class="tier-bar" style="border-left-color: #ec4899;">👑 Pool Single Shot</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chakor-tier-1">{pool_1[0]}</div>', unsafe_allow_html=True)

    with tab2:
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.markdown('<div class="tier-bar">🚫 Blocked Stable (25 Jodis)</div>', unsafe_allow_html=True)
            g = '<div class="grid-square-dynamic" style="grid-template-columns: repeat(5, 1fr); gap: 6px;">'
            for n in blk_25: g += f'<div class="chakor-b-25">{n}</div>'
            st.markdown(g+'</div>', unsafe_allow_html=True)
        with b2:
            st.markdown('<div class="tier-bar" style="border-left-color: #f97316;">🚫 Blocked Stable (16 Jodis)</div>', unsafe_allow_html=True)
            g = '<div class="grid-square-dynamic" style="grid-template-columns: repeat(4, 1fr); gap: 6px;">'
            for n in blk_16: g += f'<div class="chakor-b-16">{n}</div>'
            st.markdown(g+'</div>', unsafe_allow_html=True)
        with b3:
            st.markdown('<div class="tier-bar" style="border-left-color: #eab308;">🚫 Blocked Super Hit (9 Jodis)</div>', unsafe_allow_html=True)
            g = '<div class="grid-square-dynamic" style="grid-template-columns: repeat(3, 1fr); gap: 6px;">'
            for n in blk_9: g += f'<div class="chakor-b-9">{n}</div>'
            st.markdown(g+'</div>', unsafe_allow_html=True)
        with b4:
            st.markdown('<div class="tier-bar" style="border-left-color: #b91c1c;">🚫 Blocked Single Shot</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chakor-b-1">{blk_1[0]}</div>', unsafe_allow_html=True)

    # --- ADVANCED DOUBLE POOL UNIFIED MASTER BACKTEST ---
    st.divider()
    st.subheader("📜 10-Day Unified Double Engine Validation Backtest")
    st.caption("Yeh master table strictly nikaley hue 16 aur 25 ankon ke subgroups ki actual passing track karti hai.")
    
    hist = []
    for i in range(max(0, idx - 10), idx + 1):
        row_rem_pool, row_blk_pool = calculate_inverse_universe(df, i, shifts_list)
        
        # Extracted sub-tiers based on row 'i'
        pr16, pr9, pr5, pr1 = calculate_4_tiers_from_pool(row_rem_pool, df, i, target_s)
        rb25, rb16, rb9, rb1 = calculate_blocked_pool_tiers(row_blk_pool, df, i, target_s)
        
        actual_opened = str(df.iloc[i].get(target_s, "XX")).split('.')[0]
        
        h_rem, h_blk = "❌", "❌"
        
        if actual_opened.isdigit():
            av = str(int(actual_opened)).zfill(2)
            if av in pr1: h_rem = "<span style='color:#ec4899; font-weight:bold;'>👑 Single</span>"
            elif av in pr5: h_rem = "<span style='color:#a855f7; font-weight:bold;'>🔥 VVIP-5</span>"
            elif av in pr9: h_rem = "<span style='color:#d97706; font-weight:bold;'>💎 Super-9</span>"
            elif av in pr16: h_rem = "<span style='color:#2563eb; font-weight:bold;'>✅ Stable-16</span>"
            
            if av in rb1: h_blk = "<span style='color:#b91c1c; font-weight:bold;'>👑 Single</span>"
            elif av in rb9: h_blk = "<span style='color:#eab308; font-weight:bold;'>💎 Super-9</span>"
            elif av in rb16: h_blk = "<span style='color:#f97316; font-weight:bold;'>✅ Stable-16</span>"
            elif av in rb25: h_blk = "<span style='color:#991b1b; font-weight:bold;'>📦 Stable-25</span>"

        # STRICT EXTRACTION COMPLIANCE: Mapped entirely to 16 and 25 sub-tiers ONLY
        rem_passed = []
        blk_passed = []
        
        for s in shifts_list:
            if s in df.columns:
                val = str(df.iloc[i].get(s, "XX")).split('.')[0]
                if val.isdigit():
                    v_pad = str(int(val)).zfill(2)
                    
                    # 🟢 RULE: Check strictly inside Stable-16 sub-tier only (Baki 100 me se saaf)
                    if v_pad in pr16: 
                        rem_passed.append(f"<span style='color:#16a34a; font-weight:bold;'>{s}:{v_pad}</span>")
                    
                    # 🔴 RULE: Check strictly inside Blocked Stable-25 sub-tier only (Baki 100 me se saaf)
                    if v_pad in rb25: 
                        blk_passed.append(f"<span style='color:#16a34a; font-weight:bold;'>{s}:{v_pad}</span>")
        
        hist.append({
            "History Date": f"<b>{df.iloc[i]['DATE']}</b>",
            "Target Res": f"<b>{actual_opened}</b>",
            "🟢 Remaining (16) History Pass": ", ".join(rem_passed) if rem_passed else "<b>None</b>",
            "🔴 Blocked (25) History Pass": ", ".join(blk_passed) if blk_passed else "<b>None</b>",
            "Engine-1 (Remaining Tier)": h_rem,
            "Engine-2 (Blocked Tier)": h_blk
        })
        
    df_hist = pd.DataFrame(hist)
    st.write(df_hist.to_html(escape=False, index=False), unsafe_allow_html=True)
        
