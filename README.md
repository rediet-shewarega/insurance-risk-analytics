# Insurance Risk Analytics & Predictive Modeling

End-to-end analytics project for **AlphaCare Insurance Solutions (ACIS)**: analyse 18 months of South African auto-insurance claim data (Feb 2014 – Aug 2015), validate risk hypotheses, and build risk-based pricing models.

## Business Context

ACIS is preparing for an aggressive growth phase in the South African auto-insurance market. The goals are to:

1. Identify **low-risk customer segments** where premiums can be reduced to attract new clients.
2. **Statistically validate** hypotheses about risk drivers (province, zip code, gender).
3. Build **predictive models** for claim severity and claim probability that feed a dynamic, risk-based premium.
4. Deliver clear **business-facing recommendations**.

## Key Metrics

- **Loss Ratio** = `TotalClaims / TotalPremium` — portfolio profitability.
- **Margin** = `TotalPremium − TotalClaims` — per-policy profit contribution.
- **Claim Frequency** — proportion of policies with at least one claim.
- **Claim Severity** — mean claim amount given a claim occurred.

## Project Structure

```
insurance-risk-analytics/
├── .github/workflows/ci.yml      # Lint + tests on every push
├── data/                         # DVC-tracked, not in Git
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_hypothesis_testing.ipynb
│   └── 03_modeling.ipynb
├── src/                          # Reusable Python modules
│   ├── data_loader.py
│   ├── eda_utils.py
│   ├── hypothesis_tests.py
│   └── modeling.py
├── reports/final_report.md
├── tests/
├── dvc.yaml
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Clone & enter the repo
git clone <repo-url> && cd insurance-risk-analytics

# 2. Create a virtual environment
python -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull the data from the DVC remote
dvc pull
```

## Reproducing the Data Pipeline (DVC)

Data is versioned with **DVC** so every analysis is reproducible.

```bash
# 1) Install deps (DVC is in requirements.txt)
pip install -r requirements.txt

# 2) Point DVC at your local remote (one-time, path is *outside* the repo)
mkdir -p ~/dvc-storage/acis
dvc remote modify localstorage url ~/dvc-storage/acis   # or `dvc remote add -d ...` on a fresh checkout

# 3) Pull tracked datasets (raw + cleaned synthetic versions are tracked in this repo)
dvc pull
```

### Versions tracked

| File                                  | Version | Description |
| ------------------------------------- | ------- | ----------- |
| `data/insurance_data_synth.csv`       | raw     | Synthetic dataset matching the ACIS schema (smoke tests + CI) |
| `data/insurance_data_synth_cleaned.csv` | cleaned | Outliers winsorised at the 99.5th percentile, invalid rows dropped |

When the real ACIS dataset is provided, drop it into `data/insurance_data.csv` and re-run:

```bash
dvc add data/insurance_data.csv
git add data/insurance_data.csv.dvc
git commit -m "data: track ACIS raw extract"
dvc push
```

### Reproducible pipeline (`dvc repro`)

`dvc.yaml` defines two stages: `generate_synthetic` and `clean`. Run the whole DAG with:

```bash
dvc repro
```

## Workflow

| Task   | Branch   | Deliverable                                 |
| ------ | -------- | ------------------------------------------- |
| Task 1 | `task-1` | EDA notebook + reusable utils + CI pipeline |
| Task 2 | `task-2` | DVC-tracked data + remote                   |
| Task 3 | `task-3` | A/B hypothesis tests + results table        |
| Task 4 | `task-4` | Severity + claim-probability models + SHAP  |

Each task is merged into `main` via a Pull Request.

## Commands

```bash
# Lint
ruff check src tests

# Format check
black --check src tests

# Run tests
pytest -q
```
