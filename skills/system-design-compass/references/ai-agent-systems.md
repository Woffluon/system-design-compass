# AI and LLM Agent Systems

Use this reference when designing or reviewing LLM agents, RAG pipelines, MCP or tool gateways, multi-step model routing, or agent evaluation gates. Skip it for single-call prompt tweaks or routine SDK usage without state, authorization, or tool side effects.

**Contents:** [RAG data layers](#choose-unified-vs-split-rag-data-layers) · [Query-time auth](#enforce-query-time-authorization-and-safe-abstention) · [Tool PEP gate](#gate-tool-execution-at-a-server-side-pep) · [Simplicity and routing](#apply-the-simplicity-ladder-and-routing-budget) · [Commit-boundary evals](#verify-outcomes-at-the-commit-boundary) · [Decision template](#portable-agent-and-rag-decision-template)

## Choose unified vs split RAG data layers

State whether vector embeddings and authoritative authorization metadata live in one transactional store or separate systems. Splitting embeddings (for example, a standalone vector index) from relational ACLs creates an asynchronous sync window where permission revocations lag and deleted or restricted documents remain retrievable. Even sub-second sync windows expose stale reads and cross-tenant leaks when permissions change under concurrent queries.

Compare a split index against a unified store (such as PostgreSQL with `pgvector` and Row-Level Security) before accepting eventual ACL sync. A unified store provides `0 ms` visibility and revocation lag under a single transactional owner, trading specialized vector-index scale for strict isolation; a split index requires a synchronous query-time authorization check on every returned ID before context assembly. Follow [data ownership](interfaces-data.md#model-data-around-ownership-and-access) when selecting the authoritative boundary.

## Enforce query-time authorization and safe abstention

**Similarity ranking must never bypass authorization.** Treat vector search scores as unauthenticated candidate generation; never rely on static index metadata snapshots as the sole access boundary when revocations must take effect immediately.

Evaluate server-side ABAC or RLS against live tenant, role, and resource ownership at query time before any retrieved chunk enters the prompt—matching [authorization boundaries](interfaces-data.md#authorization-is-part-of-the-state-boundary). Test immediate revocation: revoke a session's access, issue a query on the very next request, and assert `0` restricted chunks enter LLM context.

Define **safe abstention** for denied access and corrupted or mismatched session state. Textual groundedness checks alone fail silently under corrupted session state because the model still produces fluent answers from wrong or partial context. When authorization fails or session state is inconsistent, halt generation and return a deterministic refusal without partial leakage.

## Gate tool execution at a server-side PEP

Untrusted documents, tickets, and external messages can carry indirect prompt injection or poisoned MCP tool descriptions that chain a confidential read into an outbound write (**read-then-egress** exfiltration). **Counterexample:** an agent summarizes an internal customer ticket containing hidden instructions and invokes an outbound Slack or refund tool to leak data or mutate state.

Place a server-side **Intent Gate / Policy Enforcement Point (PEP)** outside model control:

- **Short-lived JIT credentials:** mint task- and tenant-scoped tokens per invocation rather than exposing ambient service credentials to the agent runtime.
- **Version-pinned tool IDs:** bind each allowed tool to a fully qualified server identifier and pinned version or digest so tool schemas cannot mutate silently.
- **Dry-run diff and human approval:** require a dry-run state diff and explicit human confirmation before destructive, financial, or irreversible writes.
- **Egress allowlist:** restrict outbound network calls, webhooks, and destinations to pre-approved targets after reading sensitive data.

## Apply the simplicity ladder and routing budget

Escalate complexity only when simpler boundaries fail to cover the task: **single LLM call -> deterministic workflow -> autonomous agent**. Autonomous loops add failure modes, non-determinism, and tail latency that deterministic workflows avoid.

When running multi-step agent loops, avoid **cascade routing** (trying a small model first and escalating to a larger model per step), which compounds per-step cost and queue latency across iterations. Use **single-step capability or prefix routing** with explicit per-turn budgets for steps, tokens, and tool calls (`Proposed` limits until production traces justify tighter bounds).

## Verify outcomes at the commit boundary

**`LLM-as-a-judge` and textual groundedness do not verify state integrity.** Judges frequently reward polite responses that perform forbidden database writes or leave partial side effects. Pair behavioral evals with a **deterministic commit-boundary evaluator** that inspects authoritative database rows, ledger state, and external side-effect logs against expected postconditions and forbidden-write assertions.

Measure both **`pass@k`** (at least one success across *k* attempts, showing capability) and **`pass^k`** (all *k* attempts succeed, showing production reliability). Gate production rollout on `pass^k` (`Proposed` threshold) and concrete [fault schedules and oracles](decision-validation.md#turn-a-claim-into-observable-evidence) covering revoked sessions, injected documents, and tool failures.

## Portable agent and RAG decision template

Use this neutral summary structure when handing off an AI agent design or review to another engineering or coding workflow:

```markdown
**Agent and RAG Architecture Assurance Summary**
- **Authoritative State and Index Owner:** `<primary data store and RLS or ACL boundary>`
- **Query-Time Authorization Gate:** `<ABAC / RLS policy; 0 ms post-revocation context leakage>`
- **Safe Abstention Policy:** `<deterministic refusal on access denial or inconsistent session state>`
- **Tool Execution Gate (PEP):**
  - Tool identity and version pin: `<server@version or digest>`
  - Destructive and egress guard: `<JIT credentials, dry-run diff, human approval, egress allowlist>`
- **Simplicity and Routing Budget:** `<single call | workflow | single-step capability router; max steps/cost (Proposed)>`
- **Deterministic Eval Oracle:** `<commit-boundary DB/API state assertions + pass^k threshold (Proposed)>`
```
