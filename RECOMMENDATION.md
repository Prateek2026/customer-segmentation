# One-Page Recommendation

**Hypothesis:** A targeted re-engagement email to At-Risk customers
increases their reactivation rate versus no intervention.

**Method:** Segmented 4,338 customers via RFM analysis (Recency, Frequency,
Monetary), validated the segmentation with K-Means clustering (k=3, chosen
by silhouette score). Isolated the At-Risk segment (650 customers, 15% of
the base, 12% of revenue), split it 50/50 into control and treatment, and
tested the reactivation rate difference with a two-proportion z-test.

**Result:** Treatment reactivated at 20.2% vs. 13.2% for control — a 7.1
percentage-point lift (95% CI: [1.4pp, 12.8pp], p = 0.008). The lift is
statistically significant at the 5% level.

**Business recommendation:** Roll out the re-engagement email to the full
At-Risk segment. At the observed lift, that recovers an estimated 46
additional customers who would otherwise stay dormant. Champions (30% of
customers) already drive 73% of revenue — protecting that segment from
churn should be the next priority once this campaign is validated with a
real (not simulated) send.
