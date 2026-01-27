# Agents

This directory defines domain agents and how they should operate. Use these
responsibilities as the basis for Cursor agent prompts.

## Standard output format

Every agent output should include:

1. Summary
2. Decisions made or needed
3. Deliverables (files created/updated)
4. Next actions
5. Open questions

## Agent catalog

| Agent | Scope | Primary folder |
| --- | --- | --- |
| Strategy & Planning | vision, goals, OKRs, policies | `01-foundation/` |
| Operations | processes, SOPs, internal ops | `02-operations/` |
| Product | discovery, roadmap, PRDs | `03-product/` |
| Engineering | architecture, ADRs, tech notes | `04-engineering/` |
| Sales | pipeline, playbooks, pricing | `05-sales/` |
| Marketing | campaigns, positioning, content | `06-marketing/` |
| Customer Success | onboarding, support playbooks | `07-customer-success/` |
| Finance | budgets, forecasts, reporting | `08-finance/` |
| Legal | contracts, compliance | `09-legal/` |
| People | hiring, performance, culture | `10-people/` |
| Data & Analytics | metrics, dashboards, analysis | `11-data-analytics/` |
| Partnerships | partner strategy and deals | `12-partners/` |
| Program Management | cross-functional delivery | `20-projects/` |

## Agent rules

- Use templates from `_templates/` for new docs.
- Keep one source of truth and link to related files.
- Update or create an index file when a domain grows.
