---
sidebar_position: 2
---

# Customer Lifecycle Management

## Overview

The Customer Lifecycle Workflows feature in Grow allows you to define automated transitions between customer states. This helps manage customer engagement systematically.

## Accessing Lifecycle Workflows

In the Grow module, click the lifecycle icon or navigate to the workflow configuration from the customer groups panel.

## Lifecycle States

![Lifecycle Workflows](/screenshots/campaigns/lifecycle-workflows.jpg)

Customers move through predefined lifecycle states:

| Current State | Transition | Target State |
|--------------|------------|-------------|
| Activated | → | Cold |
| Active | → | PPV (Post-Purchase Visit) |
| Cold | → | Any |
| Dormant | → | Active |
| High Invoices | → | PPV |
| Irrelevant | → | PPO / PP |
| Low Payment | → | PPV |
| New Lead | → | Irrelevant / Warm |
| To Be Inactive | → | PPV |
| Warm | → | Irrelevant / New Lead |

## Adding Groups

![Add Group Dialog](/screenshots/campaigns/add-group.jpg)

To create a new customer group:

1. Click **Add New Group**
2. Enter a group name
3. Configure the customer selection criteria
4. Click **Add Group** to create

## Group Settings

Each group can be configured with:

- **Name** — A descriptive name for the group
- **Filters** — Customer attributes to include (e.g., Vehicle Type, CFA)
- **Actions** — Default actions for group members

![Group Settings](/screenshots/campaigns/group-settings.jpg)

## Tips

- Define clear lifecycle transitions to automate customer engagement
- Review dormant customers regularly for re-activation campaigns
- Use lifecycle workflows to ensure consistent follow-up across all customer segments
