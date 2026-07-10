---
sidebar_position: 1
---

# Queries Management

## Overview

The Queries Management section provides a comprehensive list of all configured query types. Each query type defines a conversation category and its associated action items.

## Queries List

The queries table displays configured queries (45 total, paginated 20 per page):

| S.No | Query Name | Action Items | Last Used | Updated On |
|------|-----------|-------------|-----------|------------|
| 1 | Bulk Order Negotiation | Create Order | 19 min ago | 6 Jul 2026 |
| 2 | Conversation Initiation | Request Payment | 19 min ago | 6 Jul 2026 |
| 3 | Create Order | Upload Invoice, Create Order, Send Order Receipt | 19 min ago | 6 Jul 2026 |
| 4 | Payment Follow-up | Send Payment Receipt | 22 hrs ago | 5 Jul 2026 |
| 5 | Product Catalogue / Browsing Request | N.A. | 1 hr ago | 6 Jul 2026 |

![Queries Overlay](/screenshots/queries/08_Overlay_Menu_enhanced.jpg)

## Viewing Query Details

Click any query row to open the details overlay showing:

- **Query Name** — The category name
- **Description** — What this query type covers
- **Action Items** — Available actions (Create Order, Send Invoice, Request Payment, etc.)

## Adding a New Query Type

1. Click the **Add Query** button
2. Fill in the form fields:

| Field | Required | Description |
|-------|----------|-------------|
| Query Name * | Yes | A unique name for the query type |
| Prompt * | Yes | Instruction/prompt associated with this query |
| Actions | Optional | Select from available message actions |

![Add Query Form](/screenshots/queries/09_Form_Entry_enhanced.jpg)

3. Click **Save** to add the query
4. Click **Cancel** to discard

## Tips

- Configure query types upfront for automatic conversation routing
- Regularly review and update query types to match evolving business needs
- Use descriptive names for easy identification in Threads
