# Customer Segmentation & Re-Engagement Experiment

RFM segmentation of an online retailer's customer base, validated with K-Means
clustering, plus a simulated re-engagement campaign tested for statistical
significance.

## Business question

Which customers are worth targeting, and does a re-engagement campaign
actually move the needle for at-risk customers — or is any observed lift
just noise?

## Data

[UCI "Online Retail" dataset](https://archive.ics.uci.edu/dataset/352/online+retail):
~542K transactions from a UK-based online retailer, Dec 2010–Dec 2011.

## Method

1. **Clean** (`sql/01_clean_transactions.sql`) — drop cancelled invoices
   (`InvoiceNo LIKE 'C%'`), missing `CustomerID`, non-positive quantity/price.
   397,884 clean rows from 541,909 raw rows.
2. **RFM aggregation** (`sql/02_rfm_aggregation.sql`) — Recency (days since
   last purchase vs. a snapshot date), Frequency (distinct invoices),
   Monetary (sum of line revenue), per customer. 4,338 customers.
3. **Score & segment** (`notebooks/01_segmentation_analysis.py`) — quartile
   RFM scores mapped to Champions / Loyal / At Risk / Dormant / New.
4. **Cluster validation** — K-Means on log-transformed, standardized RFM
   values (log transform needed because Frequency/Monetary are heavily
   right-skewed; without it, K-Means just isolates a handful of whale
   customers). k chosen via silhouette score among k≥3 — k=2 was excluded
   as a degenerate outlier-vs-everyone split. Final k=3 clusters line up
   reasonably with the manual RFM segments.
5. **Simulated experiment** (`notebooks/02_experiment_significance_test.py`)
   — At Risk segment split 50/50 into control/treatment; treatment gets a
   synthetic +8pp reactivation lift to simulate a re-engagement email effect.
   Tested with a two-proportion z-test.
6. **Dashboard export** (`notebooks/03_export_dashboard_data.py`) — three
   CSVs for Power BI: segment overview, RFM distribution, campaign result.

## Result

- Control reactivation rate: **13.2%**, Treatment: **20.2%**
- Observed lift: **7.1 percentage points**
- **p = 0.008** (one-sided z-test), 95% CI on lift: **[1.4pp, 12.8pp]**
- Champions are 30% of customers but **73% of revenue** — segmentation
  confirms revenue is highly concentrated in a small group.

## Recommendation

Targeting the At-Risk segment with a re-engagement email lifts reactivation
rate by 7.1 points (95% CI: [1.4, 12.8], p = 0.008) — statistically
significant at the 5% level. Recommend rolling out to the full At-Risk
segment (650 customers); at the observed lift, that's ~46 additional
reactivated customers.

## Repo structure

```
data/                 raw + SQLite DB (not committed if large — see .gitignore)
sql/                  cleaning + RFM aggregation queries
notebooks/            analysis scripts (segmentation, experiment, dashboard export)
output/               intermediate CSVs (full RFM table, experiment detail)
dashboard_data/       final CSVs consumed by the Power BI dashboard
```

## Power BI dashboard

Built from the CSVs in `dashboard_data/`:
1. **Segment overview** — customer count and revenue % per segment (bar chart)
2. **RFM distribution** — scatter/histogram of Recency, Frequency, Monetary colored by segment
3. **Campaign result** — control vs. treatment reactivation rate with 95% CI error bars

## What I'd do differently with more time/data

Run a real A/B test instead of a simulated split, and build a proper
customer lifetime value model instead of using raw Monetary as a proxy.
