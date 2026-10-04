# Submission Form

## 1. What did you build, and what business outcome does it move?

I built a reproducible Python and pandas report that analyses first-response SLA breaches weekly by agent and shift.

The current run analysed **11,200 deduplicated tickets** and found:

- **2,440 breaches**
- **21.79% overall breach rate**
- **Rs 350 credit per breach**
- **Rs 854,000 estimated current SLA credit exposure**

The recommended operational goal is to reduce the breach rate from **21.79% to 15%** while maintaining the current headcount.

At the current ticket volume, this would reduce expected breaches from 2,440 to 1,680:

- **760 potentially avoidable breaches**
- **Rs 266,000 potentially avoidable SLA credits**

This represents approximately **Rs 44,000 per quarter** when distributed across the six quarters covered by the dataset. This is a planning estimate, not a guaranteed saving.

## 2. What does one run cost?

No paid AI or API calls were used by the report.

- **Cost per run:** Rs 0
- **Estimated monthly API cost:** Rs 0
- **Execution:** Local Python and pandas environment

## 3. How do you know it works?

The report completed successfully and produced the following output files:

- `weekly_breach_by_agent.csv`
- `weekly_breach_by_shift.csv`
- `cleaned_ticket_sla_data.csv`

I verified that:

- The cleaned ticket count was 11,200.
- The breach count was 2,440.
- The breach rate was 21.79%.
- The breach rate matched the breach count divided by the ticket count.
- The output files contained weekly agent and shift results.
- Channel-specific SLA targets were applied correctly.

I also manually checked a sample of 30 tickets by comparing each response time with the applicable channel SLA target.

- **Sample size:** 30 tickets
- **Mismatches:** 0
- **Validation error rate:** 0%
- **Failure cases:** None identified

The main remaining error risks are timestamp conversion, overnight shifts, roster date ranges, duplicate tickets, and tickets with no first response. These should be reviewed before production use.

## 4. Did you change, narrow, or push back on the client's ask?

I kept the requested weekly breach reports by agent and shift.

I did not use ticket-text AI classification because the requested result can be produced more reliably using deterministic timestamp, roster, and SLA logic.

I also recommend reviewing ticket volume alongside breach rate so that agents or shifts with very small ticket counts are not judged unfairly.

## 5. What is wrong with what you are handing us?

- Tickets without a first response are treated as breaches.
- The output is descriptive and should not be used alone for disciplinary decisions.
- The 30-ticket manual validation sample had zero mismatches, but broader validation is still recommended before production use.
- Overnight shift boundaries and roster transitions need additional review.
- The current report does not analyse ticket text.
- The report has not been packaged as a production service.
- The Rs 266,000 avoidable-credit figure is an estimate based on achieving a 15% breach rate; it is not guaranteed savings.

## 6. What did you deliberately leave out, and why?

I left out AI analysis of customer and agent text because it was not necessary for calculating first-response SLA breaches. Including it would add cost, complexity, and another potential source of error.

I also did not use the order, customer, or product reference tables because they were not required for the requested agent-and-shift SLA report.

## 7. Anything built or found that nobody asked for?

I included:

- Cleaned ticket-level SLA data
- Estimated current SLA credit exposure
- Potentially avoidable credit exposure at the 15% target
- A 30-ticket manual validation sample
- Documented assumptions and limitations
- A business memo summarising the operational recommendation

## 8. What did you use AI for?

I used AI assistance for planning, coding guidance, debugging, documentation, and review of the business interpretation.

No paid model or API calls were used in the final report. I did not use AI to classify ticket text.

Screen recording link:

PASTE_PUBLIC_GOOGLE_DRIVE_LINK_HERE

## 9. Someone picks this up on Monday. What are the three things they need to know?

1. Run `python breach_report.py` from the project root after installing pandas.
2. Review both ticket volume and breach rate before taking action on an agent or shift.
3. Validate timestamp conversion, overnight shifts, duplicate handling, roster transitions, and no-response tickets before production use.

## 10. Honest hours spent

3.5 Hours

## 11. GitHub repository link

https://github.com/gowrisankarr04/vireo-sla-project.git
