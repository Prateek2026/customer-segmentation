"""
Builds the three CSV tables Power BI needs for the dashboard:
  1. segment_overview.csv   - size & revenue contribution per segment
  2. rfm_distribution.csv   - per-customer RFM values + segment for distribution charts
  3. campaign_result.csv    - control vs treatment reactivation rate + CI
"""
import pandas as pd

OUTPUT_DIR = "output"
DASH_DIR = "dashboard_data"

rfm = pd.read_csv(f"{OUTPUT_DIR}/customer_rfm_segments.csv")
experiment_result = pd.read_csv(f"{OUTPUT_DIR}/experiment_significance_result.csv")
experiment_detail = pd.read_csv(f"{OUTPUT_DIR}/at_risk_experiment.csv")

# 1. Segment overview: size + revenue contribution
segment_overview = (
    rfm.groupby("Segment")
    .agg(customer_count=("CustomerID", "count"), total_revenue=("Monetary", "sum"))
    .reset_index()
)
segment_overview["pct_of_customers"] = (
    segment_overview["customer_count"] / segment_overview["customer_count"].sum() * 100
).round(1)
segment_overview["pct_of_revenue"] = (
    segment_overview["total_revenue"] / segment_overview["total_revenue"].sum() * 100
).round(1)
segment_overview.to_csv(f"{DASH_DIR}/segment_overview.csv", index=False)

# 2. RFM distribution: per-customer values for histograms/scatter
rfm_distribution = rfm[["CustomerID", "Recency", "Frequency", "Monetary", "Segment", "Cluster"]]
rfm_distribution.to_csv(f"{DASH_DIR}/rfm_distribution.csv", index=False)

# 3. Campaign result: control vs treatment bar + CI
campaign_summary = (
    experiment_detail.groupby("group")["reactivated"]
    .agg(["mean", "count"])
    .reset_index()
    .rename(columns={"mean": "reactivation_rate", "count": "group_size"})
)
campaign_summary["ci_low"] = None
campaign_summary["ci_high"] = None
campaign_summary.loc[campaign_summary["group"] == "treatment", "ci_low"] = experiment_result["ci_low"].iloc[0] + campaign_summary.loc[campaign_summary["group"] == "control", "reactivation_rate"].iloc[0]
campaign_summary.loc[campaign_summary["group"] == "treatment", "ci_high"] = experiment_result["ci_high"].iloc[0] + campaign_summary.loc[campaign_summary["group"] == "control", "reactivation_rate"].iloc[0]
campaign_summary["p_value"] = experiment_result["p_value"].iloc[0]
campaign_summary.to_csv(f"{DASH_DIR}/campaign_result.csv", index=False)

print("Wrote dashboard_data/segment_overview.csv, rfm_distribution.csv, campaign_result.csv")
print("\nsegment_overview:\n", segment_overview)
print("\ncampaign_result:\n", campaign_summary)
