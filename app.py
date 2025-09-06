# -*- coding: utf-8 -*-
# Wrapper version: 2025-09-06-security-2
import re, io, os, importlib.util, datetime as dt, math, base64
from pathlib import Path

import streamlit as st
import pandas as pd

st.set_page_config(page_title="🧩 School Split — Thin Wrapper", page_icon="🧩", layout="wide")
st.title("🧩 School Split — Thin Wrapper")
st.caption("Λεπτός wrapper εκτέλεσης — Καμία αλλαγή στη λογική των modules.")
st.info("Έκδοση wrapper: 2025-09-06-security-2")

ROOT = Path(__file__).parent

def _load_module(name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(name, str(file_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def _read_file_bytes(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()

def _timestamped(base: str, ext: str) -> str:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    import re as _re
    safe = _re.sub(r"[^A-Za-z0-9_\-\.]+", "_", base)
    return f"{safe}_{ts}{ext}"

def _check_required_files(paths):
    missing = [str(p) for p in paths if not p.exists()]
    return missing

def _restart_app():
    for k in list(st.session_state.keys()):
        if k.startswith("uploader_") or k in ("last_step6_path","auth_ok","accepted_terms","app_enabled"):
            try:
                del st.session_state[k]
            except Exception:
                pass
    try:
        st.cache_data.clear()
    except Exception:
        pass
    try:
        st.cache_resource.clear()
    except Exception:
        pass
    st.rerun()

def _inject_logo(logo_bytes: bytes, width_px: int = 140):
    b64 = base64.b64encode(logo_bytes).decode("ascii")
    html = f"""
    <div style="position: fixed; bottom: 38px; right: 38px; z-index: 1000;">
        <img src="data:image/png;base64,{b64}" style="width:{width_px}px; height:auto; opacity:0.95; border-radius:12px;" />
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def _terms_md():
    return """
**Υποχρεωτική Αποδοχή Όρων Χρήσης**  
Χρησιμοποιώντας την εφαρμογή δηλώνετε ότι:  
- Δεν τροποποιείτε τη λογική των αλγορίθμων και δεν αναδιανέμετε τα αρχεία χωρίς άδεια.  
- Αναλαμβάνετε την ευθύνη για την ορθότητα των εισαγόμενων δεδομένων.  
- Η εφαρμογή παρέχεται «ως έχει», χωρίς εγγύηση για οποιαδήποτε χρήση.  

**Πνευματικά Δικαιώματα & Νομική Προστασία**  
© 2025 Γιαννίτσαρου Παναγιώτα — Όλα τα δικαιώματα διατηρούνται.  
Ο κώδικας wrapper και το συνοδευτικό υλικό προστατεύονται από το δίκαιο πνευματικής ιδιοκτησίας.  
Για άδεια χρήσης/συνεργασίες: *panayiotayiannitsarou@gmail.com*.
"""

REQUIRED = [
    ROOT / "export_step1_6_per_scenario.py",
    ROOT / "step1_immutable_ALLINONE.py",
    ROOT / "step_2_helpers_FIXED.py",
    ROOT / "step_2_zoiroi_idiaterotites_FIXED_v3_PATCHED.py",
    ROOT / "step3_amivaia_filia_FIXED.py",
    ROOT / "step4_corrected.py",
    ROOT / "step5_enhanced.py",
    ROOT / "step6_compliant.py",
    ROOT / "step7_fixed_final.py",
]

with st.sidebar:
    st.header("🔐 Πρόσβαση & Ρυθμίσεις")

    st.markdown("**Απλή ενεργοποίηση/απενεργοποίηση** της κύριας εφαρμογής και κλείδωμα με κωδικό.")
    pwd = st.text_input("Κωδικός πρόσβασης", type="password", help="Κωδικός: katanomi2025")
    if "auth_ok" not in st.session_state:
        st.session_state.auth_ok = False
    if pwd:
        if pwd.strip() == "katanomi2025":
            st.session_state.auth_ok = True
        else:
            st.session_state.auth_ok = False
            st.error("Λανθασμένος κωδικός.")

    with st.expander("📄 Όροι Χρήσης & Πνευματικά Δικαιώματα", expanded=True):
        st.markdown(_terms_md())
    accepted_terms = st.checkbox("✅ Αποδέχομαι τους Όρους Χρήσης", value=st.session_state.get("accepted_terms", False))
    st.session_state.accepted_terms = accepted_terms

    app_enabled = st.toggle("⏯️ Ενεργοποίηση κύριας εφαρμογής", value=st.session_state.get("app_enabled", True))
    st.session_state.app_enabled = app_enabled

    st.divider()
    st.subheader("🖼️ Λογότυπο")
    logo_file = st.file_uploader("PNG/JPG/SVG λογότυπο (προαιρετικό)", type=["png","jpg","jpeg","svg"], key="logo_upl")
    if logo_file is not None:
        try:
            _inject_logo(logo_file.read(), width_px=140)
            st.caption("Το λογότυπο προβάλλεται κάτω δεξιά (~1cm από άκρες).")
        except Exception:
            st.warning("Δεν ήταν δυνατή η εμφάνιση του λογότυπου.")

# εικονίδιο features
with st.expander("ℹ️ Τα νέα που προστέθηκαν", expanded=True):
    st.markdown(
        "- 🔐 Κλείδωμα πρόσβασης με κωδικό (katanomi2025)
"
        "- ✅ Υποχρεωτική αποδοχή Όρων Χρήσης (με νομική δήλωση)
"
        "- ⏯️ Toggle ενεργοποίησης/απενεργοποίησης
"
        "- 📊 Κουμπί 'Στατιστικά' στο αρχικό Excel
"
        "- 🖼️ Σταθερό λογότυπο κάτω-δεξιά (~1cm)
"
    )

# Πύλες
if not st.session_state.auth_ok:
    st.warning("🔐 Εισάγετε τον σωστό κωδικό για πρόσβαση (katanomi2025).")
    st.stop()

if not st.session_state.accepted_terms:
    st.warning("✅ Για να συνεχίσετε, αποδεχθείτε τους Όρους Χρήσης (αριστερά).")
    st.stop()

if not st.session_state.app_enabled:
    st.info("⏸️ Η εφαρμογή είναι απενεργοποιημένη. Ενεργοποιήστε την από τα αριστερά.")
    st.stop()

box1, box2 = st.columns([3, 2])
with box1:
    st.subheader("📦 Έλεγχος αρχείων")
    missing = _check_required_files(REQUIRED)
    if missing:
        st.error("❌ Λείπουν αρχεία:\n" + "\n".join(f"- {m}" for m in missing))
    else:
        st.success("✅ Όλα τα απαραίτητα αρχεία βρέθηκαν.")

with box2:
    st.subheader("♻️ Επανεκκίνηση")
    if st.button("Επανεκκίνηση εφαρμογής", type="secondary", use_container_width=True):
        _restart_app()

st.divider()

# -------------- ΟΛΑ (1→7) --------------
st.header("🚀 Εκτέλεση ΟΛΑ (Βήματα 1→7)")
st.write("Ανέβασε μόνο το **αρχικό Excel**. Ο wrapper τρέχει 1→6 και μετά 7 και δίνει **τελικό αποτέλεσμα**.")

up_all = st.file_uploader("Ανέβασε αρχικό Excel (για 1→7)", type=["xlsx"], key="uploader_all")
colA, colB, colC = st.columns([1,1,1])
with colA:
    pick_step4_all = st.selectbox("Κανόνας επιλογής στο Βήμα 4", ["best", "first", "strict"], index=0, key="pick_all")
with colB:
    final_name_all = st.text_input("Όνομα αρχείου Τελικού Αποτελέσματος", value=_timestamped("STEP7_FINAL_SCENARIO", ".xlsx"))
with colC:
    if up_all is not None:
        try:
            df_preview = pd.read_excel(up_all, sheet_name=0)
            N = df_preview.shape[0]
            min_classes = max(2, math.ceil(N/25)) if N else 0
            st.metric("Μαθητές / Ελάχιστα τμήματα", f"{N} / {min_classes}")
        except Exception:
            st.caption("Δεν ήταν δυνατή η ανάγνωση για προεπισκόπηση.")

run_all = st.button("🚀 Τρέξε ΟΛΑ (1→7)", type="primary", use_container_width=True)

if run_all:
    if missing:
        st.error("Δεν είναι δυνατή η εκτέλεση: λείπουν modules.")
    elif up_all is None:
        st.warning("Πρώτα ανέβασε ένα Excel.")
    else:
        try:
            input_path = ROOT / _timestamped("INPUT_STEP1", ".xlsx")
            with open(input_path, "wb") as f:
                f.write(up_all.getbuffer())

            m = _load_module("export_step1_6_per_scenario", ROOT / "export_step1_6_per_scenario.py")
            s7 = _load_module("step7_fixed_final", ROOT / "step7_fixed_final.py")

            step6_path = ROOT / _timestamped("STEP1_6_PER_SCENARIO", ".xlsx")
            with st.spinner("Τρέχουν τα Βήματα 1→6..."):
                m.build_step1_6_per_scenario(str(input_path), str(step6_path), pick_step4=pick_step4_all)

            with st.spinner("Τρέχει το Βήμα 7..."):
                xls = pd.ExcelFile(step6_path)
                sheet_names = [s for s in xls.sheet_names if s != "Σύνοψη"]
                if not sheet_names:
                    st.error("Δεν βρέθηκαν sheets σεναρίων (εκτός από 'Σύνοψη').")
                else:
                    df0 = pd.read_excel(step6_path, sheet_name=sheet_names[0])
                    scen_cols = [c for c in df0.columns if re.match(r"^ΒΗΜΑ6_ΣΕΝΑΡΙΟ_\d+$", str(c))]
                    if not scen_cols:
                        st.error("Δεν βρέθηκαν στήλες τύπου 'ΒΗΜΑ6_ΣΕΝΑΡΙΟ_N'.")
                    else:
                        pick = s7.pick_best_scenario(df0.copy(), scen_cols, random_seed=42)
                        best = pick.get("best")
                        if not best or "scenario_col" not in best:
                            st.error("Αποτυχία επιλογής σεναρίου.")
                        else:
                            winning_col = best["scenario_col"]
                            final_out = ROOT / final_name_all
                            full_df = pd.read_excel(step6_path, sheet_name=sheet_names[0]).copy()
                            with pd.ExcelWriter(final_out, engine="xlsxwriter") as w:
                                full_df.to_excel(w, index=False, sheet_name="FINAL_SCENARIO")
                                labels = sorted(
                                    [str(v) for v in full_df[winning_col].dropna().unique() if re.match(r"^Α\d+$", str(v))],
                                    key=lambda x: int(re.search(r"\d+", x).group(0))
                                )
                                for lab in labels:
                                    sub = full_df.loc[full_df[winning_col] == lab, ["ΟΝΟΜΑ", winning_col]].copy()
                                    sub = sub.rename(columns={winning_col: "ΤΜΗΜΑ"})
                                    sub.to_excel(w, index=False, sheet_name=str(lab))

                            st.success(f"✅ Ολοκληρώθηκε. Νικητής: στήλη {winning_col}")
                            st.download_button(
                                "⬇️ Κατέβασε Τελικό Αποτέλεσμα (1→7)",
                                data=_read_file_bytes(final_out),
                                file_name=final_out.name,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
        except Exception as e:
            st.exception(e)

st.divider()

# -------------- Αναλυτικά (1→6) --------------
st.header("🔎 Αναλυτικά Σενάρια (Βήματα 1→6)")
st.write("Ανέβασε το **αρχικό Excel**. Θα παραχθεί Excel με όλα τα σενάρια (ΒΗΜΑ6_ΣΕΝΑΡΙΟ_1, …) και σύνοψη.")

up_16 = st.file_uploader("Ανέβασε αρχικό Excel (για 1→6)", type=["xlsx"], key="uploader_16")
col1, col2, col3 = st.columns([1,1,1])
with col1:
    pick_step4 = st.selectbox("Κανόνας επιλογής στο Βήμα 4", ["best", "first", "strict"], index=0, key="pick_16")
with col2:
    out_name_16 = st.text_input("Όνομα αρχείου εξόδου (1→6)", value=_timestamped("STEP1_6_PER_SCENARIO", ".xlsx"))
with col3:
    if up_16 is not None:
        try:
            df_preview2 = pd.read_excel(up_16, sheet_name=0)
            N2 = df_preview2.shape[0]
            min_classes2 = max(2, math.ceil(N2/25)) if N2 else 0
            st.metric("Μαθητές / Ελάχιστα τμήματα", f"{N2} / {min_classes2}")
        except Exception:
            st.caption("Δεν ήταν δυνατή η ανάγνωση για προεπισκόπηση.")

run_16 = st.button("▶️ Τρέξε Αναλυτικά (1→6)", use_container_width=True)

if run_16:
    if missing:
        st.error("Δεν είναι δυνατή η εκτέλεση: λείπουν modules.")
    elif up_16 is None:
        st.warning("Πρώτα ανέβασε ένα Excel.")
    else:
        try:
            input_path = ROOT / _timestamped("INPUT_STEP1", ".xlsx")
            with open(input_path, "wb") as f:
                f.write(up_16.getbuffer())

            m = _load_module("export_step1_6_per_scenario", ROOT / "export_step1_6_per_scenario.py")
            out_path = ROOT / out_name_16

            with st.spinner("Τρέχουν τα Βήματα 1→6..."):
                m.build_step1_6_per_scenario(str(input_path), str(out_path), pick_step4=pick_step4)

            st.success("✅ Ολοκληρώθηκε η παραγωγή σεναρίων (1→6).")
            st.download_button(
                "⬇️ Κατέβασε Excel (1→6)",
                data=_read_file_bytes(out_path),
                file_name=out_path.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.exception(e)

st.divider()

# -------------- Στατιστικά --------------
st.header("📊 Στατιστικά (από το αρχικό Excel)")
st.write("Χρησιμοποιεί το αρχείο που έχεις ανεβάσει σε μία από τις παραπάνω ενότητες (1→7 ή 1→6).")

def _stats_from_df(df: pd.DataFrame):
    out = {}
    N = df.shape[0]
    out["Σύνολο μαθητών"] = int(N)
    out["Ελάχιστα τμήματα (≤25)"] = int(max(2, math.ceil(N/25))) if N else 0

    def cnt(col, positive_vals=('Ν','Y','YES','Yes',1,True)):
        if col not in df.columns: return None
        ser = df[col].astype(str).str.strip()
        return int(ser.isin([str(v) for v in positive_vals]).sum())

    def by_value(col):
        if col not in df.columns: return None
        return df[col].fillna("—").astype(str).value_counts().to_dict()

    for col in ["ΦΥΛΟ","ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ"]:
        b = by_value(col)
        if b is not None:
            out[f"Κατανομή: {col}"] = b

    for flag in ["ΖΩΗΡΟΣ","ΙΔΙΑΙΤΕΡΟΤΗΤΑ","ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ"]:
        c = cnt(flag)
        if c is not None:
            out[f"Σύνολο {flag}=Ν"] = c

    if "ΦΙΛΟΙ" in df.columns:
        out["Συμπληρωμένες φιλικές δηλώσεις"] = int(df["ΦΙΛΟΙ"].notna().sum())
    if "ΣΥΓΚΡΟΥΣΗ" in df.columns:
        out["Καταχωρημένες συγκρούσεις"] = int(df["ΣΥΓΚΡΟΥΣΗ"].notna().sum())

    return out

if st.button("📊 Υπολόγισε Στατιστικά", use_container_width=True):
    ref_file = up_all if up_all is not None else up_16
    if ref_file is None:
        st.warning("Δεν έχεις ανεβάσει ακόμη αρχικό Excel. Ανέβασέ το στο 1→7 ή 1→6.")
    else:
        try:
            df_stats = pd.read_excel(ref_file, sheet_name=0)
            stats = _stats_from_df(df_stats)
            cols = st.columns(2)
            for i,(k,v) in enumerate(stats.items()):
                with cols[i%2]:
                    if isinstance(v, dict):
                        st.markdown(f"**{k}**")
                        st.json(v)
                    else:
                        st.metric(k, v)
        except Exception as e:
            st.exception(e)

st.divider()

# -------------- Επανεκκίνηση --------------
st.header("♻️ Επανεκκίνηση")
st.write("Καθαρίζει προσωρινά δεδομένα και ξαναφορτώνει το app.")
if st.button("♻️ Επανεκκίνηση τώρα", type="secondary", use_container_width=True, key="restart_btn"):
    _restart_app()

st.caption("Wrapper μόνο — τα modules φορτώνονται όπως είναι, χωρίς καμία αλλαγή στη λογική.")