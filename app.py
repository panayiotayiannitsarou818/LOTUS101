# -*- coding: utf-8 -*-
# Wrapper version: 2025-09-06-security-8.6-FEATURES-DOC-and-MATCHING
import re, os, json, importlib.util, datetime as dt, math, base64, unicodedata
from pathlib import Path

import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="🧩 School Split — Thin Wrapper", page_icon="🧩", layout="wide")
st.title("🧩 School Split — Thin Wrapper")
st.caption("Λεπτός wrapper εκτέλεσης — Καμία αλλαγή στη λογική των modules.")
st.info("Έκδοση wrapper: 2025-09-06-security-8.6-FEATURES-DOC-and-MATCHING")

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
PERSIST_LOGO_PATH = ASSETS / "persisted_logo.bin"
PERSIST_LOGO_META = ASSETS / "persisted_logo.meta.json"

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
        if k.startswith("uploader_") or k in ("auth_ok","accepted_terms","app_enabled","last_final_path"):
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

def _inject_logo(logo_bytes: bytes, width_px: int = 140, mime: str = "image/png"):
    b64 = base64.b64encode(logo_bytes).decode("ascii")
    html = f"""
    <div style="position: fixed; bottom: 38px; right: 38px; z-index: 1000;">
        <img src="data:{mime};base64,{b64}" style="width:{width_px}px; height:auto; opacity:0.95; border-radius:12px;" />
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

    st.markdown("**Απλή ενεργοποίηση/απενεργοποίησης** της κύριας εφαρμογής και κλείδωμα με κωδικό.")
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

    if PERSIST_LOGO_PATH.exists() and PERSIST_LOGO_META.exists():
        try:
            meta = json.loads(PERSIST_LOGO_META.read_text(encoding="utf-8"))
            mime = meta.get("mime", "image/png")
            _inject_logo(_read_file_bytes(PERSIST_LOGO_PATH), width_px=140, mime=mime)
            st.caption("Φορτώθηκε **αυτόματα** το αποθηκευμένο λογότυπο (κάτω δεξιά).")
        except Exception:
            st.warning("Το αποθηκευμένο λογότυπο δεν μπόρεσε να φορτωθεί.")

    logo_file = st.file_uploader("PNG/JPG/SVG λογότυπο (προαιρετικό)", type=["png","jpg","jpeg","svg"], key="logo_upl")
    if logo_file is not None:
        try:
            mime = getattr(logo_file, "type", "image/png") or "image/png"
            data = logo_file.read()
            _inject_logo(data, width_px=140, mime=mime)
            try:
                PERSIST_LOGO_PATH.write_bytes(data)
                PERSIST_LOGO_META.write_text(json.dumps({"mime": mime, "saved_at": dt.datetime.now().isoformat()}), encoding="utf-8")
                st.success("Το λογότυπο **αποθηκεύτηκε μόνιμα** και θα φορτώνεται αυτόματα.")
            except Exception as e:
                st.warning(f"Ανεβάστηκε, αλλά δεν αποθηκεύτηκε μόνιμα: {e}")
        except Exception:
            st.warning("Δεν ήταν δυνατή η εμφάνιση του λογότυπου.")

    colL, colR = st.columns([1,1])
    with colL:
        if st.button("🧹 Καθαρισμός αποθηκευμένου λογότυπου", use_container_width=True):
            try:
                if PERSIST_LOGO_PATH.exists(): PERSIST_LOGO_PATH.unlink()
                if PERSIST_LOGO_META.exists(): PERSIST_LOGO_META.unlink()
                st.success("Διαγράφηκε το αποθηκευμένο λογότυπο.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Αποτυχία καθαρισμού: {e}")
    with colR:
        st.caption("Το αποθηκευμένο λογότυπο φορτώνεται πάντα αυτόματα.")

with st.expander("ℹ️ Εγχειρίδιο / Χαρακτηριστικά", expanded=True):
    st.markdown("""
**Κύρια λειτουργικότητα**  
- 📊 *Στατιστικά ανά τμήμα:* Κατανομή φύλου (αγόρια/κορίτσια), Παιδιά εκπαιδευτικού, Ζωηρά, Ιδιαιτερότητες, Επίπεδο ελληνικών, Μετρητές συγκρούσεων & σπασμένων φιλιών.  
- 🧩 *Ανάλυση σπασμένων αμοιβαίων φιλιών:* Εντοπισμός μαθητών που δηλώνουν αμοιβαία φιλία αλλά είναι σε διαφορετικά τμήματα, παραγωγή αναφορών (πλήρης λίστα ζευγών & μετρητές ανά μαθητή).  
- 🧾 *Συγκρούσεις στο ίδιο τμήμα:* Εντοπισμός μαθητών με σύγκρουση με συμμαθητές του ίδιου τμήματος (μετρητές & ονόματα).  

**Τεχνικά χαρακτηριστικά**  
- *Auto-rename columns:* Έξυπνη αντιστοίχιση ελληνικών στηλών σε κανονική μορφή.  
- *Name canonicalization:* Αφαίρεση διακριτικών, normalization ονομάτων.  
- *Friends parsing:* Επεξεργασία λιστών φίλων (CSV, arrays, κ.λπ.).  
- *Token-based name resolution:* Ευφυής αντιστοίχιση ονομάτων με partial matching.  
- *Multi-sheet processing:* Ανάλυση πολλαπλών σεναρίων/τμημάτων (όπου διατίθεται).  
- *Excel export:* Πλήρεις αναφορές με formatting.  

**Συμμόρφωση**  
- GDPR notices και όροι χρήσης — εκπαιδευτική χρήση μόνο.  
- Προστασία προσωπικών δεδομένων.  
- Copyright notice: © 2025 Γιαννίτσαρου Παναγιώτα.
""")

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

# ===== Έλεγχος αρχείων =====
st.subheader("📦 Έλεγχος αρχείων")
missing = _check_required_files(REQUIRED)
if missing:
    st.error("❌ Λείπουν αρχεία:\n" + "\n".join(f"- {m }" for m in missing))
else:
    st.success("✅ Όλα τα απαραίτητα αρχεία βρέθηκαν.")

st.divider()

# ===== ΕΚΤΕΛΕΣΗ ΚΑΤΑΝΟΜΗΣ (1→7) =====
st.header("🚀 Εκτέλεση ΟΛΑ (Βήματα 1→7)")
st.write("Ανέβασε μόνο το **αρχικό Excel**. Ο wrapper τρέχει 1→6 και μετά 7 και δίνει **τελικό αποτέλεσμα**. Το αρχείο αποθηκεύεται και χρησιμοποιείται αυτόματα από τα Στατιστικά.")

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

run_all = st.button("🚀 ΕΚΤΕΛΕΣΗ ΚΑΤΑΝΟΜΗΣ", type="primary", use_container_width=True)

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

                            st.session_state["last_final_path"] = str(final_out.resolve())

                            st.success(f"✅ Ολοκληρώθηκε. Νικητής: στήλη {winning_col}")
                            st.download_button(
                                "⬇️ Κατέβασε Τελικό Αποτέλεσμα (1→7)",
                                data=_read_file_bytes(final_out),
                                file_name=final_out.name,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                            st.caption("ℹ️ Το αρχείο αποθηκεύτηκε και θα χρησιμοποιηθεί **αυτόματα** από τα «📊 Στατιστικά».")

        except Exception as e:
            st.exception(e)

st.divider()

# ===== Helpers (stats) =====
def _find_latest_final_path() -> Path | None:
    p = st.session_state.get("last_final_path")
    if p and Path(p).exists():
        return Path(p)
    candidates = list(ROOT.glob("STEP7_FINAL_SCENARIO*.xlsx"))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return candidates[0]

def _strip_diacritics(s: str) -> str:
    nfkd = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

def _canon_name(s: str) -> str:
    s = (str(s) if s is not None else "").strip()
    s = s.strip("[]'\" ")
    s = re.sub(r"\s+", " ", s)
    s = _strip_diacritics(s).upper()
    return s

def _tokenize_name(canon: str):
    return [t for t in re.split(r"[^A-Z0-9]+", canon) if t]

def _best_name_match(target_canon: str, candidates: list[str]) -> str | None:
    # Exact
    if target_canon in candidates:
        return target_canon
    tks = set(_tokenize_name(target_canon))
    if not tks:
        return None
    # Score by token overlap and prefix hits
    best = None; best_score = 0.0
    for c in candidates:
        cks = set(_tokenize_name(c))
        if not cks:
            continue
        inter = tks & cks
        jacc = len(inter) / max(1, len(tks | cks))
        prefix = any(c.startswith(tok) or target_canon.startswith(tok) for tok in inter) if inter else False
        score = jacc + (0.2 if prefix else 0.0)
        if score > best_score:
            best = c; best_score = score
    if best_score >= 0.34:  # conservative threshold
        return best
    return None

def auto_rename_columns(df: pd.DataFrame):
    mapping = {}
    if "ΦΙΛΟΙ" not in df.columns:
        for c in df.columns:
            if "ΦΙΛ" in str(c).upper():
                mapping[c] = "ΦΙΛΟΙ"
                break
    if "ΣΥΓΚΡΟΥΣΗ" not in df.columns and "ΣΥΓΚΡΟΥΣΕΙΣ" in df.columns:
        mapping["ΣΥΓΚΡΟΥΣΕΙΣ"] = "ΣΥΓΚΡΟΥΣΗ"
    return df.rename(columns=mapping), mapping

def compute_conflict_counts_and_names(df: pd.DataFrame):
    if "ΟΝΟΜΑ" not in df.columns or "ΤΜΗΜΑ" not in df.columns:
        return pd.Series([0]*len(df), index=df.index), pd.Series([""]*len(df), index=df.index)
    # Ensure ΣΥΓΚΡΟΥΣΗ column exists
    sc = "ΣΥΓΚΡΟΥΣΗ" if "ΣΥΓΚΡΟΥΣΗ" in df.columns else None
    if sc is None:
        return pd.Series([0]*len(df), index=df.index), pd.Series([""]*len(df), index=df.index)
    df = df.copy()
    df["__C"] = df["ΟΝΟΜΑ"].map(_canon_name)
    cls = df["ΤΜΗΜΑ"].astype(str).str.strip()
    canon_names = list(df["__C"].astype(str).unique())
    index_by = {cn: i for i, cn in enumerate(df["__C"])}
    def parse_targets(cell):
        raw = str(cell) if cell is not None else ""
        parts = [p.strip() for p in re.split(r"[;,/|\n]", raw) if p.strip()]
        return [_canon_name(p) for p in parts]
    counts = [0]*len(df); names = [""]*len(df)
    for i, row in df.iterrows():
        my_class = cls.iloc[i]
        targets = parse_targets(row.get(sc,""))
        same = []
        for t in targets:
            j = index_by.get(t)
            if j is None:
                # try best-match
                match = _best_name_match(t, canon_names)
                j = index_by.get(match) if match else None
            if j is not None and cls.iloc[j] == my_class and df.loc[i, "__C"] != df.loc[j, "__C"]:
                same.append(df.loc[j, "ΟΝΟΜΑ"])
        counts[i] = len(same)
        names[i] = ", ".join(same)
    return pd.Series(counts, index=df.index), pd.Series(names, index=df.index)

def list_broken_mutual_pairs(df: pd.DataFrame) -> pd.DataFrame:
    fcol = next((c for c in ["ΦΙΛΟΙ","ΦΙΛΟΣ","ΦΙΛΙΑ"] if c in df.columns), None)
    if fcol is None or "ΟΝΟΜΑ" not in df.columns or "ΤΜΗΜΑ" not in df.columns:
        return pd.DataFrame(columns=["A","A_ΤΜΗΜΑ","B","B_ΤΜΗΜΑ"])
    df = df.copy()
    df["__C"] = df["ΟΝΟΜΑ"].map(_canon_name)
    name_to_original = dict(zip(df["__C"], df["ΟΝΟΜΑ"].astype(str)))
    class_by_name = dict(zip(df["__C"], df["ΤΜΗΜΑ"].astype(str).str.strip()))
    canon_names = list(df["__C"].astype(str).unique())
    def parse_list(cell):
        raw = str(cell) if cell is not None else ""
        parts = [p.strip() for p in re.split(r"[;,/|\n]", raw) if p.strip()]
        return [_canon_name(p) for p in parts]
    friends_map = {}
    for i, cn in enumerate(df["__C"]):
        raw_targets = parse_list(df.loc[i, fcol])
        resolved = []
        for t in raw_targets:
            if t in canon_names:
                resolved.append(t)
            else:
                match = _best_name_match(t, canon_names)
                if match:
                    resolved.append(match)
        friends_map[cn] = set(resolved)
    rows = []
    for a, fa in friends_map.items():
        for b in fa:
            fb = friends_map.get(b, set())
            if a in fb and class_by_name.get(a) != class_by_name.get(b):
                rows.append({
                    "A": name_to_original.get(a, a), "A_ΤΜΗΜΑ": class_by_name.get(a,""),
                    "B": name_to_original.get(b, b), "B_ΤΜΗΜΑ": class_by_name.get(b,"")
                })
    return pd.DataFrame(rows).drop_duplicates()

def generate_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "ΤΜΗΜΑ" in df:
        df["ΤΜΗΜΑ"] = df["ΤΜΗΜΑ"].astype(str).str.strip()
    boys = df[df.get("ΦΥΛΟ","").astype(str).str.upper().eq("Α")].groupby("ΤΜΗΜΑ").size() if "ΦΥΛΟ" in df else pd.Series(dtype=int)
    girls = df[df.get("ΦΥΛΟ","").astype(str).str.upper().eq("Κ")].groupby("ΤΜΗΜΑ").size() if "ΦΥΛΟ" in df else pd.Series(dtype=int)
    edus = df[df.get("ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ","").astype(str).str.upper().eq("Ν")].groupby("ΤΜΗΜΑ").size() if "ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ" in df else pd.Series(dtype=int)
    z = df[df.get("ΖΩΗΡΟΣ","").astype(str).str.upper().eq("Ν")].groupby("ΤΜΗΜΑ").size() if "ΖΩΗΡΟΣ" in df else pd.Series(dtype=int)
    id_ = df[df.get("ΙΔΙΑΙΤΕΡΟΤΗΤΑ","").astype(str).str.upper().eq("Ν")].groupby("ΤΜΗΜΑ").size() if "ΙΔΙΑΙΤΕΡΟΤΗΤΑ" in df else pd.Series(dtype=int)
    g = df[df.get("ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ","").astype(str).str.upper().eq("Ν")].groupby("ΤΜΗΜΑ").size() if "ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ" in df else pd.Series(dtype=int)
    total = df.groupby("ΤΜΗΜΑ").size() if "ΤΜΗΜΑ" in df else pd.Series(dtype=int)

    try:
        c_counts, _ = compute_conflict_counts_and_names(df)
        cls = df["ΤΜΗΜΑ"].astype(str).str.strip()
        conf_by_class = c_counts.groupby(cls).sum().astype(int)
    except Exception:
        conf_by_class = pd.Series(dtype=int)

    try:
        pairs = list_broken_mutual_pairs(df)
        if pairs.empty:
            broken = pd.Series({tm: 0 for tm in df["ΤΜΗΜΑ"].dropna().astype(str).str.strip().unique()})
        else:
            counts = {}
            for _, row in pairs.iterrows():
                counts[row["A_ΤΜΗΜΑ"]] = counts.get(row["A_ΤΜΗΜΑ"], 0) + 1
                counts[row["B_ΤΜΗΜΑ"]] = counts.get(row["B_ΤΜΗΜΑ"], 0) + 1
            broken = pd.Series(counts).astype(int)
    except Exception:
        broken = pd.Series(dtype=int)

    stats = pd.DataFrame({
        "ΑΓΟΡΙΑ": boys,
        "ΚΟΡΙΤΣΙΑ": girls,
        "ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ": edus,
        "ΖΩΗΡΟΙ": z,
        "ΙΔΙΑΙΤΕΡΟΤΗΤΑ": id_,
        "ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ": g,
        "ΣΥΓΚΡΟΥΣΗ": conf_by_class,
        "ΣΠΑΣΜΕΝΗ ΦΙΛΙΑ": broken,
        "ΣΥΝΟΛΟ ΜΑΘΗΤΩΝ": total,
    }).fillna(0).astype(int)

    try:
        stats = stats.sort_index(key=lambda x: x.str.extract(r"(\d+)")[0].astype(float))
    except Exception:
        stats = stats.sort_index()
    return stats

def export_stats_to_excel(stats_df: pd.DataFrame) -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        stats_df.to_excel(writer, index=True, sheet_name="Στατιστικά", index_label="ΤΜΗΜΑ")
        wb = writer.book; ws = writer.sheets["Στατιστικά"]
        header_fmt = wb.add_format({"bold": True, "valign":"vcenter", "text_wrap": True, "border":1})
        for col_idx, value in enumerate(["ΤΜΗΜΑ"] + list(stats_df.columns)):
            ws.write(0, col_idx, value, header_fmt)
        for i in range(0, len(stats_df.columns)+1):
            ws.set_column(i, i, 18)
    output.seek(0)
    return output

def prepare_conflict_students(df: pd.DataFrame) -> pd.DataFrame:
    counts, names = compute_conflict_counts_and_names(df)
    out = df.copy()
    out["ΣΥΓΚΡΟΥΣΗ_ΠΛΗΘΟΣ"] = counts.astype(int)
    out["ΣΥΓΚΡΟΥΣΗ_ΟΝΟΜΑ"] = names
    out = out.loc[out["ΣΥΓΚΡΟΥΣΗ_ΠΛΗΘΟΣ"] > 0, ["ΟΝΟΜΑ","ΤΜΗΜΑ","ΣΥΓΚΡΟΥΣΗ_ΠΛΗΘΟΣ","ΣΥΓΚΡΟΥΣΗ_ΟΝΟΜΑ"]]
    return out.sort_values(["ΤΜΗΜΑ","ΟΝΟΜΑ"])

# ===== 📊 Στατιστικά — UI tabs =====
st.header("📊 Στατιστικά — ΑΥΣΤΗΡΑ (AUTO από Βήμα 7)")

def _find_latest_final_path() -> Path | None:
    p = st.session_state.get("last_final_path")
    if p and Path(p).exists():
        return Path(p)
    candidates = list(ROOT.glob("STEP7_FINAL_SCENARIO*.xlsx"))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return candidates[0]

final_path = _find_latest_final_path()
if not final_path:
    st.warning("Δεν βρέθηκε αρχείο Βήματος 7. Πρώτα τρέξε «ΕΚΤΕΛΕΣΗ ΚΑΤΑΝΟΜΗΣ».")
else:
    try:
        xl = pd.ExcelFile(final_path)
        sheets = xl.sheet_names
        st.success(f"✅ Βρέθηκε: **{final_path.name}** | Sheets: {', '.join(sheets)}")
    except Exception as e:
        xl = None
        st.error(f"❌ Σφάλμα ανάγνωσης: {e}")

    if xl is not None and "FINAL_SCENARIO" in sheets:
        used_df = xl.parse("FINAL_SCENARIO")
        scen_cols = [c for c in used_df.columns if re.match(r"^ΒΗΜΑ6_ΣΕΝΑΡΙΟ_\d+$", str(c))]
        if len(scen_cols) != 1:
            st.error("❌ Απαιτείται **ακριβώς μία** στήλη `ΒΗΜΑ6_ΣΕΝΑΡΙΟ_N` στο FINAL_SCENARIO.")
        else:
            used_df["ΤΜΗΜΑ"] = used_df[scen_cols[0]].astype(str).str.strip()
            used_df, rename_map = auto_rename_columns(used_df)

            tab1, tab2, tab3 = st.tabs([
                "📊 Στατιστικά (1 sheet)",
                "❌ Σπασμένες αμοιβαίες (όλα τα sheets) — Έξοδος: Πλήρες αντίγραφο + Σύνοψη",
                "⚠️ Μαθητές με σύγκρουση στην ίδια τάξη",
            ])

            with tab1:
                st.subheader("📈 Υπολογισμός Στατιστικών για Επιλεγμένο Sheet")
                sheet_choice = st.selectbox("Διάλεξε sheet", ["FINAL_SCENARIO"])

                with st.expander("🔎 Διάγνωση/Μετονομασίες", expanded=False):
                    st.write("Αυτόματες μετονομασίες:", rename_map if rename_map else "—")
                    required_cols = ["ΟΝΟΜΑ","ΦΥΛΟ","ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ","ΖΩΗΡΟΣ","ΙΔΙΑΙΤΕΡΟΤΗΤΑ","ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ","ΦΙΛΟΙ","ΣΥΓΚΡΟΥΣΗ",]
                    missing_cols = [c for c in required_cols if c not in used_df.columns]
                    st.write("Λείπουν στήλες:", missing_cols if missing_cols else "—")
                st.info("Συμπλήρωσε/διόρθωσε τις στήλες που λείπουν στο Excel και ξαναφόρτωσέ το.")

                stats_df = generate_stats(used_df)
                st.dataframe(stats_df, use_container_width=True)

                st.download_button(
                    "📥 Εξαγωγή ΜΟΝΟ Στατιστικών (Excel)",
                    data=export_stats_to_excel(stats_df).getvalue(),
                    file_name=f"statistika_STEP7_FINAL_UI_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

            with tab2:
                st.subheader("💔 Σπασμένες αμοιβαίες φιλίες")
                pairs = list_broken_mutual_pairs(used_df)
                if pairs.empty:
                    st.success("Δεν βρέθηκαν σπασμένες αμοιβαίες φιλίες.")
                else:
                    st.dataframe(pairs, use_container_width=True)
                    counts = {}
                    for _, row in pairs.iterrows():
                        counts[row["A_ΤΜΗΜΑ"]] = counts.get(row["A_ΤΜΗΜΑ"], 0) + 1
                        counts[row["B_ΤΜΗΜΑ"]] = counts.get(row["B_ΤΜΗΜΑ"], 0) + 1
                    summary = pd.DataFrame.from_dict(counts, orient="index", columns=["Σπασμένες Αμοιβαίες"]).sort_index()
                    st.write("Σύνοψη ανά τμήμα:")
                    st.dataframe(summary, use_container_width=True)

            with tab3:
                st.subheader("⚠️ Μαθητές με σύγκρουση στην ίδια τάξη")
                conflict_students = prepare_conflict_students(used_df)
                if conflict_students.empty:
                    st.success("Δεν βρέθηκαν συγκρούσεις εντός της ίδιας τάξης.")
                else:
                    st.dataframe(conflict_students, use_container_width=True)

st.divider()

# ===== ♻️ Επανεκκίνηση (μία και καλή) =====
st.header("♻️ Επανεκκίνηση")
st.write("Καθαρίζει προσωρινά δεδομένα και ξαναφορτώνει το app.")
if st.button("♻️ Επανεκκίνηση τώρα", type="secondary", use_container_width=True, key="restart_btn"):
    _restart_app()

st.divider()

# ===== 🔎 Αναλυτικά (1→6) — ΤΕΛΕΥΤΑΙΟ =====
st.header("🔎 Αναλυτικά Σενάρια (Βήματα 1→6)")
st.write("Ενότητα σπάνιας χρήσης, μόνο για έλεγχο: παράγει Excel με όλα τα σενάρια (ΒΗΜΑ6_ΣΕΝΑΡΙΟ_1, …) και σύνοψη.")

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

run_16 = st.button("🧪 ΑΝΑΛΥΤΙΚΑ ΒΗΜΑΤΑ", type="secondary", use_container_width=True)

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

st.caption("Wrapper μόνο — τα modules φορτώνονται όπως είναι, χωρίς καμία αλλαγή στη λογική.")