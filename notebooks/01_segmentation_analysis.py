"""
Customer Segmentation: RFM scoring + K-Means clustering validation.

Reads customer_rfm from the SQLite DB (built by sql/01 and sql/02),
scores customers into RFM segments, validates the segmentation with
K-Means clustering, and writes outputs used by the experiment step
and the Power BI dashboard.
"""
import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

DB_PATH = "data/online_retail.db"
OUTPUT_DIR = "output"

# ---------------------------------------------------------------------------
# 1. Load RFM table
# ---------------------------------------------------------------------------
conn = sqlite3.connect(DB_PATH)
rfm = pd.read_sql("SELECT * FROM customer_rfm", conn)
conn.close()

# ---------------------------------------------------------------------------
# 2. Score & segment (quartile-based RFM score)
# ---------------------------------------------------------------------------
# Recency: lower is better -> reverse the quartile labels.
rfm["R_score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1]).astype(int)
rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["M_score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]


def label_segment(row):
    r, f, m = row["R_score"], row["F_score"], row["M_score"]
    if r >= 3 and f >= 3 and m >= 3:
        return "Champions"
    if r >= 3 and f >= 2:
        return "Loyal"
    if r <= 2 and f >= 3:
        return "At Risk"
    if r <= 2 and f <= 2 and m <= 2:
        return "Dormant"
    return "New"


rfm["Segment"] = rfm.apply(label_segment, axis=1)

print("Segment sizes:")
print(rfm["Segment"].value_counts())

# ---------------------------------------------------------------------------
# 3. Clustering validation (K-Means on standardized, log-transformed RFM)
# ---------------------------------------------------------------------------
# Frequency and Monetary are heavily right-skewed (a handful of whale
# customers). Without a log transform, K-Means/silhouette just isolates
# those outliers into their own cluster instead of finding real segments.
rfm_log = pd.DataFrame({
    "Recency": rfm["Recency"],
    "Frequency": np.log1p(rfm["Frequency"]),
    "Monetary": np.log1p(rfm["Monetary"].clip(lower=0)),
})
X = StandardScaler().fit_transform(rfm_log)

inertias, silhouettes = [], []
k_range = range(2, 8)
for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X, km.labels_))

print("\nk : inertia (elbow) : silhouette")
for k, i, s in zip(k_range, inertias, silhouettes):
    print(f"{k} : {i:.1f} : {s:.3f}")

# Pick k by silhouette, but excluding k=2 which tends to just be a
# degenerate outlier-vs-everyone split rather than an actionable segmentation.
candidates = [(k, s) for k, s in zip(k_range, silhouettes) if k >= 3]
best_k = max(candidates, key=lambda t: t[1])[0]
print(f"\nChosen k = {best_k} (highest silhouette score among k>=3, "
      f"avoiding the degenerate 2-cluster outlier split)")

final_km = KMeans(n_clusters=best_k, random_state=42, n_init=10).fit(X)
rfm["Cluster"] = final_km.labels_

# Sanity-check clusters against manual RFM segments
print("\nCluster vs manual segment crosstab:")
print(pd.crosstab(rfm["Cluster"], rfm["Segment"]))

# ---------------------------------------------------------------------------
# 4. Save outputs
# ---------------------------------------------------------------------------
rfm.to_csv(f"{OUTPUT_DIR}/customer_rfm_segments.csv", index=False)

elbow_df = pd.DataFrame({"k": list(k_range), "inertia": inertias, "silhouette": silhouettes})
elbow_df.to_csv(f"{OUTPUT_DIR}/kmeans_elbow_silhouette.csv", index=False)

print(f"\nSaved: {OUTPUT_DIR}/customer_rfm_segments.csv, {OUTPUT_DIR}/kmeans_elbow_silhouette.csv")
