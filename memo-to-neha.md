# Vireo Audio SLA Breach Report

**To:** Neha Kulkarni, Support Operations Manager  
**Subject:** Weekly First-Response SLA Breach Report

## Summary

I built a reproducible Python and pandas report to identify first-response SLA breaches by agent and shift on a weekly basis.

The report:

- Converts ticket timestamps from UTC to IST.
- Removes duplicate migration records, prioritising the current helpdesk record.
- Matches each ticket to the correct roster assignment using the ticket creation date.
- Applies the channel-specific first-response SLA targets.
- Produces weekly reports by agent and shift, including ticket volume and breach rate.

## Current results

The analysis covers **11,200 deduplicated tickets**.

- **Total SLA breaches:** 2,440
- **Overall breach rate:** 21.79%
- **Credit per breach:** Rs 350
- **Estimated current SLA credit exposure:** Rs 854,000

The channel SLA targets used are:

- **Chat:** 15 minutes
- **Voice:** 120 minutes
- **Social:** 240 minutes
- **Email:** 480 minutes

Tickets without a first response are treated as SLA breaches.

## Recommended business goal

Reduce the overall breach rate from **21.79% to 15%** while maintaining the current headcount.

At the current volume of 11,200 tickets:

- Breaches at a 15% target: **1,680**
- Current breaches: **2,440**
- Avoidable breaches: **760**
- Potentially avoidable SLA credits: **Rs 266,000**

This is an operational target rather than a guaranteed saving. It assumes the ticket volume and credit policy remain unchanged.

The dataset covers approximately six quarters. If the potential avoidable amount is distributed evenly across that period:

- **Rs 266,000 ÷ 6 quarters = approximately Rs 44,333 per quarter**
- Rounded planning estimate: **approximately Rs 44,000 per quarter**

The current Rs 854,000 figure represents estimated credit exposure, not savings. The Rs 266,000 figure represents the potential avoidable portion if the breach rate is reduced to 15%.

## Recommended action

Review the weekly agent and shift reports with team leads. Prioritise high-volume groups with consistently high breach rates rather than groups with small ticket samples.

The review should focus on:

- Queue timing and backlog accumulation
- Handoffs between agents and teams
- Overnight coverage and morning backlog
- Channel-specific workload
- Roster and shift alignment
- Repeated patterns across multiple weeks

These results should be used to improve queue management, coverage, and handoffs—not to blame individual agents. Staffing changes should not be assumed, since the current headcount is frozen.

## Validation

I manually checked a random sample of **30 tickets** from the cleaned SLA dataset. For each ticket, I recalculated the breach decision by comparing its response time with the applicable channel SLA target.

- **Sample size:** 30 tickets
- **Mismatches:** 0
- **Validation error rate:** 0%
- **Failure cases:** None identified

All 30 sampled breach decisions matched the documented SLA rules.

## Limitations and assumptions

- Tickets without a first response are treated as breaches.
- Duplicate migration records are removed by keeping the current helpdesk record over the legacy record.
- Roster assignments are matched using the ticket creation date in IST.
- Results depend on the quality of the ticket timestamps, channel values, and roster dates.
- The report uses deterministic timestamp, roster, and policy logic.
- AI classification was not used because free-text classification was not necessary for calculating the requested SLA metrics.
- The 15% target and Rs 266,000 avoidable-credit estimate are planning assumptions, not guaranteed financial savings.

## Output files

The report produces the following files:

- `weekly_breach_by_agent.csv`
- `weekly_breach_by_shift.csv`
- `cleaned_ticket_sla_data.csv`
