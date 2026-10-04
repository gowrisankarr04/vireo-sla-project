# Vireo Audio SLA Breach Report

## Purpose

This project analyses customer-support tickets and reports first-response SLA breaches by agent and shift, weekly.

## SLA rules

| Channel | Target |
|---|---:|
| Chat | 15 minutes |
| Voice | 2 hours |
| Social | 4 hours |
| Email | 8 hours |

Each SLA breach is estimated at Rs 350 in customer credit cost.

## How to run

Install the dependency:

```powershell
python -m pip install pandas
