# ============================================================
# INDIGO MARKET INTELLIGENCE ENGINE V2
# app.py
# ============================================================

import os
import pickle
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

APP_TITLE = "Indigo Market Intelligence"
ENGINE_FILE = "indigo_v2_engine_streamlit_complete.pkl"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# ENGINE LOADER
# ============================================================

@st.cache_resource
def load_engine(path):
    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        return pickle.load(f)


engine = load_engine(ENGINE_FILE)


if engine is None:
    st.error(
        f"Engine artifact not found: `{ENGINE_FILE}`"
    )
    st.info(
        "Place app.py and indigo_v2_engine.pkl in the same directory."
    )
    st.stop()


# ============================================================
# SAFE HELPERS
# ============================================================

def get_dict(obj):
    return obj if isinstance(obj, dict) else {}


def get_df(obj):
    if isinstance(obj, pd.DataFrame):
        return obj.copy()

    if isinstance(obj, list):
        try:
            return pd.DataFrame(obj)
        except Exception:
            return pd.DataFrame()

    if isinstance(obj, dict):
        try:
            return pd.DataFrame(obj)
        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()


def fmt_number(x, decimals=2):
    try:
        if pd.isna(x):
            return "—"
        return f"{float(x):,.{decimals}f}"
    except Exception:
        return "—"


def fmt_pct(x, decimals=2):
    try:
        if pd.isna(x):
            return "—"
        return f"{float(x):,.{decimals}f}%"
    except Exception:
        return "—"


def find_frames(obj, path=""):
    """
    Recursively locate DataFrames contained in the engine artifact.
    """
    found = {}

    if isinstance(obj, pd.DataFrame):
        found[path or "data"] = obj.copy()

    elif isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{path}.{key}" if path else str(key)
            found.update(find_frames(value, child_path))

    elif isinstance(obj, (list, tuple)):
        for i, value in enumerate(obj):
            child_path = f"{path}[{i}]"
            found.update(find_frames(value, child_path))

    return found


def frame_matches(name, terms):
    name = name.lower()
    return any(term in name for term in terms)


ALL_FRAMES = find_frames(engine)


def frames_for(terms):
    return {
        name: df
        for name, df in ALL_FRAMES.items()
        if frame_matches(name, terms)
    }


def first_frame(terms):
    candidates = frames_for(terms)
    return next(iter(candidates.values()), pd.DataFrame())


# ============================================================
# ENGINE STRUCTURE
# ============================================================

metadata = get_dict(engine.get("metadata"))

universe = get_dict(engine.get("universe"))
integrity = get_dict(engine.get("data_integrity"))
supporting = get_dict(engine.get("supporting"))


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("## INDIGO")
st.sidebar.caption("Market Intelligence Engine")

st.sidebar.divider()

page = st.sidebar.radio(
    "Intelligence",
    [
        "Executive Overview",
        "Market Intelligence",
        "Portfolio Risk",
        "Cross-Asset Risk",
        "Stress & Scenario",
        "Liquidity",
        "Alerts & Exceptions",
        "Institutional Report",
    ],
)

st.sidebar.divider()

st.sidebar.caption(
    f"Engine {metadata.get('version', 'V2')}"
)

if metadata.get("export_timestamp"):
    st.sidebar.caption(
        f"Data snapshot: {metadata['export_timestamp']}"
    )


# ============================================================
# HEADER
# ============================================================

def page_header(title, subtitle):
    st.title(title)
    st.caption(subtitle)
    st.divider()


# ============================================================
# 1. EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    page_header(
        "Executive Overview",
        "Institutional view of market conditions, portfolio risk and exceptions."
    )

    clean_data = get_dict(
        integrity.get("clean_market_data")
    )

    rejected = get_dict(
        integrity.get("rejected_assets")
    )

    quality = get_df(
        integrity.get("data_quality_summary")
    )

    registry = get_dict(
        universe.get("instrument_registry")
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Tracked Assets",
        len(registry) if registry else len(clean_data)
    )

    c2.metric(
        "Clean Series",
        len(clean_data)
    )

    c3.metric(
        "Rejected Assets",
        len(rejected)
    )

    c4.metric(
        "Quality Records",
        len(quality)
    )

    st.divider()

    st.subheader("Engine Coverage")

    coverage = pd.DataFrame({
        "Module": [
            "Universe & Configuration",
            "Data Integrity",
            "Market Risk",
            "Portfolio Risk",
            "Factor / Common Risk",
            "Attribution",
            "Stress & Scenario",
            "Liquidity",
            "Monitoring & Exceptions",
            "Indigo Intelligence",
            "Institutional Reporting",
        ],
        "Status": [
            "Loaded",
            "Loaded",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
        ],
    })

    st.dataframe(
        coverage,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Data Quality")

    if quality.empty:
        st.info("No data-quality table is available.")
    else:
        st.dataframe(
            quality,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# 2. MARKET INTELLIGENCE
# ============================================================

elif page == "Market Intelligence":

    page_header(
        "Market Intelligence",
        "Asset-level returns, volatility, drawdown, anomalies and market behaviour."
    )

    market_frames = frames_for([
        "market",
        "asset",
        "return",
        "volatility",
        "drawdown",
        "anomaly",
        "regime",
    ])

    if not market_frames:
        st.info(
            "No downstream market-analysis tables are embedded in the current artifact."
        )
    else:

        selected = st.selectbox(
            "Analysis",
            list(market_frames.keys()),
        )

        df = market_frames[selected]

        st.metric(
            "Observations",
            f"{len(df):,}"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# 3. PORTFOLIO RISK
# ============================================================

elif page == "Portfolio Risk":

    page_header(
        "Portfolio Risk",
        "Portfolio exposure, concentration and risk contribution."
    )

    portfolio_frames = frames_for([
        "portfolio",
        "risk",
        "contribution",
        "exposure",
    ])

    if not portfolio_frames:
        st.info(
            "No downstream portfolio-risk table is embedded in the current artifact."
        )
    else:

        selected = st.selectbox(
            "Portfolio analysis",
            list(portfolio_frames.keys()),
        )

        df = portfolio_frames[selected]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# 4. CROSS-ASSET RISK
# ============================================================

elif page == "Cross-Asset Risk":

    page_header(
        "Cross-Asset Risk",
        "Correlation, beta and common-risk relationships across the universe."
    )

    cross_frames = frames_for([
        "correlation",
        "factor",
        "beta",
        "cross",
        "common",
    ])

    if not cross_frames:
        st.info(
            "No downstream cross-asset analysis table is embedded in the current artifact."
        )
    else:

        selected = st.selectbox(
            "Cross-asset analysis",
            list(cross_frames.keys()),
        )

        df = cross_frames[selected]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# 5. STRESS & SCENARIO
# ============================================================

elif page == "Stress & Scenario":

    page_header(
        "Stress & Scenario",
        "Portfolio and market behaviour under adverse conditions and scenarios."
    )

    stress_frames = frames_for([
        "stress",
        "scenario",
        "shock",
        "sensitivity",
    ])

    if not stress_frames:
        st.info(
            "No downstream stress/scenario table is embedded in the current artifact."
        )
    else:

        selected = st.selectbox(
            "Scenario analysis",
            list(stress_frames.keys()),
        )

        df = stress_frames[selected]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# 6. LIQUIDITY
# ============================================================

elif page == "Liquidity":

    page_header(
        "Liquidity",
        "Asset and portfolio liquidity conditions and liquidity stress."
    )

    liquidity_frames = frames_for([
        "liquidity",
        "liquid",
    ])

    if not liquidity_frames:
        st.info(
            "No downstream liquidity table is embedded in the current artifact."
        )
    else:

        selected = st.selectbox(
            "Liquidity analysis",
            list(liquidity_frames.keys()),
        )

        df = liquidity_frames[selected]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# 7. ALERTS & EXCEPTIONS
# ============================================================

elif page == "Alerts & Exceptions":

    page_header(
        "Alerts & Exceptions",
        "Prioritised market, portfolio and liquidity exceptions."
    )

    alert_frames = frames_for([
        "alert",
        "exception",
        "anomaly",
        "monitor",
        "signal",
    ])

    if not alert_frames:
        st.info(
            "No downstream monitoring table is embedded in the current artifact."
        )
    else:

        selected = st.selectbox(
            "Monitoring output",
            list(alert_frames.keys()),
        )

        df = alert_frames[selected]

        # Attempt to identify severity column
        severity_cols = [
            c for c in df.columns
            if any(
                term in str(c).lower()
                for term in [
                    "severity",
                    "priority",
                    "level",
                ]
            )
        ]

        if severity_cols:

            severity = severity_cols[0]

            counts = (
                df[severity]
                .astype(str)
                .value_counts()
            )

            cols = st.columns(
                min(4, max(1, len(counts)))
            )

            for col, (level, count) in zip(
                cols,
                counts.items()
            ):
                col.metric(
                    str(level),
                    int(count)
                )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# 8. INSTITUTIONAL REPORT
# ============================================================

elif page == "Institutional Report":

    page_header(
        "Institutional Report",
        "Formal Indigo market intelligence and risk reporting."
    )

    report = (
        engine.get("INSTITUTIONAL_REPORT")
        or engine.get("institutional_report")
    )

    if report is None:

        st.info(
            "The institutional report is not embedded in the current artifact."
        )

    elif isinstance(report, dict):

        for name, content in report.items():

            st.subheader(
                str(name).replace("_", " ").title()
            )

            if isinstance(content, pd.DataFrame):

                st.dataframe(
                    content,
                    use_container_width=True,
                    hide_index=True,
                )

            elif isinstance(content, dict):

                st.json(content)

            else:

                st.write(content)

    else:

        st.write(report)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Indigo Market Intelligence Engine V2"
)
