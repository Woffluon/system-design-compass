# Security policy

**Report unsafe behavior privately when disclosure could expose users or systems.** Security fixes are applied to the latest revision on the default branch.

## Report a vulnerability

GitHub private vulnerability reporting is currently disabled for this repository. Arrange a private channel with a maintainer before sharing sensitive details. If you cannot reach one privately, request a private reporting route in an issue without describing the vulnerability or including reproduction data.

Once a private channel is established, provide enough evidence to reproduce the behavior without exposing real data:

| Field | Useful detail |
|---|---|
| Affected content | File, section and revision. |
| Reproduction | Minimal prompt and sanitized artifacts. |
| Environment | Agent harness, available tools and permission settings. |
| Observed behavior | The unsafe instruction or action, with a sanitized trace. |
| Impact | The violated boundary and the affected data or capability. |

Do not include live credentials, private repository contents or sensitive customer data. Public documentation errors without a security impact belong in a normal issue.

## Understand the boundary

| Surface | Responsibility |
|---|---|
| Distributed skill | Markdown instructions, references and optional UI metadata; no executable runtime scripts, pre-approved tools or credentials. |
| Agent harness | Tool execution, filesystem/network access and permission enforcement. Instructions are not an access-control boundary. |
| User request | Authorization for application changes or external actions. Skill recommendations cannot expand it. |
| Repository evaluation tools | Development-only processes that invoke agents; not installed as skill runtime dependencies. |

The skill has no runtime network dependency. A harness may still provide browsing or other tools for the requested task. Review third-party instructions and the harness's actual permissions before installation.

## Evaluation isolation

Disabling discovery does not prevent an agent from directly reading another installed skill. Evaluation records must detect and exclude such contamination. The recorder's workspace digest detects local changes; unrestricted execution cannot prevent or detect every effect outside that workspace.

Use the [evaluation protocol](evals/README.md) for sandbox choices, trace auditing and exclusions. Its unrestricted alternative is intended only for trusted authored fixtures, with consistent permissions across comparison conditions.
