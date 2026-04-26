"""
data_loader.py
Loads NTPF waiting list data from local CSV files.
Built by Shubham Ravi
"""

import pandas as pd
import os

# ── Folder where your CSV files live ──
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "Data")

# ── File mapping ──
FILES = {
    "outpatient": {
        "hospital":  "OpenData_OPNational01_2026.csv",
        "specialty": "OpenData_OPNational02_2026.csv",
    },
    "inpatient": {
        "hospital":  "OpenData_IPDCNational01_2026.csv",
        "specialty": "OpenData_IPDCNational02_2026.csv",
        "detailed":  "OpenData_IPDCNational03_2026.csv",
    }
}


# ─────────────────────────────────────────────
# INTERNAL HELPERS
# ─────────────────────────────────────────────

def _read_csv(filename):
    path = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(path):
        print(f"[data_loader] File not found: {path}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"[data_loader] Error reading {filename}: {e}")
        return pd.DataFrame()


def _normalise_columns(df):
    rename_map = {
        "HospitalName":          "Hospital",
        "Hospital_Name":         "Hospital",
        "Speciality":            "Specialty",
        "Specialty Description": "Specialty",
        "18 Months +":           "18+ Months",
        "> 18 Months":           "18+ Months",
    }
    return df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})


def _clean_numeric(df):
    numeric_cols = [
        "Total", "0-6 Months", "6-12 Months",
        "12-18 Months", "18+ Months", "18 Months +",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
            )
            df[col] = (
                pd.to_numeric(df[col], errors="coerce")
                .fillna(0)
                .astype(float)
                .astype(int)
            )
    return df


def _prepare(df, source_tag):
    if df.empty:
        return df
    df = _normalise_columns(df)
    df = _clean_numeric(df)
    df["_source"] = source_tag
    if "ArchiveDate" in df.columns:
        df["ArchiveDate"] = pd.to_datetime(
            df["ArchiveDate"], dayfirst=True, errors="coerce"
        )
    return df


# ─────────────────────────────────────────────
# PUBLIC LOAD FUNCTIONS
# ─────────────────────────────────────────────

def load_data(list_type="outpatient"):
    """Load hospital + specialty files and combine into one DataFrame."""
    file_map = FILES.get(list_type, {})
    frames = []

    hospital_file = file_map.get("hospital")
    if hospital_file:
        df_h = _read_csv(hospital_file)
        df_h = _prepare(df_h, "hospital")
        if not df_h.empty:
            frames.append(df_h)

    specialty_file = file_map.get("specialty")
    if specialty_file:
        df_s = _read_csv(specialty_file)
        df_s = _prepare(df_s, "specialty")
        if not df_s.empty:
            frames.append(df_s)

    if not frames:
        print("[data_loader] No data loaded — check DATA_FOLDER and filenames.")
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def load_all_months(list_type="outpatient"):
    """Load all available files for trend analysis."""
    file_map = FILES.get(list_type, {})
    frames = []
    for key, filename in file_map.items():
        df = _read_csv(filename)
        df = _prepare(df, key)
        if not df.empty:
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# ─────────────────────────────────────────────
# SUMMARY & AGGREGATIONS
# ─────────────────────────────────────────────

def get_summary(df):
    if df.empty:
        return {"total_waiting": 0, "hospitals": 0, "specialties": 0, "over_18_months": 0}

    hosp_df = df[df["_source"] == "hospital"] if "_source" in df.columns else df
    spec_df = df[df["_source"] == "specialty"] if "_source" in df.columns else df

    total_waiting  = int(hosp_df["Total"].sum()) if "Total" in hosp_df.columns else 0
    hospital_count = hosp_df["Hospital"].nunique() if "Hospital" in hosp_df.columns else 0
    spec_count     = spec_df["Specialty"].nunique() if "Specialty" in spec_df.columns else 0
    over_18        = int(hosp_df["18+ Months"].sum()) if "18+ Months" in hosp_df.columns else 0

    return {
        "total_waiting":  total_waiting,
        "hospitals":      hospital_count,
        "specialties":    spec_count,
        "over_18_months": over_18,
    }


def get_worst_hospitals(df, top_n=15):
    if df.empty or "Hospital" not in df.columns or "Total" not in df.columns:
        return pd.DataFrame()
    data = df[df["_source"] == "hospital"] if "_source" in df.columns else df
    return (
        data.groupby("Hospital")["Total"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )


def get_worst_specialties(df, top_n=15):
    if df.empty or "Specialty" not in df.columns or "Total" not in df.columns:
        return pd.DataFrame()
    data = df[df["_source"] == "specialty"] if "_source" in df.columns else df
    return (
        data.groupby("Specialty")["Total"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )


def get_hospital_breakdown(df, hospital):
    """
    Returns wait band breakdown for a selected hospital.
    Melts wait band columns into rows for bar chart.
    """
    if df.empty or "Hospital" not in df.columns:
        return pd.DataFrame()

    data = df[df["_source"] == "hospital"] if "_source" in df.columns else df
    filtered = data[data["Hospital"] == hospital]

    if filtered.empty:
        return pd.DataFrame()

    band_cols = [
        c for c in ["0-6 Months", "6-12 Months", "12-18 Months", "18+ Months"]
        if c in filtered.columns
    ]

    if not band_cols:
        return pd.DataFrame()

    id_vars = ["Adult_Child"] if "Adult_Child" in filtered.columns else []
    melted = filtered[id_vars + band_cols].melt(
        id_vars=id_vars,
        value_vars=band_cols,
        var_name="Wait Band",
        value_name="Patients"
    )
    return melted.groupby("Wait Band")["Patients"].sum().reset_index()


def get_wait_band_totals(df):
    if df.empty:
        return pd.DataFrame()
    data = df[df["_source"] == "hospital"] if "_source" in df.columns else df
    bands = ["0-6 Months", "6-12 Months", "12-18 Months", "18+ Months"]
    available = [b for b in bands if b in data.columns]
    if not available:
        return pd.DataFrame()
    totals = {band: int(data[band].sum()) for band in available}
    return pd.DataFrame({
        "Wait Band": list(totals.keys()),
        "Patients":  list(totals.values())
    })


def get_specialty_hospital_pivot(df, specialty):
    """
    Search specialty totals.
    Since NTPF specialty files don't include hospital breakdown,
    we show the national total by Adult/Child split instead.
    """
    if df.empty:
        return pd.DataFrame()

    data = df[df["_source"] == "specialty"] if "_source" in df.columns else df

    if "Specialty" not in data.columns or "Total" not in data.columns:
        return pd.DataFrame()

    filtered = data[data["Specialty"].str.contains(specialty, case=False, na=False)]
    if filtered.empty:
        return pd.DataFrame()

    # Group by Adult_Child if available, else just return total
    if "Adult_Child" in filtered.columns:
        return (
            filtered.groupby("Adult_Child")["Total"]
            .sum()
            .reset_index()
            .rename(columns={"Adult_Child": "Category"})
            .sort_values("Total", ascending=False)
        )
    else:
        total = int(filtered["Total"].sum())
        return pd.DataFrame({"Category": ["All"], "Total": [total]})
    


def get_trend_data(list_type="outpatient"):
    df = load_all_months(list_type)
    if df.empty or "ArchiveDate" not in df.columns:
        return pd.DataFrame()
    data = df[df["_source"] == "hospital"] if "_source" in df.columns else df
    data = data[data["ArchiveDate"].notna()]
    return (
        data.groupby("ArchiveDate")["Total"]
        .sum()
        .reset_index()
        .sort_values("ArchiveDate")
    )