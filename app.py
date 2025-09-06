# -*- coding: utf-8 -*-
import re, io, os, importlib.util, datetime as dt
from pathlib import Path

import streamlit as st
import pandas as pd

# ---------------------------
# Ρυθμίσεις σελίδας
# ---------------------------
st.set_page_config(page_title="🧩 School Split — Thin Wrapper", page_icon="🧩", layout="wide")
st.title("🧩 School Split — Thin Wrapper")

st.markdown("""
<div style="display:flex; align-items:center; gap:10px; margin-top:-8px; margin-bottom:8px;">
  <span style="font-size:0.95rem;">Μια παιδεία που βλέπει το φως σε όλα τα παιδιά</span>
  <svg width="26" height="26" viewBox="0 0 64 64" aria-label="lotus" role="img">
    <g fill="#B57EDC">
      <path d="M32 8c-4 8-4 16 0 24 4-8 4-16 0-24z"/>
      <path d="M18 14c-1 7 1 14 6 20 1-8-1-16-6-20z"/>
      <path d="M46 14c-5 4-7 12-6 20 5-6 7-13 6-20z"/>
      <path d="M10 28c3 6 9 10 16 12-3-6-8-11-16-12z"/>
      <path d="M54 28c-8 1-13 6-16 12 7-2 13-6 16-12z"/>
      <path d="M20 38c3 6 8 10 12 10s9-4 12-10c-7 2-17 2-24 0z"/>
    </g>
  </svg>
</div>
""", unsafe_allow_html=True)

ROOT = Path(__file__).parent

# ---------------------------
# Βοηθητικά
# ---------------------------
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
    safe = re.sub(r"[^A-Za-z0-9_\-\.]+", "_", base)
    return f"{safe}_{ts}{ext}"

def _check_required_files(paths):
    missing = [str(p) for p in paths if not p.exists()]
    return missing

def _restart_app():
    # καθάρισμα uploader keys & cache
    for k in list(st.session_state.keys()):
        if k.startswith("uploader_") or k in ("last_step6_path",):
            del st.session_state[k]
    try:
        st.cache_data.clear()
    except Exception:
        pass
    try:
        st.cache_resource.clear()
    except Exception:
        pass
    st.rerun()

# ---------------------------
# Απαραίτητα modules που ΔΕΝ αλλάζουμε
# ---------------------------
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

# ---------------------------
# Κουμπί 1 — ΟΛΑ (Βήματα 1→7) με ένα upload
# ---------------------------
st.header("🚀 ΕΚΤΕΛΕΣΗ ΚΑΤΑΝΟΜΗΣ")
st.write("Ανέβασε μόνο το **αρχικό Excel**. Ο wrapper τρέχει 1→6 και αμέσως μετά 7 και σου δίνει **το τελικό αποτέλεσμα** (FINAL_SCENARIO + ανά τμήμα).")

up_all = st.file_uploader("Ανέβασε αρχικό Excel (για 1→7)", type=["xlsx"], key="uploader_all")
colA, colB = st.columns(2)
with colA:
    pick_step4_all = st.selectbox("Κανόνας επιλογής στο Βήμα 4", ["best", "first", "strict"], index=0, key="pick_all")
with colB:
    final_name_all = st.text_input("Όνομα αρχείου Τελικού Αποτελέσματος", value=_timestamped("STEP7_FINAL_SCENARIO", ".xlsx"))

run_all = st.button("🚀 Τρέξε ΟΛΑ (1→7)", type="primary", use_container_width=True)

if run_all:
    if missing:
        st.error("Δεν είναι δυνατή η εκτέλεση: λείπουν modules.")
    elif up_all is None:
        st.warning("Πρώτα ανέβασε ένα Excel.")
    else:
        try:
            # Αποθήκευση input
            input_path = ROOT / _timestamped("INPUT_STEP1", ".xlsx")
            with open(input_path, "wb") as f:
                f.write(up_all.getbuffer())

            # Φόρτωση modules
            m = _load_module("export_step1_6_per_scenario", ROOT / "export_step1_6_per_scenario.py")
            s7 = _load_module("step7_fixed_final", ROOT / "step7_fixed_final.py")

            # 1→6
            step6_path = ROOT / _timestamped("STEP1_6_PER_SCENARIO", ".xlsx")
            with st.spinner("Τρέχουν τα Βήματα 1→6..."):
                m.build_step1_6_per_scenario(str(input_path), str(step6_path), pick_step4=pick_step4_all)

            # 7
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
                            # Χτίζουμε το τελικό workbook
                            final_out = ROOT / final_name_all
                            full_df = pd.read_excel(step6_path, sheet_name=sheet_names[0]).copy()
                            with pd.ExcelWriter(final_out, engine="xlsxwriter") as w:
                                # sheet 1: FINAL_SCENARIO (ολόκληρος πίνακας με τη στήλη-νικητή)
                                full_df.to_excel(w, index=False, sheet_name="FINAL_SCENARIO")
                                # extra sheets: ανά τμήμα
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

# ---------------------------
# Κουμπί 2 — Αναλυτικά (Βήματα 1→6) με ένα upload
# ---------------------------
st.header("🔎 Αναλυτικά Σενάρια (Βήματα 1→6)")
st.write("Ανέβασε το **αρχικό Excel**. Θα παραχθεί Excel με όλα τα σενάρια (ΒΗΜΑ6_ΣΕΝΑΡΙΟ_1, …) και σύνοψη.")

up_16 = st.file_uploader("Ανέβασε αρχικό Excel (για 1→6)", type=["xlsx"], key="uploader_16")
col1, col2 = st.columns(2)
with col1:
    pick_step4 = st.selectbox("Κανόνας επιλογής στο Βήμα 4", ["best", "first", "strict"], index=0, key="pick_16")
with col2:
    out_name_16 = st.text_input("Όνομα αρχείου εξόδου (1→6)", value=_timestamped("STEP1_6_PER_SCENARIO", ".xlsx"))

run_16 = st.button("▶️ Τρέξε Αναλυτικά (1→6)", use_container_width=True)

if run_16:
    if missing:
        st.error("Δεν είναι δυνατή η εκτέλεση: λείπουν modules.")
    elif up_16 is None:
        st.warning("Πρώτα ανέβασε ένα Excel.")
    else:
        try:
            # save upload
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

# ---------------------------
# Κουμπί 3 — Επανεκκίνηση
# ---------------------------
st.header("♻️ Επανεκκίνηση")
st.write("Καθαρίζει προσωρινά δεδομένα και ξαναφορτώνει το app.")
if st.button("♻️ Επανεκκίνηση τώρα", type="secondary", use_container_width=True, key="restart_btn"):
    _restart_app()

st.caption("Wrapper μόνο — τα modules φορτώνονται όπως είναι, χωρίς καμία αλλαγή στη λογική.")
