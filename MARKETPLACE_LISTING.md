# System Design Compass: Marketplace Listing Guide

This document provides verified, field-by-field copy for publishing System Design Compass to the Agent Skills marketplace. Every field matches the submission dashboard across all five steps and adheres to strict antislop technical writing standards.

---

## Overview and Field Summary

| Step | Form Section | Recommended Action or Value |
|---|---|---|
| **Step 1** | Skill ZIP Upload | Upload `system-design-compass.zip` (contains `SKILL.md`, `agents/`, `references/`, `scripts/`). |
| **Step 2** | Skill Details | Set Name, Summary (181 chars), Full Description, and upload `assets/system-design-compass-logo.png`. |
| **Step 3** | See it in action (demo) | High-stakes Payment Wallet Settlement scenario with realistic prompt and complete oracle output. |
| **Step 4** | Compatibility & Pricing | Set Compatibility Note (`skills` standard, zero external dependencies) and select `Free (No charge)`. |
| **Step 5** | Permissions & Setup | **CRITICAL FIX:** Clear auto-filled `apple-music-mcp/macOS/uv`. Check `Read Files` only (optional `Terminal / Shell` only for bundled stdlib verification scripts); uncheck `Network Access`. |
| **Extra** | Tags, FAQ & Media | Fill 7 tags, 4 FAQs, and upload `assets/system-design-compass-hero.png` as screenshot. |

---

## Step 1: Skill Package Upload

- **Field:** `Upload your skill ZIP *`
- **File to Upload:** `system-design-compass.zip`
- **Contents:** The distributable skill package located at `skills/system-design-compass/` containing:
  - `SKILL.md` (481-word entrypoint)
  - `agents/openai.yaml` (UI metadata)
  - `references/*.md` (17 on-demand Markdown guides)
  - `scripts/*.py` (2 optional stdlib-only Python 3 verification scripts: `capacity_check.py`, `check_deliverable.py`)
- **Notice:** Excludes repository development tools, tests, and historical evaluation runs.

---

## Step 2: Skill Details and Identity

### Skill Logo Asset
- **Field:** `Skill logo (square, recommended 512×512)`
- **File to Upload:** `assets/system-design-compass-logo.png`
- **Asset Specifications:** 512x512 squircle icon (1024x1024 Retina 2x PNG, 594 KB).
- **Visual Description:** Midnight navy drafting dial with 72 calibrated tick marks, system boundary nodes, and a faceted warm copper compass needle pointing to an authoritative ivory porcelain hub.

### Skill Name Field
- **Field:** `Skill Name *` (Max 60 characters)
- **Input Value:**
```text
System Design Compass
```
*(Length: 21 / 60 characters)*

### Summary Field
- **Field:** `Summary *` (Up to 300 characters, single line)
- **Input Value:**
```text
A disciplined AI agent skill for production architecture reviews, narrow ADRs, and safe migrations. Identifies critical invariants and stress-tests designs against failure paths.
```
*(Length: 181 / 300 characters)*

### Full Description Field
- **Field:** `Full Description *` (Supports Markdown)
- **Input Value:**

```markdown
Architecture decisions often stall on superficial trade-offs or unverified assumptions. Generic advice tells teams to "use a queue" or "add idempotency", but skips the operational failure modes that break production systems.

System Design Compass gives your coding agent a structured framework to audit architectures, write defensible Architectural Decision Records (ADRs), and evaluate complex migrations. Instead of generic summaries, it forces your agent to identify authoritative state owners, construct concrete violating failure sequences, and specify testable validation oracles.

### What the skill does

- **Direct ADR Decisions:** Produces concise, scoped decisions covering latency, isolation boundaries, retry safety, cost drivers, and measurable reconsideration triggers.
- **Deep Architecture Reviews:** Audits proposed or existing systems against repository facts. Cites exact code evidence, measures blast radius, and recommends the smallest viable correction.
- **Zero-Downtime Migration Planning:** Plans safe database and service migrations. Defines per-phase sources of truth, dual-write convergence gates, cutover barriers, and rollback contracts.
- **Production Readiness Audits:** Evaluates queue backlog recovery capacity, lease fencing mechanisms, replication lag, and disaster recovery boundaries.
- **System Design Practice:** Facilitates structured mock architecture interviews with time-boxed scoping, capacity estimation, and rubric-driven feedback.

### How it works

The skill uses selective on-demand routing. Instead of loading thousands of tokens on every conversation turn, a compact 481-word entrypoint (`SKILL.md`) routes requests by the unresolved decision:
- **Narrow decisions:** Resolved directly within the entrypoint.
- **Complex workflows:** Selectively loads only the relevant boundary or domain reference among 17 focused guides or 28 production workload archetypes.
- **Zero external dependencies:** Requires no external MCP servers, third-party packages, network calls, or API keys; includes 2 optional stdlib-only Python 3 verification scripts (`capacity_check.py`, `check_deliverable.py`). Follows the open Agent Skills specification.

### Three engineering reminders built into every review

1. **A timeout is an unknown outcome:** Never treat an ambiguous remote call as a clean failure before resolving external state.
2. **Queue storage is not recovery capacity:** Backlog clearance requires net positive completion headroom above normal arrivals plus retries.
3. **Restoring old binaries does not undo incompatible writes:** Rollback safety depends on mixed-version read and write compatibility.
```

---

## Step 3: See It in Action Demo

### Demo Request Prompt
- **Field:** `The request (what the buyer types)`
- **Input Value:**

```text
$system-design-compass Review our payment wallet settlement flow. We have an API gateway calling a third-party payment processor, then writing balance updates to Postgres. We are seeing duplicate charge risks during gateway timeouts. Focus on retry identity, atomic ledger updates, and external provider ambiguity.
```

### Demo Result Output
- **Field:** `The result (what your agent delivers)`
- **Input Value:**

```markdown
I reviewed the payment wallet settlement flow. The primary risk is duplicate debits caused by ambiguous remote timeouts: when the third-party processor succeeds but the network times out before returning a response, naive retries re-execute the charge under a new request context.

### Architectural Assessment: Payment Wallet Settlement

| Boundary | Invariant | Failure Mode | Enforcement Mechanism |
|---|---|---|---|
| **Retry Identity** | Exactly-once financial effect per client operation | Client retries after network drop; generates fresh request | Scope idempotency key by `tenant_id:account_id:idempotency_key` at the API boundary before calling external services. |
| **Provider Ambiguity** | No local ledger commit without verified external state | 30s timeout on payment capture; outcome unknown | Store payment intent as `PENDING` with deterministic key; query provider reconciliation API before retry or refund. |
| **Ledger Atomicity** | Balance debit and transaction record commit together | DB connection drops after balance deduction | Wrap balance decrement and audit ledger entry in a single serializable database transaction. |
| **Rollback Safety** | Irreversible external charges cannot be rolled back locally | Failed ledger write leaves external capture orphan | Background reconciliation worker polls pending intents, resolves final status, and issues refunds if unlinked. |

### Concrete Violating Failure Sequence
1. Client submits $50 wallet transfer with `idempotency_key: tx_981`.
2. Gateway stores intent `tx_981` as `PENDING` and calls Payment Processor.
3. Payment Processor captures $50 successfully, but response drops due to a transit timeout.
4. Client SDK times out after 10s and retries the request with a newly generated UUID `tx_982`.
5. Gateway treats `tx_982` as a new transaction and captures another $50, causing a double debit.

### Smallest Defensible Correction
1. **Contract-Scoped Idempotency:** Require the client to retain the original business transaction identity across retries. Reject attempts to reuse keys across different payloads.
2. **Intent Reservation:** Commit an `INTENT` record with status `PROCESSING` in Postgres prior to dispatching external network calls.
3. **Reconciliation Gate:** When a remote call times out, do not fail or retry immediately. Transition intent to `IN_DOUBT` and invoke the provider's `GET /v1/charges/{idempotency_key}` status endpoint before deciding whether to retry or reverse.

### Validation Test and Observable Oracle
- **Fault Schedule:** Inject a 15-second dropped connection on the processor HTTP response socket during test runs.
- **Pass/Fail Oracle:** After 5 retry attempts by the client, total external settled volume must equal exactly $50 (1 charge), local ledger must reflect exactly one debit, and zero orphan pending intents remain after the reconciliation worker executes.
```

---

## Step 4: Compatibility and Pricing

### Compatibility Note Field
- **Field:** `Compatibility Note`
- **Input Value:**
```text
Compatible with any AI agent supporting the open Agent Skills specification (SKILL.md), including Claude Code, Cursor, Codex CLI, Gemini CLI, VS Code Copilot, and OpenCode. Requires zero external dependencies, no API keys, no network calls, and no MCP servers; includes 2 optional Python 3 stdlib-only verification scripts. (Optional verification scripts and repository development tools require Python 3.10+).
```

### Pricing Model Field
- **Field:** `Pricing Model *`
- **Selection:** `Free (No charge)`
- **Rationale:** System Design Compass is open-source software licensed under MIT. Listing as free maximizes developer adoption across the agent ecosystem.

---

## Step 5: Permissions and Tooling

### Required Tools and Software Field
- **Field:** `Required tools & software`
- **Action:** **Delete all auto-filled items** (`apple-music-mcp`, `macOS`, `uv` are invalid hallucinations).
- **Input Value:**
```text
None
```
*(Leave completely blank or type `None`)*

### Tools Used Checkboxes
- **Field:** `Tools Used`
- **Check:**
  - `[x] Read Files` (Needed so the agent can inspect repository code, schemas, and ADRs when requested).
- **Optional:**
  - `[ ] Terminal / Shell` (Optional: only needed if you want the agent to run the 2 bundled stdlib-only Python 3 verification scripts locally; skill guidance works without shell execution).
- **Uncheck:**
  - `[ ] Write Files`
  - `[ ] Browser`
  - `[ ] Network Access` (**CRITICAL:** Uncheck network access; the skill and its optional local scripts make zero network calls).
  - `[ ] Environment Variables`

### Needs Access To and Other Tool Fields
- **Field:** `Needs access to` -> Select nothing / Leave empty.
- **Field:** `Other tool` -> Leave blank.

### File Scopes Field
- **Field:** `File Scopes`
- **Input Value:**
```text
src/**, docs/**, *.md, *.json, *.yaml
```
*(Or leave empty for project-wide inspection)*

### Permission Notes Field
- **Field:** `Notes (optional)`
- **Input Value:**
```text
System Design Compass follows the open Agent Skills specification with 17 on-demand Markdown guides and 2 optional stdlib-only Python 3 verification scripts. It requires zero external packages, zero API keys, no network access, and no background runtime services. The Read Files permission is used solely to inspect repository code, schemas, and configuration when the user requests an architecture review or design recommendation.
```

---

## Step 6: Tags, Categories, and Usecases

### Recommended Tags
Add the following 7 tags:
- `system-design`
- `software-architecture`
- `distributed-systems`
- `adr`
- `reliability`
- `backend`
- `sre`

### Recommended Categories
- Primary Category: `Software Architecture`
- Secondary Category: `Engineering Tools` / `Code Review`

### Core Usecases
- Production architecture reviews and fault analysis
- Architectural Decision Record (ADR) drafting
- Zero-downtime database and schema migrations
- Queue backlog capacity and recovery audits
- System design mock interview preparation

---

## Step 7: Extra Details and FAQ

### Metadata Properties
- **Version:** `1.2.0`
- **Author:** `Woffluon`
- **License:** `MIT`
- **Repository URL:** `https://github.com/Woffluon/system-design-compass`

### Frequently Asked Questions

**Q1: Does this skill require any external API keys or MCP servers?**
> A: No. System Design Compass ships 17 Markdown guides and 2 optional Python 3 stdlib-only verification scripts. It has zero external dependencies, makes no external network calls, and requires no third-party API credentials.

**Q2: How does the skill prevent bloating the model context?**
> A: The skill uses a compact 481-word entrypoint (`SKILL.md`) that selectively routes requests. Narrow decisions are answered within the entrypoint. The agent loads deeper reference files only when specific boundary guarantees or workload archetypes are unresolved.

**Q3: Which coding agents are supported?**
> A: The skill follows the open Agent Skills specification (`agentskills.io`). It works across Claude Code, Cursor, Codex CLI, Gemini CLI, VS Code Copilot, and any environment that discovers `SKILL.md`.

**Q4: How were the architectural recommendations verified?**
> A: The repository includes a blind comparative evaluation suite (`evals/`). On the frozen 1.1.0 candidate entrypoint, all 8/8 core benchmark cases passed under tool-free blind grading on Gemini 3.8 Flash Medium with zero critical violations.

---

## Step 8: Visual Media and Documentation Links

### Recommended Screenshots
1. **Primary Cover / Banner:** `assets/system-design-compass-hero.png` (Wide 16:9 editorial architectural maquette).
2. **Square Brand Icon:** `assets/system-design-compass-logo.png` (512x512 squircle logo).

### Documentation Link Target
- **Field:** `Documentation Link (Optional)`
- **Input Value:**
```text
https://github.com/Woffluon/system-design-compass#readme
```
