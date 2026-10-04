from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

CREDIT_PER_BREACH_INR = 350
TIMEZONE = "Asia/Kolkata"


# -----------------------------
# Load source data
# -----------------------------
tickets = pd.read_csv(DATA_DIR / "tickets.csv")
agents = pd.read_csv(DATA_DIR / "agents.csv")

print(f"Raw tickets loaded: {len(tickets):,}")


# -----------------------------
# Preserve raw response values
# so blank responses and invalid
# timestamps are not confused.
# -----------------------------
raw_response = tickets["first_response_at"].astype("string")

tickets["response_was_blank"] = (
    raw_response.isna()
    | raw_response.str.strip().eq("")
)


# -----------------------------
# Parse timestamps.
# The helpdesk API export is UTC.
# -----------------------------
time_columns = [
    "created_at",
    "first_response_at",
    "resolved_at",
]

for column in time_columns:
    tickets[column] = pd.to_datetime(
        tickets[column],
        errors="coerce",
        utc=True,
    ).dt.tz_convert(TIMEZONE)


tickets["created_timestamp_invalid"] = tickets["created_at"].isna()

tickets["response_timestamp_invalid"] = (
    tickets["first_response_at"].isna()
    & ~tickets["response_was_blank"]
)


# -----------------------------
# Remove migration duplicates.
# Prefer current helpdesk rows
# over legacy rows.
# -----------------------------
tickets["source_priority"] = tickets["source_system"].map(
    {
        "helpdesk": 0,
        "legacy_fd": 1,
    }
).fillna(2)

duplicate_rows_before = tickets["ticket_id"].duplicated().sum()

tickets = (
    tickets
    .sort_values(["ticket_id", "source_priority"])
    .drop_duplicates("ticket_id", keep="first")
    .copy()
)

duplicate_rows_removed = duplicate_rows_before

print(f"After deduplication: {len(tickets):,}")
print(f"Duplicate rows removed: {duplicate_rows_removed:,}")
print(
    "Duplicate ticket IDs remaining: "
    f"{tickets['ticket_id'].duplicated().sum():,}"
)


# -----------------------------
# Convert UTC timestamps to
# local IST dates for roster
# and weekly reporting.
# -----------------------------
tickets["created_date_ist"] = tickets["created_at"].dt.date


# -----------------------------
# SLA calculation
# -----------------------------
sla_minutes = {
    "chat": 15,
    "voice": 120,
    "social": 240,
    "email": 480,
}

tickets["sla_target_minutes"] = tickets["channel"].map(sla_minutes)

tickets["response_minutes"] = (
    tickets["first_response_at"] - tickets["created_at"]
).dt.total_seconds() / 60

tickets["response_before_creation"] = (
    tickets["response_minutes"] < 0
)

tickets["response_data_invalid"] = (
    tickets["response_timestamp_invalid"]
    | tickets["response_before_creation"]
)

# A genuinely blank first response is a breach.
# An invalid timestamp is excluded from the breach denominator.
tickets["breach"] = pd.Series(pd.NA, index=tickets.index, dtype="boolean")

valid_response_data = (
    ~tickets["response_data_invalid"]
    & tickets["sla_target_minutes"].notna()
    & tickets["created_at"].notna()
)

tickets.loc[valid_response_data, "breach"] = (
    tickets.loc[valid_response_data, "response_was_blank"]
    | (
        tickets.loc[valid_response_data, "response_minutes"]
        > tickets.loc[valid_response_data, "sla_target_minutes"]
    )
)

tickets["analysis_eligible"] = tickets["breach"].notna()


# -----------------------------
# Match each ticket to the
# correct roster assignment.
#
# We preserve unmatched tickets
# as "Unmatched roster" instead
# of silently deleting them.
# -----------------------------
agents["from_date"] = pd.to_datetime(
    agents["from_date"],
    errors="coerce",
).dt.date

agents["to_date"] = pd.to_datetime(
    agents["to_date"],
    errors="coerce",
).dt.date

roster_columns = [
    "agent_id",
    "name",
    "site",
    "team",
    "shift",
    "tier",
    "from_date",
    "to_date",
]

roster = agents[roster_columns].copy()

tickets["_ticket_row_id"] = range(len(tickets))

roster_candidates = tickets[
    [
        "_ticket_row_id",
        "agent_id",
        "created_date_ist",
    ]
].merge(
    roster,
    on="agent_id",
    how="left",
)

roster_candidates["date_matches_assignment"] = (
    roster_candidates["created_date_ist"].notna()
    & (
        roster_candidates["from_date"].isna()
        | (
            roster_candidates["created_date_ist"]
            >= roster_candidates["from_date"]
        )
    )
    & (
        roster_candidates["to_date"].isna()
        | (
            roster_candidates["created_date_ist"]
            <= roster_candidates["to_date"]
        )
    )
)

valid_roster_candidates = roster_candidates[
    roster_candidates["date_matches_assignment"]
].copy()

roster_match_counts = (
    valid_roster_candidates
    .groupby("_ticket_row_id")
    .size()
)

overlapping_ticket_count = int(
    (roster_match_counts > 1).sum()
)

# If overlapping rows exist, select the assignment with
# the latest starting date and report the overlap count.
selected_roster = (
    valid_roster_candidates
    .sort_values(
        ["_ticket_row_id", "from_date"],
        ascending=[True, False],
    )
    .drop_duplicates("_ticket_row_id", keep="first")
)

assignment_columns = [
    "_ticket_row_id",
    "name",
    "site",
    "team",
    "shift",
    "tier",
    "from_date",
    "to_date",
]

tickets = tickets.merge(
    selected_roster[assignment_columns],
    on="_ticket_row_id",
    how="left",
)

unmatched_roster_count = int(tickets["name"].isna().sum())

tickets["name"] = tickets["name"].fillna("Unmatched roster")
tickets["site"] = tickets["site"].fillna("Unmatched roster")
tickets["team"] = tickets["team"].fillna("Unmatched roster")
tickets["shift"] = tickets["shift"].fillna("Unmatched roster")
tickets["tier"] = tickets["tier"].fillna("Unknown")


print(f"Tickets without roster match: {unmatched_roster_count:,}")
print(f"Tickets with overlapping roster rows: {overlapping_ticket_count:,}")
print(
    "Duplicate ticket IDs after roster matching: "
    f"{tickets['ticket_id'].duplicated().sum():,}"
)


# -----------------------------
# Monday-start reporting weeks.
# W-SUN means each period ends
# Sunday and starts on Monday.
# -----------------------------
tickets["week_start"] = (
    tickets["created_at"]
    .dt.tz_localize(None)
    .dt.to_period("W-SUN")
    .dt.start_time
    .dt.date
)


# -----------------------------
# Use only valid rows for
# breach-rate reports.
# Unmatched roster tickets remain
# visible under "Unmatched roster".
# -----------------------------
report_tickets = tickets[
    tickets["analysis_eligible"]
].copy()

report_tickets["breach"] = (
    report_tickets["breach"]
    .astype(bool)
)


# -----------------------------
# Weekly report by agent
# -----------------------------
agent_report = (
    report_tickets
    .groupby(
        [
            "week_start",
            "agent_id",
            "name",
            "site",
            "team",
            "shift",
            "tier",
        ],
        dropna=False,
    )
    .agg(
        tickets=("ticket_id", "count"),
        breaches=("breach", "sum"),
        breach_rate=("breach", "mean"),
        average_response_minutes=("response_minutes", "mean"),
    )
    .reset_index()
)

agent_report["breach_rate"] = (
    agent_report["breach_rate"] * 100
).round(2)

agent_report["estimated_credit_cost_inr"] = (
    agent_report["breaches"] * CREDIT_PER_BREACH_INR
)


# -----------------------------
# Weekly report by shift
# -----------------------------
shift_report = (
    report_tickets
    .groupby(
        [
            "week_start",
            "site",
            "shift",
        ],
        dropna=False,
    )
    .agg(
        tickets=("ticket_id", "count"),
        breaches=("breach", "sum"),
        breach_rate=("breach", "mean"),
        average_response_minutes=("response_minutes", "mean"),
    )
    .reset_index()
)

shift_report["breach_rate"] = (
    shift_report["breach_rate"] * 100
).round(2)

shift_report["estimated_credit_cost_inr"] = (
    shift_report["breaches"] * CREDIT_PER_BREACH_INR
)


# -----------------------------
# Save reports
# -----------------------------
agent_report.to_csv(
    OUTPUT_DIR / "weekly_breach_by_agent.csv",
    index=False,
)

shift_report.to_csv(
    OUTPUT_DIR / "weekly_breach_by_shift.csv",
    index=False,
)

tickets.to_csv(
    OUTPUT_DIR / "cleaned_ticket_sla_data.csv",
    index=False,
)


# -----------------------------
# Final audit summary
# -----------------------------
total_tickets = len(report_tickets)
total_breaches = int(report_tickets["breach"].sum())
breach_rate = (
    total_breaches / total_tickets * 100
    if total_tickets
    else 0
)
invalid_rows = int((~tickets["analysis_eligible"]).sum())
estimated_credit_cost = total_breaches * CREDIT_PER_BREACH_INR

print()
print("Report completed successfully.")
print(f"Raw tickets: {len(tickets) + duplicate_rows_removed:,}")
print(f"Deduplicated tickets: {len(tickets):,}")
print(f"Tickets used in SLA analysis: {total_tickets:,}")
print(f"Excluded data-quality rows: {invalid_rows:,}")
print(f"Total breaches: {total_breaches:,}")
print(f"Overall breach rate: {breach_rate:.2f}%")
print(f"Estimated credit cost: Rs {estimated_credit_cost:,}")
print(f"Blank first responses: {tickets['response_was_blank'].sum():,}")
print(
    "Invalid first-response timestamps: "
    f"{tickets['response_timestamp_invalid'].sum():,}"
)
print(
    "Responses before ticket creation: "
    f"{tickets['response_before_creation'].sum():,}"
)
print(f"Duplicate rows removed: {duplicate_rows_removed:,}")
print(f"Unmatched roster rows: {unmatched_roster_count:,}")
print(f"Overlapping roster matches: {overlapping_ticket_count:,}")
print("Files saved in the output folder.")
