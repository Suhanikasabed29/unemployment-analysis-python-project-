<<<<<<< HEAD
# Unemployment Analysis with Python

## Project objective
This project analyzes unemployment-rate data from India using Python only. It:
- cleans and validates the supplied CSV datasets
- explores unemployment, employment, and labour participation
- visualizes unemployment trends
- investigates the COVID-19 period
- identifies regional, rural/urban, and seasonal patterns
- produces CSV summaries and PNG charts
- creates a text report with policy-relevant observations

## Dataset used
The project uses the two CSV files supplied in the original ZIP:
1. `Unemployment in India.csv`
2. `Unemployment_Rate_upto_11_2020.csv`

The first file contains monthly regional data with Rural/Urban area information. The second provides a separate 2020 monthly regional dataset.

## Requirements
- Python 3.9+
- pandas
- numpy
- matplotlib

Install:
```bash
pip install -r requirements.txt
```

## Run
From this project folder:
```bash
python main.py
```

The script automatically:
1. loads both CSV files
2. cleans column names, dates, missing values and numeric fields
3. saves cleaned datasets
4. calculates national/monthly, regional and COVID-period summaries
5. creates charts
6. writes `outputs/analysis_report.txt`

## Output files
### CSV
- `outputs/cleaned_unemployment_india.csv`
- `outputs/cleaned_unemployment_2020.csv`
- `outputs/monthly_national_trend.csv`
- `outputs/region_summary.csv`
- `outputs/covid_impact_summary.csv`
- `outputs/seasonal_month_summary.csv`
- `outputs/rural_urban_summary.csv`

### Charts
- `01_national_unemployment_trend.png`
- `02_covid_impact.png`
- `03_top_regions_average_unemployment.png`
- `04_rural_vs_urban.png`
- `05_seasonal_pattern.png`
- `06_employment_vs_unemployment.png`

## Important interpretation note
The COVID-period comparison is descriptive, not a causal econometric estimate. The supplied data can show changes in unemployment around 2020, but it cannot by itself prove that COVID-19 was the only cause.

## Suggested viva points
- `pandas` is used for data loading, cleaning, grouping and aggregation.
- `numpy` supports numerical calculations.
- `matplotlib` is used for all visualizations.
- Missing values are handled by removing rows that do not contain the required analysis fields.
- Dates are converted to datetime so monthly trends can be analyzed.
- The COVID comparison uses pre-COVID observations versus the April-June 2020 period in the detailed dataset.
- Rural and Urban observations are compared where the detailed dataset contains the `Area` column.
=======
# unemployment-analysis-python-project-
>>>>>>> 54af35b6cf839632c195863f57ebc207618c570b
