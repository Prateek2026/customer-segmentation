"""
Simulated re-engagement experiment on the At Risk segment.

Splits At Risk customers into control/treatment, simulates a re-engagement
email lift for treatment, and tests whether the lift is statistically
significant with a two-proportion z-test (95% CI on the lift).
"""
import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep

OUTPUT_DIR = "output"
RANDOM_SEED = 42

rfm = pd.read_csv(f"{OUTPUT_DIR}/customer_rfm_segments.csv")
at_risk = rfm[rfm["Segment"] == "At Risk"].copy()
n = len(at_risk)
print(f"At Risk segment size: {n}")

# ---------------------------------------------------------------------------
# 1. Random control/treatment split
# ---------------------------------------------------------------------------
rng = np.random.default_rng(RANDOM_SEED)
at_risk["group"] = rng.choice(["control", "treatment"], size=n, p=[0.5, 0.5])

# ---------------------------------------------------------------------------
# 2. Simulate reactivation outcome
#    Baseline reactivation rate for At Risk customers (control): 12%.
#    Treatment (re-engagement email) adds a synthetic +8pp lift: 20%.
# ---------------------------------------------------------------------------
BASE_RATE = 0.12
LIFT = 0.08

at_risk["reactivated"] = 0
control_idx = at_risk["group"] == "control"
treatment_idx = at_risk["group"] == "treatment"

at_risk.loc[control_idx, "reactivated"] = rng.binomial(1, BASE_RATE, control_idx.sum())
at_risk.loc[treatment_idx, "reactivated"] = rng.binomial(1, BASE_RATE + LIFT, treatment_idx.sum())

summary = at_risk.groupby("group")["reactivated"].agg(["sum", "count", "mean"])
summary.columns = ["reactivated_count", "group_size", "reactivation_rate"]
print("\nGroup summary:")
print(summary)

# ---------------------------------------------------------------------------
# 3. Two-proportion z-test
# ---------------------------------------------------------------------------
count = [summary.loc["treatment", "reactivated_count"], summary.loc["control", "reactivated_count"]]
nobs = [summary.loc["treatment", "group_size"], summary.loc["control", "group_size"]]

z_stat, p_value = proportions_ztest(count, nobs, alternative="larger")
ci_low, ci_high = confint_proportions_2indep(count[0], nobs[0], count[1], nobs[1], method="wald")

observed_lift = summary.loc["treatment", "reactivation_rate"] - summary.loc["control", "reactivation_rate"]

print(f"\nObserved lift: {observed_lift:.4f} ({observed_lift*100:.1f} pp)")
print(f"z-statistic: {z_stat:.3f}")
print(f"p-value (one-sided, treatment > control): {p_value:.4f}")
print(f"95% CI on lift: [{ci_low:.4f}, {ci_high:.4f}]")

# ---------------------------------------------------------------------------
# 4. Save results
# ---------------------------------------------------------------------------
at_risk.to_csv(f"{OUTPUT_DIR}/at_risk_experiment.csv", index=False)

result_row = pd.DataFrame([{
    "control_rate": summary.loc["control", "reactivation_rate"],
    "treatment_rate": summary.loc["treatment", "reactivation_rate"],
    "observed_lift": observed_lift,
    "z_stat": z_stat,
    "p_value": p_value,
    "ci_low": ci_low,
    "ci_high": ci_high,
}])
result_row.to_csv(f"{OUTPUT_DIR}/experiment_significance_result.csv", index=False)
print(f"\nSaved: {OUTPUT_DIR}/at_risk_experiment.csv, {OUTPUT_DIR}/experiment_significance_result.csv")
