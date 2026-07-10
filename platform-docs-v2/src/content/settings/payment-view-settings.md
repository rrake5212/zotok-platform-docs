---
sidebar_position: 2
---

# Payment View Settings

## Overview

The Payment View Settings overlay allows you to configure how receivable ageing is calculated and displayed.

## Accessing Settings

Click **Payments** (💳 icon) in the left navigation sidebar to open the settings overlay.

## Configuration Options

### Ageing Calculation

- **Ageing By** — Choose the basis for ageing calculation:
  - **Due Date** — Age from the invoice due date
  - **Bill Date** — Age from the invoice bill date

### Ageing Bucket Ranges

Configure the ageing bucket ranges:

| Bucket | Range | Description |
|--------|-------|-------------|
| 1 | 0–10 Days | Current / near-term receivables |
| 2 | 11–20 Days | Early overdue |
| 3 | 21–30 Days | Moderate overdue |
| 4 | 31–40 Days | Attention required |
| 5 | 41–50 Days | Escalation needed |
| 6 | Over 50 Days | Critical — immediate follow-up |

### Empty State

When no invoices exist, the system displays: "No invoices to show."

## Actions

- **Save** — Apply your configuration
- **Cancel** — Discard changes and return to dashboard

## Tips

- Use **Due Date** ageing for better accuracy in payment tracking
- Review the "Over 50 Days" bucket daily for critical follow-ups
- Configure bucket ranges to match your organization's collection policies
