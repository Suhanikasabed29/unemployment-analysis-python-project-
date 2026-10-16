import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
CHART_DIR = os.path.join(OUTPUT_DIR, "charts")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

FILE_DETAILED = os.path.join(DATA_DIR, "Unemployment in India.csv")
FILE_2020 = os.path.join(DATA_DIR, "Unemployment_Rate_upto_11_2020.csv")

RATE_COL = "Estimated Unemployment Rate (%)"
EMP_COL = "Estimated Employed"
LPR_COL = "Estimated Labour Participation Rate (%)"


def clean_columns(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def clean_dataset(df):
    df = clean_columns(df)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    for col in [RATE_COL, EMP_COL, LPR_COL, "longitude", "latitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Frequency" in df.columns:
        df["Frequency"] = df["Frequency"].astype("string").str.strip()

    if "Region" in df.columns:
        df["Region"] = df["Region"].astype("string").str.strip()

    if "Area" in df.columns:
        df["Area"] = df["Area"].astype("string").str.strip()

    # Keep records with the core variables needed for analysis.
    required = [RATE_COL, EMP_COL, LPR_COL, "Date", "Region"]
    existing_required = [c for c in required if c in df.columns]
    df = df.dropna(subset=existing_required).copy()

    # Remove exact duplicates.
    df = df.drop_duplicates().reset_index(drop=True)
    return df


def save_csv(df, filename):
    df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False)


def monthly_national_trend(df):
    out = (
        df.groupby("Date", as_index=False)
        .agg(
            unemployment_rate=(RATE_COL, "mean"),
            employed=(EMP_COL, "mean"),
            labour_participation=(LPR_COL, "mean"),
            observations=(RATE_COL, "count"),
        )
        .sort_values("Date")
    )
    return out


def region_summary(df):
    out = (
        df.groupby("Region", as_index=False)
        .agg(
            avg_unemployment_rate=(RATE_COL, "mean"),
            min_unemployment_rate=(RATE_COL, "min"),
            max_unemployment_rate=(RATE_COL, "max"),
            avg_employed=(EMP_COL, "mean"),
            avg_labour_participation=(LPR_COL, "mean"),
            observations=(RATE_COL, "count"),
        )
        .sort_values("avg_unemployment_rate", ascending=False)
    )
    return out


def rural_urban_summary(df):
    if "Area" not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby("Area", as_index=False)
        .agg(
            avg_unemployment_rate=(RATE_COL, "mean"),
            avg_employed=(EMP_COL, "mean"),
            avg_labour_participation=(LPR_COL, "mean"),
            observations=(RATE_COL, "count"),
        )
        .sort_values("avg_unemployment_rate", ascending=False)
    )


def covid_summary(df):
    # Use the detailed dataset because it contains the longest continuous period
    # and Rural/Urban observations.
    x = df.copy()
    x["period"] = np.select(
        [
            x["Date"] < pd.Timestamp("2020-03-01"),
            x["Date"].between("2020-03-01", "2020-03-31"),
            x["Date"].between("2020-04-01", "2020-06-30"),
        ],
        ["Pre-COVID baseline", "March 2020", "April-June 2020"],
        default="Post-June 2020",
    )
    out = (
        x[x["period"].isin(["Pre-COVID baseline", "March 2020", "April-June 2020"])]
        .groupby("period", as_index=False)
        .agg(
            avg_unemployment_rate=(RATE_COL, "mean"),
            avg_employed=(EMP_COL, "mean"),
            avg_labour_participation=(LPR_COL, "mean"),
            observations=(RATE_COL, "count"),
        )
    )
    return out


def seasonal_summary(df):
    x = df.copy()
    x["month"] = x["Date"].dt.month
    out = (
        x.groupby("month", as_index=False)
        .agg(
            avg_unemployment_rate=(RATE_COL, "mean"),
            observations=(RATE_COL, "count"),
        )
    )
    month_names = {
        1:"January", 2:"February", 3:"March", 4:"April",
        5:"May", 6:"June", 7:"July", 8:"August",
        9:"September", 10:"October", 11:"November", 12:"December"
    }
    out["month_name"] = out["month"].map(month_names)
    return out


def plot_national_trend(monthly):
    plt.figure(figsize=(11, 5.5))
    plt.plot(monthly["Date"], monthly["unemployment_rate"], marker="o", linewidth=2)
    plt.axvline(pd.Timestamp("2020-03-01"), linestyle="--", linewidth=1.5, label="COVID period begins")
    plt.axvspan(pd.Timestamp("2020-04-01"), pd.Timestamp("2020-06-30"), alpha=0.12, label="Apr-Jun 2020")
    plt.title("Average Unemployment Rate Trend in India")
    plt.xlabel("Month")
    plt.ylabel("Unemployment Rate (%)")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "01_national_unemployment_trend.png"), dpi=180)
    plt.close()


def plot_covid(covid):
    plt.figure(figsize=(9, 5.5))
    plt.bar(covid["period"], covid["avg_unemployment_rate"])
    plt.title("Unemployment Before and During the COVID-19 Period")
    plt.xlabel("Period")
    plt.ylabel("Average Unemployment Rate (%)")
    plt.xticks(rotation=12)
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "02_covid_impact.png"), dpi=180)
    plt.close()


def plot_regions(regions):
    top = regions.head(10).sort_values("avg_unemployment_rate")
    plt.figure(figsize=(10, 6))
    plt.barh(top["Region"], top["avg_unemployment_rate"])
    plt.title("10 Regions with Highest Average Unemployment Rate")
    plt.xlabel("Average Unemployment Rate (%)")
    plt.ylabel("Region")
    plt.grid(axis="x", alpha=0.25)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "03_top_regions_average_unemployment.png"), dpi=180)
    plt.close()


def plot_rural_urban(ru):
    if ru.empty:
        return
    plt.figure(figsize=(7, 5))
    plt.bar(ru["Area"], ru["avg_unemployment_rate"])
    plt.title("Average Unemployment Rate: Rural vs Urban")
    plt.xlabel("Area")
    plt.ylabel("Average Unemployment Rate (%)")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "04_rural_vs_urban.png"), dpi=180)
    plt.close()


def plot_seasonal(seasonal):
    plt.figure(figsize=(10, 5.5))
    plt.plot(seasonal["month_name"], seasonal["avg_unemployment_rate"], marker="o", linewidth=2)
    plt.title("Seasonal Pattern in Average Unemployment Rate")
    plt.xlabel("Month")
    plt.ylabel("Average Unemployment Rate (%)")
    plt.xticks(rotation=35)
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "05_seasonal_pattern.png"), dpi=180)
    plt.close()


def plot_employment_relationship(df):
    monthly = (
        df.groupby("Date", as_index=False)
        .agg(unemployment_rate=(RATE_COL, "mean"), employed=(EMP_COL, "mean"))
        .sort_values("Date")
    )
    plt.figure(figsize=(9, 5.5))
    plt.scatter(monthly["unemployment_rate"], monthly["employed"], alpha=0.75)
    plt.title("Employment vs Unemployment Rate")
    plt.xlabel("Average Unemployment Rate (%)")
    plt.ylabel("Average Employed")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "06_employment_vs_unemployment.png"), dpi=180)
    plt.close()


def make_report(detailed, second, monthly, regions, covid, seasonal, ru):
    peak = monthly.loc[monthly["unemployment_rate"].idxmax()]
    low = monthly.loc[monthly["unemployment_rate"].idxmin()]

    pre = covid.loc[covid["period"] == "Pre-COVID baseline", "avg_unemployment_rate"]
    covid_period = covid.loc[covid["period"] == "April-June 2020", "avg_unemployment_rate"]

    pre_val = float(pre.iloc[0]) if len(pre) else np.nan
    covid_val = float(covid_period.iloc[0]) if len(covid_period) else np.nan
    change = covid_val - pre_val if pd.notna(pre_val) and pd.notna(covid_val) else np.nan

    top_region = regions.iloc[0] if len(regions) else None
    bottom_region = regions.iloc[-1] if len(regions) else None

    report = []
    report.append("UNEMPLOYMENT ANALYSIS WITH PYTHON")
    report.append("=" * 60)
    report.append("")
    report.append("1. DATASET OVERVIEW")
    report.append(f"- Detailed dataset rows after cleaning: {len(detailed)}")
    report.append(f"- Secondary 2020 dataset rows after cleaning: {len(second)}")
    report.append(f"- Detailed dataset date range: {detailed['Date'].min().date()} to {detailed['Date'].max().date()}")
    report.append(f"- Number of regions in detailed dataset: {detailed['Region'].nunique()}")
    report.append("")
    report.append("2. TREND FINDINGS")
    report.append(f"- Highest monthly average unemployment rate: {peak['unemployment_rate']:.2f}% in {peak['Date'].strftime('%B %Y')}.")
    report.append(f"- Lowest monthly average unemployment rate: {low['unemployment_rate']:.2f}% in {low['Date'].strftime('%B %Y')}.")
    report.append("")
    report.append("3. COVID-19 PERIOD")
    if pd.notna(pre_val) and pd.notna(covid_val):
        direction = "increase" if change >= 0 else "decrease"
        report.append(f"- Pre-COVID baseline average unemployment rate: {pre_val:.2f}%.")
        report.append(f"- April-June 2020 average unemployment rate: {covid_val:.2f}%.")
        report.append(f"- Descriptive change between these periods: {change:+.2f} percentage points ({direction}).")
    report.append("- This is a descriptive comparison. It does not establish that COVID-19 alone caused the observed change.")
    report.append("")
    report.append("4. REGIONAL PATTERNS")
    if top_region is not None:
        report.append(f"- Highest average unemployment region in this dataset: {top_region['Region']} ({top_region['avg_unemployment_rate']:.2f}%).")
    if bottom_region is not None:
        report.append(f"- Lowest average unemployment region in this dataset: {bottom_region['Region']} ({bottom_region['avg_unemployment_rate']:.2f}%).")
    report.append("")
    report.append("5. SEASONAL PATTERNS")
    if len(seasonal):
        high_month = seasonal.loc[seasonal["avg_unemployment_rate"].idxmax()]
        low_month = seasonal.loc[seasonal["avg_unemployment_rate"].idxmin()]
        report.append(f"- Highest average month: {high_month['month_name']} ({high_month['avg_unemployment_rate']:.2f}%).")
        report.append(f"- Lowest average month: {low_month['month_name']} ({low_month['avg_unemployment_rate']:.2f}%).")
    report.append("")
    report.append("6. RURAL/URBAN")
    if not ru.empty:
        for _, row in ru.iterrows():
            report.append(f"- {row['Area']}: average unemployment rate {row['avg_unemployment_rate']:.2f}%.")
    report.append("")
    report.append("7. POLICY-RELEVANT INSIGHTS")
    report.append("- Monitor unemployment at both national and regional levels because regional averages differ substantially.")
    report.append("- During sudden shocks, monthly labour-market monitoring can help identify rapid changes and support timely employment interventions.")
    report.append("- Rural and urban labour markets should be analyzed separately where the data supports that distinction.")
    report.append("- Seasonal variation can be considered when interpreting monthly unemployment movements.")
    report.append("- The results should be combined with wage, sector, inflation, migration and labour-force data before making policy decisions.")
    report.append("")
    report.append("8. LIMITATIONS")
    report.append("- The datasets cover a limited time window and therefore cannot represent long-run historical unemployment.")
    report.append("- The COVID comparison is observational and descriptive, not a causal impact study.")
    report.append("- Regional coverage differs between the supplied files.")
    report.append("- Average rates can hide important differences between states, cities, sectors and demographic groups.")
    report.append("")
    report.append("Generated by main.py using pandas, numpy and matplotlib.")

    with open(os.path.join(OUTPUT_DIR, "analysis_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report))


def main():
    print("Loading datasets...")

    detailed = pd.read_csv(FILE_DETAILED)
    second = pd.read_csv(FILE_2020)

    detailed = clean_dataset(detailed)
    second = clean_dataset(second)

    print("Cleaning completed.")

    save_csv(detailed, "cleaned_unemployment_india.csv")
    save_csv(second, "cleaned_unemployment_2020.csv")

    monthly = monthly_national_trend(detailed)
    regions = region_summary(detailed)
    covid = covid_summary(detailed)
    seasonal = seasonal_summary(detailed)
    ru = rural_urban_summary(detailed)

    save_csv(monthly, "monthly_national_trend.csv")
    save_csv(regions, "region_summary.csv")
    save_csv(covid, "covid_impact_summary.csv")
    save_csv(seasonal, "seasonal_month_summary.csv")
    if not ru.empty:
        save_csv(ru, "rural_urban_summary.csv")

    plot_national_trend(monthly)
    plot_covid(covid)
    plot_regions(regions)
    plot_rural_urban(ru)
    plot_seasonal(seasonal)
    plot_employment_relationship(detailed)

    make_report(detailed, second, monthly, regions, covid, seasonal, ru)

    print("\nProject completed successfully.")
    print(f"Outputs saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
