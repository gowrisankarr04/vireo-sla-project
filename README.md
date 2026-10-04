# Vireo Audio SLA Breach Report

A pandas-based report showing first-response SLA breaches by agent and shift, summarized weekly.

## What this project does

The script:

- Reads ticket and agent-roster data.
- Matches each ticket to the correct agent assignment.
- Calculates whether the first-response SLA was breached.
- Produces weekly breach summaries by agent and shift.
- Saves the results in the `output/` folder.

## Requirements

- Python 3.9 or later
- pandas

Install pandas:

```powershell
python -m pip install pandas
```

## Input files

The private client data is not included in this public repository.

Put `tickets.csv`, `agents.csv` and the other files from the pack in a folder called `data/`, then run `python breach_report.py`.

The local project should look like this:

```text
vireo-sla-project/
├── breach_report.py
├── data/
│   ├── tickets.csv
│   ├── agents.csv
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── email-thread.txt
│   ├── support-policy.pdf
│   └── README.txt
└── output/
```

The `data/` folder is ignored by Git because it contains private client information.

## Run the report

Open PowerShell in the project folder and run:

```powershell
python breach_report.py
```

The report files will be created in the `output/` folder.

The main public summary files are:

```text
output/weekly_breach_by_agent.csv
output/weekly_breach_by_shift.csv
```

The processed ticket-level data and private validation files are not included in the public repository.

## Validation

A manual sample of tickets was checked against the report calculations. The validation notes record the sample checked, the comparison method, and known limitations.

## Public repository

https://github.com/gowrisankarr04/vireo-sla-project
