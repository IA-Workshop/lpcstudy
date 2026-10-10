---
name: verify-citation
description: "Confirms that a cited source supports a specific claim, or finds a published reference value, using the researcher agent, the only agent with web access (VV.2, LPC.AUTH.2)."
argument-hint: "[claim] -- [source or what to find]"
context: fork
agent: researcher
background: false
---

Request: $ARGUMENTS

1. Retrieve the source: one item per request, no crawling.
2. Decide whether it supports the exact claim: `confirmed`, `partially supported`, `not supported` or `could not retrieve`.
3. Quote the supporting passage, with page or section, and record the conditions (parameters, method, step size) for any numerical value.
4. Append a row to `docs/agent/notes/<today>-research-citations.md`.
5. Return the status and the quote.

Never fill a citation from memory.
