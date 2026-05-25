# ACIS Insurance Risk Analytics — Final Report

*(Medium-style write-up. Fill in once Tasks 3 and 4 are executed against the real dataset.)*

## 1. Executive summary (for ACIS leadership)
- **Question we set out to answer.**
- **What we found, in one paragraph, no jargon.**
- **What ACIS should do differently next quarter.**

## 2. Approach
- 18 months of policy + claim data (Feb 2014 – Aug 2015).
- Two anchor metrics: **Loss Ratio** (`TotalClaims / TotalPremium`) and **Margin** (`TotalPremium - TotalClaims`).
- Pipeline: EDA → A/B hypothesis testing → severity + claim-probability models → risk-based premium.
- All artefacts versioned in Git; data versioned in DVC for auditability.

## 3. Key insights from EDA
*(Populated from `notebooks/01_eda.ipynb`. Each bullet should reference a chart.)*
- Portfolio loss ratio: …
- Province-level dispersion: …
- Vehicle make/age effects: …
- Temporal trend over the 18-month window: …
- Notable data-quality issues and how we handled them.

## 4. Hypothesis-testing results
*(Populated from `notebooks/02_hypothesis_testing.ipynb`.)*

| Hypothesis | KPI | Test | p-value | Decision | Business reading |
| --- | --- | --- | --- | --- | --- |
| H1: No risk diff across provinces | Severity, Frequency | ANOVA + chi-squared | … | … | … |
| H2: No risk diff between zip codes | Frequency | chi-squared | … | … | … |
| H3: No margin diff between zip codes | Margin | Welch t-test | … | … | … |
| H4: No risk diff Men vs Women | Frequency, Severity | z-test, t-test | … | … | … |

For each rejected H0, write one sentence on direction + magnitude + recommendation.

## 5. Predictive models
*(Populated from `notebooks/03_modeling.ipynb`.)*

**Severity model** — `TotalClaims` on claimants only.

| Model | RMSE | R² |
| --- | --- | --- |
| Linear Regression | … | … |
| Random Forest | … | … |
| XGBoost | … | … |

**Claim probability model** — binary classification on full portfolio.

| Model | Accuracy | Precision | Recall | F1 | ROC AUC |
| --- | --- | --- | --- | --- | --- |
| Logistic Regression | … | … | … | … | … |
| Random Forest | … | … | … | … | … |
| XGBoost | … | … | … | … | … |

**Risk-based premium**: `P(claim) × Predicted severity + Expense loading + Profit margin`.
Compare to `CalculatedPremiumPerTerm` for a sample of policies and discuss where the model would re-price.

## 6. Feature importance (SHAP)
Top 5–10 features with short business reading for each:
1. …
2. …

## 7. Recommendations
- Pricing: …
- Marketing / acquisition: …
- Underwriting guardrails: …

## 8. Limitations & next steps
- Data window: 18 months — seasonality only partially observable.
- Synthetic-data fallback used for CI; production findings depend on the real ACIS extract.
- Future work: external macro features, telematics, fraud signals.
