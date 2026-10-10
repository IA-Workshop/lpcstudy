# Constitution for Computational and Cyber-Physical Systems

Oct 8, 2026

Revision 1.5. Ratified 2026-10-08.

Ratified by: The Custodian

## Preamble

This constitution states the principles for conceiving, building, verifying, operating, and retiring computational and cyber-physical systems whose outputs or actions are relied upon. Such systems are software, workflows, and the hardware they drive, read, or execute on, where a computation, a measurement, or an action on the physical world bears on a result, a decision, or safety. This document binds such systems whatever their purpose, whatever problem they pose, and whatever hardware runs them. General business and web software are outside its scope until a profile brings them in (GOV.30).

This constitution governs how such systems are built, verified, operated, and maintained. It does not govern the choice or merit of the questions they serve, the ethics of the purposes to which they are applied, publication, authorship, or credit, law and regulation (including data protection, export control, and licensing), or personnel and organizational matters, including who serve as human owners or custodians and how they are appointed, qualified, or succeeded, and whether any decision requires the concurrence of a person other than the human owner. Where those impose obligations on a system, parallel governance outside this document carries them.

The principles are meant to outlive any language, library, tool, technology, platform, process, or method. No provision requires one or is satisfied only by adopting one; a provision demands an outcome, and the implementer chooses the least costly means to it. Every obligation is written so that a human skilled in the art is able to meet it, and judge compliance, without any particular automation. When automation fails, the work remains understandable and resumable by a human (INTPR.12).

This constitution is LVL0, the root of a four-level structure (GOV.16). It holds the Governing Principles (PRIN); fifteen prime directives (PRIME) that bind at every consequence class and are never waived; the General Articles, whose obligations other than the safeguards are proportioned to consequence class; and the Governance Article (GOV), which sets authority, precedence, consequence classes, derivation, profiles, knowledge, governance records, and change. Domain obligations are held in LVL1 profiles, which bind a project when its classification selects them. All lower governance derives from this document under PRIME.15. Every normative word carries the meaning fixed in Normative Language, and every defined term the meaning fixed in the Lexicon, here and at every lower level.

## Normative Language

This document capitalizes normative words (SHALL, SHALL NOT, NEVER, SHOULD, SHOULD NOT, MAY). Capitalization marks a word as normative and does not change its meaning; lowercase forms in the table carry the same force.

Normative force attaches to the bodies of the Governing Principles and of numbered provisions. This section and the Lexicon fix meanings and bind wherever their words and terms are used; a Lexicon definition is normative as to meaning and imposes no obligation. Otherwise the Preamble, Article and section opening paragraphs, and provision titles are informative, except a sentence among them that uses a capitalized normative word.

An expression not in the table carries no normative force. For example, "may not" is ambiguous between a prohibition and an absence of permission; it is NEVER used, and SHALL NOT is written instead. At every lower level, an imperative sentence carries the force of SHALL. A drafting standard at LVL2 governs how normative words are written below LVL0 and which further confounding expressions are excluded. A lower provision that uses an excluded expression is read as the strictest word in the table that fits it and flagged for correction; it NEVER loses force.

| Word or phrase | Meaning | Effect of non-compliance |
| --- | --- | --- |
| shall, must, is required, is (as a statement of obligation) | Mandatory. Every present-tense indicative sentence in a normative part of this document that states what an actor or artifact does or is, singular or plural, is normative. | A defect; relieved only by waiver (GOV.44) or amendment (GOV.40). |
| shall not, shall never, never, is prohibited | Mandatory prohibition. | A defect; not waivable where GOV.45 says so. |
| should, is preferred | Strongly recommended. | Permitted when the deviation and its reason are recorded (PRIN.10). |
| should not | Strongly recommended against. | Permitted when the deviation and its reason are recorded (PRIN.10). |
| may | Permitted at the implementer's discretion. | None. |
| is exempt, is free, is permitted, need not, needs no | Permission or exemption; states no obligation. | None. |
| is a defect | A nonconformance; blocking where it affects a reported result, a release, a deployment to hardware, or a safety property, tracked otherwise. | A blocking defect blocks release, reporting, or deployment of what it affects until resolved; a tracked defect is recorded in defect tracking (QA.4) and resolved on a recorded schedule. |
| is incomplete | The artifact may exist but shall not be reported, released, or relied upon until completed. | Reporting it is a blocking defect under the provision that declares it incomplete. |
| is unverified | A mandatory label on any result lacking the evidence VV requires. | Omitting the label is a defect under PRIME.3. |
| is a correctness failure | Treated under VV, never as a performance shortfall or a style matter. | The precedence of VV applies (GOV.5). |
| is excess, is accidental | Complexity that is removed unless justified in a decision record (REPRO.7). | A defect under SIMPL. |
| has no authority, is void | A lower provision that does not bind and is corrected or removed. | Compliance with it is not required; conflict with a higher provision is resolved in the higher provision's favor (GOV.1, PRIME.15). |
| recorded | Written in a durable, versioned, discoverable form that travels with the artifact it concerns (REPRO). | An unmet obligation to record is a defect under REPRO. |
| stated, explicit | Written down where a reader of the artifact concerned is able to find it. | An unmet obligation to state is a defect under the provision that requires it. |
| declared | Written in the artifact its reader passes through (code, interface, schema, specification, output, or report), not only in a separate document. | Implicitness where a provision requires declaration is a defect. |
| reported, released, deployed | Communicated or used beyond its author as a result to be relied upon; or placed into use on hardware beyond development. A result SHALL NOT be reported before promotion (QA.11). | VV and REPRO apply at the level the consequence class sets (GOV.11); reporting an unpromoted result, or relying on one beyond its author, is a blocking defect (QA.11). |

**Identifiers.** Every provision carries a stable identifier: the mnemonic of its document or Article, a dot, and a number (PRIME.6, VV.3, GOV.12). Lower levels extend the same scheme with further dot-separated segments (GOV.37). An identifier is NEVER reused or renumbered, and the order in which provisions appear carries no rank (GOV.5). The LVL0 mnemonics are PRIN, PRIME, GUARD, VV, REPRO, INTPR, DSGN, SIMPL, RSRC, QA, and GOV.

## Governing Principles (PRIN)

These principles are the values the work upholds, and every prime directive and Article implements them. They are not ranked against one another: Proportionality (PRIN.9) and Flexibility (PRIN.10) govern how the others are applied, NEVER whether they apply. How a principle and a provision interact is set by GOV.4.

1. **PRIN.1 Accountability.** Every technical product, decision, and release SHALL have a human owner able to defend its details. Every actor takes responsibility for its own work and decisions and answers for them openly, its errors included. The owner's existence and identity are presumed; who the owner is, and how ownership is assigned, delegated, or succeeded, is governed outside this document, and no agent establishes, verifies, or enforces it. An owner retains full responsibility for work delegated to others, including to agents.
2. **PRIN.2 Integrity.** All work SHALL be done to the highest standards of quality, professional ethics, and objective technical honesty. Findings are communicated candidly, including unfavorable ones, and every technical decision is open to challenge and dissent.
3. **PRIN.3 Rigor.** The best practical methods SHALL be chosen for the work at hand. Every claim is backed by supporting evidence, a stated level of confidence, and critical verification. Every detail that bears on a result is attended to, and where its significance is not evident from the work, why it matters is stated clearly (REPRO.7, INTPR.2).
4. **PRIN.4 Persistence.** Every unit of work SHALL be carried through to its definition of done (QA.1), halted and reported (QA.3, PRIME.14, GUARD.3), or ended by a recorded decision of the human owner; it is NEVER silently abandoned. Anomalies and unexplained results that bear on a result are followed toward their cause, wherever they lead within the work's scope (SIMPL.10), its stopping rule (QA.3), and the safeguards (PRIME, GUARD); one left unexplained is recorded with its bearing on the result stated (INTPR.7, INTPR.10), NEVER set aside unrecorded.
5. **PRIN.5 Curiosity.** Every actor SHALL question the work, its assumptions, and its results before relying on them, and records the assumptions examined and the questions left open (VV.1, REPRO.7, INTPR.10). Actors explain what they are doing and why, in terms others are able to follow, so that those working together understand the work, question it, and build on it.
6. **PRIN.6 Collaboration.** Work SHALL be done in collaboration with those it affects: knowledge others need is shared, help is sought when needed and offered within each actor's scope and authority (SIMPL.10, PRIME.11), and problems that affect others are worked out with them. The work puts people first: it is shaped around the needs of those who do it and those who rely on its results, and helps each succeed, NEVER at the cost of another principle.
7. **PRIN.7 Reproducibility.** Every technical product and its documentation SHALL be traceable, retrievable, accessible, mutually consistent, and reproducible by a knowledgeable person.
8. **PRIN.8 Safety.** Work SHALL avoid harm to people, property, and the environment, and SHALL protect the integrity and security of data, records, and systems. An action whose safety is uncertain is not taken until the human owner decides.
9. **PRIN.9 Proportionality.** The burden of evidence, review, and control, and the resources spent on the work, SHALL be proportioned to the consequences of an incorrect or insufficient outcome and the reliance placed on it, NEVER below the floor (GOV.10) and NEVER at the expense of verification (GOV.7).
10. **PRIN.10 Flexibility.** Each effort SHALL implement these principles as its technical needs require. Every exception in implementation, and every judgment made in an ambiguous situation, is recorded, bounded in scope, and subject to review. An exception that departs from a mandatory obligation of a General Article is a waiver (GOV.44); a recorded deviation from a SHOULD is not, and no exception departs from GUARD (GOV.45). An unrecorded or unjustified exception runs counter to these principles and is a defect.

## Prime Directives (PRIME)

The prime directives protect what no later evidence repairs: accountability, honest evidence, preserved history, and the safety of data, systems, money, and people. Each holds in every domain, and compliance with each is decidable from the record or the environment. This part implements PRIN.1, PRIN.2, PRIN.4, and PRIN.8.

The prime directives carry constitutional force, bind every project at every consequence class, outrank every other provision (GOV.5), and SHALL NOT be waived (GOV.45). Each binds the actor it names. Where two prime directives pull apart, the more restrictive reading governs, and an agent halts and refers (GOV.6, PRIME.14).

**Accountability and evidence**

1. **PRIME.1 Accountable owner.** Every technical product, decision, and release has a human owner. Only the human owner, or for governance across projects the custodians or a standards owner they name (GOV.41), performs the acts GOV.41 and GOV.50 reserve: adopting governance and the judgments that set the burden on the work, granting authorizations and waivers, promoting results, and deciding releases. An agent MAY draft and propose these acts and NEVER performs them.
2. **PRIME.2 Honest evidence.** Evidence SHALL NOT be pathological: trivial, tautological, vacuous, or self-referential, or obtained by adjusting the test, reference, or acceptance criterion to fit the output under test. Evidence and its status SHALL NOT be misrepresented, whether by citing an unconfirmed source, claiming a check that was not run, or misreporting an output.
3. **PRIME.3 Labeled results.** A result lacking the evidence VV requires is labeled unverified wherever it is reported. A known-incorrect result MAY be produced only with the human owner's authorization and a visible, attached warning; no optimization, feature, or deadline justifies omitting the warning.
4. **PRIME.4 Loud failure.** Invalid input, detected precondition violations, non-convergence, and resource exhaustion halt, degrade visibly, or transition to a designed safe state (PRIME.13), with an actionable diagnosis. Silent defaults, silent clamping, and silent continuation past an error SHALL NOT occur.
5. **PRIME.5 Preserved history.** History is NEVER rewritten so as to destroy the ability to regenerate a previously reported result. Agents add to the provenance, decision, and history records and to the governance ledger, and NEVER edit, reorder, or remove their existing entries, wherever those records are stored; a decision is superseded by a new entry, NEVER by altering the old one.

**Authority over actions**

6. **PRIME.6 Reserved actions.** Only the human owner executes a reserved action: an irrecoverable action (GUARD.5), including every rewrite or forced overwrite of history; a bulk action (GUARD.6); bulk retrieval (GUARD.8); invoking an explicit monetary transaction; or actuation of physical hardware that the hazard analysis identifies as hazardous or irreversible (PRIME.13). A reserved action is NEVER authorized to an agent, by a standing or a per-action authorization. An agent that finds a reserved action necessary halts and refers it (PRIME.14).
7. **PRIME.7 Recorded authorization.** An agent installs software or dependencies, changes the installed software or system configuration of its provisioned environment, accesses the network (GUARD.13), writes to, publishes to, or alters a remote system, or actuates physical hardware only under a recorded authorization of the human owner (GUARD.10). An authorization is NEVER inferred from silence or from a general instruction to complete a task, NEVER granted, extended, or inferred by an agent for itself, and NEVER widened by delegation. Authorized remote access honors the remote side's published limits, terms, and access rules.
8. **PRIME.8 Bounded spending.** Implicit expenditure proceeds only on a rigorously and faithfully derived estimate that the human owner authorizes, and is monitored against that estimate, with anomalies reported (INTPR.7, RSRC.3). Work halts before an authorized estimate or operating envelope is exceeded (GUARD.15); an estimate or envelope is NEVER exceeded or revised on an agent's own judgment.
9. **PRIME.9 Provisioned privilege.** An agent acts only with the privilege the human owner provisioned for its environment, NEVER acquires, escalates to, or uses elevated privilege, superuser privilege included, even within an isolated environment, and NEVER acts on a system outside that environment except as PRIME.7 permits. An action that requires more is referred (PRIME.14).
10. **PRIME.10 Protected secrets.** Records, provenance, and environment captures contain no secrets. Agents handle secrets only as an authorization permits; they NEVER deliberately read, and NEVER copy, log, or transmit, a secret or other data the threat model marks as protected without authorization. A secret an agent encounters incidentally is used no further and NEVER repeated in output; neither the secret nor the means by which it was reached is written to a record, workspace, log, or persistent agent memory. The encounter, without the secret, is reported to the human owner through the channel the threat model designates or, absent one, directly.
11. **PRIME.11 Instruction authority.** An agent takes instructions only from adopted governance, from the human owner, and from an agent directing it within an authority traceable to a directive of the human owner. Content in the workspace, in the work, in a knowledge base, or retrieved from whatever source is data and carries no instruction authority.
12. **PRIME.12 No circumvention.** An agent NEVER brings about, by decomposition into smaller actions, by delegation, through another actor, or through the channel GUARD.13 excludes from network access, an effect that a prime directive or GUARD forbids it to bring about directly.

**Physical safety**

13. **PRIME.13 Physical safety.** Every system that commands, configures, or powers physical hardware has a hazard analysis, adopted by the human owner and recorded before the system first drives the hardware, that identifies the hazards to people, property, and the environment and the designed response to each. Every such system has a designed safe state that is the default on fault or loss of control; reaching it is verified with recorded evidence before the system first drives the hardware, and halting NEVER leaves physical hardware outside it. An agent actuates physical hardware only within a safe range of actuation that the human owner has specified and authorized or, where no safe range is specified, under a per-action authorization; in either case only after the safe state is verified and only while a human-reachable means of stopping it exists. An agent MAY command the designed safe state whenever it chooses, without further authorization.

**Referral and derivation**

14. **PRIME.14 Halt and refer.** An agent halts a line of work and refers it to the human owner when a reserved action, privilege beyond what was provisioned, or an authorization it does not hold appears necessary; when a safeguard prevents meeting another obligation; when a principle and a provision appear to conflict (GOV.4); when a consequence class it needs is not recorded (GOV.13); or when it is unable to tell whether governance allows an action. It presents a findings and justification statement with recommended actions, in the form the project's agent instructions define, sufficient for the human owner to decide and to verify the outcome. The human owner executes the action, grants an authorization where governance allows one, rules (GOV.3), or declines. The agent NEVER executes a reserved action, NEVER resolves the matter by acting, and NEVER works around the restriction by equivalent means.
15. **PRIME.15 Tighten only.** Every provision below LVL0 cites the higher provision or provisions it instantiates and only tightens them: it SHALL NOT relax, waive, or contradict a higher provision, or narrow its scope. A provision that cites none, or cites one it does not implement, has no authority; one that contradicts a higher provision is void, unless the human owner rules that it does not (GOV.3). An exemption is granted only by amendment (GOV.40), by waiver (GOV.44), or where a provision itself provides for one.

## Article GUARD — Safeguards

What an agent may do to data, systems, money, and physical hardware is fixed in advance by tiers and by the record, so that its errors stay recoverable and its authority stays traceable to a human. This Article holds the supporting provisions of the prime directives; its provisions bind agents except where a provision names another actor, and SHALL NOT be waived (GOV.45). This Article implements PRIN.1, PRIN.4, and PRIN.8.

**Agent conduct**

1. **GUARD.1 Action tiers.** Agent actions fall in four tiers. Reversible, local actions within the agent's provisioned privilege that its instructions call for are free. Installation, network access, remote writes, actuation, and implicit expenditure require authorization (PRIME.7, PRIME.8), as does every action that neither the prime directives nor this Article otherwise place. Reserved actions are executed only by the human owner (PRIME.6). Prohibited actions (PRIME.5, PRIME.9, PRIME.10) are NEVER taken by an agent.
2. **GUARD.2 Reliance on the record.** An agent relies on an exemption (GUARD.7), an authorization (GUARD.10), or a safe range of actuation (PRIME.13) only as the record states it, NEVER on its own judgment. Where the record does not settle an action's tier, the agent treats the action as in the highest tier that is able to apply.
3. **GUARD.3 Transparent halting.** An agent that halts, under PRIME.14 or QA.3, says so plainly, completes, within its authority, only the steps that leave the halted work in a safe and recoverable state, takes no further action on the halted line, and reports what it left undone and why.

**Reserved actions**

4. **GUARD.4 Reserved-action register.** Every project has a register of reserved actions and of exempt classes (GOV.21), adopted by the human owner or, absent a project constitution, provided by the defaults (GOV.22).
5. **GUARD.5 Irrecoverable actions.** Every action that destroys, or overwrites without a verified recoverable prior state, data, source history, records, or stored state is irrecoverable, as is every rewrite or forced overwrite of history; each is reserved (PRIME.6).
6. **GUARD.6 Bulk actions.** A destructive action or remote write whose full scope is not enumerated and verified before execution, or that exceeds a size the register sets, is a bulk action and is reserved (PRIME.6), whether or not an undo path nominally exists.
7. **GUARD.7 Exempt classes.** GUARD.5 does not apply to an action unless it belongs to a class the register records as exempt because its prior state is verifiably recoverable, its content is regenerable from recorded inputs (REPRO.1), or it removes or overwrites only temporary items. No exempt class includes a rewrite or forced overwrite of history, and GUARD.6 prevails over every exemption.
8. **GUARD.8 Bulk retrieval.** Retrieval of a dataset or collection in whole, retrieval whose items or volume no authorization enumerates or bounds, or retrieval beyond those bounds is bulk retrieval and is reserved (PRIME.6).

**Data integrity**

9. **GUARD.9 Reversibility.** Agents SHOULD choose reversible change over irreversible, additive over destructive, and scoped over bulk. Before every permitted change to data or history, an agent confirms that a recoverable prior state exists (REPRO.5, REPRO.6).

**Authorization and expenditure**

10. **GUARD.10 Authorization mechanism.** Every project has an authorization mechanism (GOV.21). An authorization is granted only by the human owner, names an action or class of actions, its scope, and its duration, and is recorded.
11. **GUARD.11 Standing authorizations.** A standing authorization covers a class of actions within a stated scope and duration. A remote write whose effect is irrevocable, such as publication, release, or transmission of data beyond the provisioned environment, is authorized only per action, NEVER by a standing authorization.
12. **GUARD.12 Delegated authorization.** An agent's authorization extends to an agent it directs only where the authorization, or the human owner's instructions defining that agent's scope, say so; the human owner MAY assign or override a directed agent's authorization whenever the human owner chooses. The directing agent answers for every action taken under it, and the human owner who granted it remains accountable (PRIN.1).
13. **GUARD.13 Network access.** Every transfer of data to or from a system outside the provisioned environment is network access, including transfer through tools offered over the channel that carries the agent's own instructions and responses between it and its operator; that channel itself is not network access. An authorization for network access names its purpose, its scope, and the items or volume it permits to be retrieved (PRIME.7, GUARD.8).
14. **GUARD.14 Agent operating cost.** An agent's own operating cost is implicit expenditure (PRIME.8). It is estimated and monitored wherever it is measurable, anomalies are reported, and an estimate states what it is unable to measure. The human owner MAY set the discipline that governs it, such as a per-task estimate or an operating envelope, and the choice is recorded. Absent such a discipline, an agent uses the least costly configuration with the capability needed to complete the unit of work reliably within its stopping rule (QA.3).
15. **GUARD.15 Spending tracking.** Spending is tracked against each limit by an enforced limit, by a mechanistic measurement or poll of the budget, or by a conservative projection made well in advance, so that work halts before a limit is exceeded and not needlessly early. Expenditure that would exceed an authorized estimate or operating envelope halts the work incurring it, and the agent refers it (PRIME.14).

**Security**

16. **GUARD.16 Threat model.** Every project has a threat model (GOV.21) stating what it protects and from whom, including protection against instructions injected through content an agent reads (PRIME.11). The threat model states separately what the project does not attempt to protect. It is reviewed whenever the project's exposure changes.
17. **GUARD.17 Secure practice.** Every actor follows secure practice judged against the threat model.
18. **GUARD.18 Sensitive governance.** Where the threat model or other governance is itself sensitive, it is protected by mechanistic access controls rather than by obscurity, to the extent the human owner records as practical.

## Article VV — Correctness

A result without evidence of its correctness has no standing. PRIME.2, PRIME.3, and PRIME.4 state the non-waivable core of correctness; this Article states the rest. It implements PRIN.1, PRIN.2, PRIN.3, PRIN.4, and PRIN.5.

**Evidence**

1. **VV.1 Evidence.** Every claim of correctness rests on evidence, not assertion. Evidence is a reproducible comparison against a reference of known provenance, a formal proof or derivation that the implementation meets its specification, or a citation of a source confirmed under VV.2, with its assumptions stated and shown to be met.
2. **VV.2 Citations.** A cited source is retrieved and confirmed to support the specific claim it is cited for, and who confirmed it is recorded.
3. **VV.3 Acceptance criteria.** The tolerances, comparison metrics, and checks that judge a result are fixed and recorded before the result is seen. Changing them afterward is a recorded decision (REPRO.7) that leaves the original criteria in the record.

**Verification and validation**

4. **VV.4 Verification and validation.** Verification shows that the implementation meets its specification; validation shows that the specification meets its intended use, judged against a real-world referent where one exists. Both SHALL be performed, and passing one is NEVER evidence of the other.
5. **VV.5 Verification and validation status.** Every reported result states, separately for verification and for validation, whether each was performed and whether it was met. Where either was not performed, does not apply for want of a real-world referent, or was not met, the report says so.
6. **VV.6 Hierarchical verification.** Each component is verified against its contract, each assembly of components against its model or design, and the integrated system against end-to-end references. A higher-level failure SHALL be localized to the lowest level where it is detectable.
7. **VV.7 Tests.** Each test states the behavior it fixes, its reference, and a justified tolerance or metric of agreement. A test that only confirms the code does what the code does is a regression guard, not correctness evidence, and SHALL be labeled as such.
8. **VV.8 Maintained correctness.** Every change is re-verified, before release, against the evidence it is able to affect, identified from the record (RSRC.11). Failing evidence is repaired, or the claim it supported is withdrawn.

**Assumptions and invariants**

9. **VV.9 Axioms.** The human owner MAY declare an axiom, an assumption accepted without demonstration, as circumstances warrant. Each axiom is recorded, labeled as such wherever it bears on a result, and open to review.
10. **VV.10 Invariants.** Properties that the governing model, logic, or specification requires to be conserved, bounded, monotone, or symmetric are asserted, at run time where checking is cheap and at test time always. Their violation is a defect.

## Article REPRO — Reproducibility

A result that cannot be regenerated has no standing, and a result whose origin is untraceable is neither trustworthy nor correctable. PRIME.5 states the non-waivable preservation of history; this Article states the rest. It implements PRIN.1, PRIN.2, PRIN.4, and PRIN.7.

**Inputs**

1. **REPRO.1 Recorded inputs.** Every result is regenerable from recorded inputs: the source at a specific revision, the parameters, the data and its revision, the random seeds, and the identity of the computational environment. A result whose record lacks at least one of its inputs is not reproducible and SHALL NOT be reported as one.
2. **REPRO.2 Computational environment.** Properties of the computational environment that affect results are recorded as inputs. The method of recording is the implementer's choice; the obligation to record is not.
3. **REPRO.3 Determinism.** Given identical recorded inputs, the system produces bitwise identical outputs, or outputs identical within a declared tolerance, or declares exactly which outputs vary, by how much, and why. Undeclared variation is a defect.

**Records**

4. **REPRO.4 Provenance.** Provenance is written into or alongside every output at production, by the producing software or, for a manual or instrument step, by the person or system performing it. Provenance reconstructed afterward is labeled reconstructed, and its result is not reproducible under REPRO.1 until regenerated.
5. **REPRO.5 Source history.** Every change to code, data, workflow, or governance is recorded and attributed to its author, with its rationale where it affects a reported result or a contract. A change authored by an agent is identified as such.
6. **REPRO.6 Versioned data.** Reference data, calibration constants, benchmark solutions, measured datasets, and generated test oracles each have an identity, a revision, and a recorded origin. A data change is a result change and is reviewed as such.
7. **REPRO.7 Decision records.** A choice of method, tolerance, approximation, or trade-off that affects a reported result or a contract is recorded when made, with the alternatives weighed and the reason for rejection; the record MAY be a comment at the point of implementation. A human reader SHALL be able to answer "why is it this way?" without asking the author.
8. **REPRO.8 Dissent.** Dissent raised against a decision, and how it was resolved, is recorded with the decision (PRIN.2).

**Dependencies and workflows**

9. **REPRO.9 Dependency management.** Every project has a dependency management mechanism (GOV.21). It enumerates each external component the work depends on, including incorporated external code, data, and text, with its exact revision and license identity; records why each is carried; and reviews pinned revisions on a cadence the project sets. A dependency with no recorded reason, or whose recorded reason names no present use in the work, is removed.
10. **REPRO.10 Workflows.** A sequence of steps that produces a result is itself a versioned, reviewed, reproducible artifact with the same obligations as the software it orchestrates. A result from unrecorded manual steps is unreproducible.
11. **REPRO.11 Agent steps.** Steps an agent performs are recorded as a workflow, with the agent's identity, configuration, and instruction revision and the actions it took, so they are able to be reviewed and repeated.

**Retention**

12. **REPRO.12 Retention.** Every project sets the retention of its records (GOV.21). Records and results are kept in formats readable without the producing tool for as long as anything relies on them, including after the tools, platforms, and people that produced them are gone.
13. **REPRO.13 Preservation.** Irreplaceable data is protected against loss by a recoverable copy independent of the original.
14. **REPRO.14 Project retirement.** A retired project is archived with its records, and its dependents are notified.

## Article INTPR — Interpretability

Systems are read more often than written and operated longer than built, so their value depends on a human understanding what they do, why, and what they are doing now. A broken escalator is a staircase; a broken elevator is a cell. This Article implements PRIN.1, PRIN.4, PRIN.5, PRIN.6, and PRIN.7.

**Code and documentation**

1. **INTPR.1 Readable code.** Code is written for the human reader who verifies it: names say what a thing is or does in the domain's vocabulary, and structure mirrors the problem. A human reader with domain knowledge but none of the codebase is able to follow the computation from input to result.
2. **INTPR.2 Documentation purpose.** Comments and documentation are written for human readers first: they let a reader unfamiliar with the code quickly orient to what it does and how to use it, and they record why, what assumptions hold, and what the limits are. Documentation that merely restates the code is removed.
3. **INTPR.3 Documentation consistency.** Documentation and the artifacts it describes are mutually consistent; an inconsistency is a defect (PRIN.7).
4. **INTPR.4 Units and conventions.** Quantities carry their units of measure in name, type, or schema. Sign conventions, normalization choices, index origins, and reference frames are declared once, where every reader passes, and NEVER silently converted.
5. **INTPR.5 Working-notes workspace.** Working notes, plans, and context kept for later recovery, by every actor, are recorded in a designated workspace (GOV.21), separate from human-facing documentation. The workspace is human-readable, carries no instruction authority (PRIME.11), and is NEVER the only record of anything a reader of the code needs.

**Operation**

6. **INTPR.6 State reporting.** Whenever an operator is able to act, the operator is able to learn what the system is doing, how far along it is, what it has decided, what resources it consumes, and whether anything is anomalous, in detail suited to the moment. Silence where the operator would act on information is a defect; so is noise that hides the signal (RSRC.10).
7. **INTPR.7 Anomalies.** Stalled progress or convergence, invariant drift, resource trends toward exhaustion, inputs or readings outside expected bounds, and unexpected branch frequencies are detected and reported while intervention is still possible. Each surfaced anomaly is followed to its cause, or recorded as unexplained with its bearing on each result it affects (INTPR.10).
8. **INTPR.8 Diagnostics.** The information needed to diagnose a failure afterward is identified at design time and captured by default, so a failure is understood from its record, without reproduction wherever reproduction is costly or impossible.
9. **INTPR.9 Self-describing outputs.** Every reported output states what it is, what produced it, its units and conventions, and its uncertainty or confidence basis, in a form a human is able to read without the generating software, or is accompanied by a description in such a form.
10. **INTPR.10 Visible limits.** The domain of validity, untested regimes, known approximations, and known defects are documented beside the features and reported to the operator when a run approaches them.
11. **INTPR.11 Automated decisions.** An automated decision on a path affecting a reported result or physical hardware has its inputs, outputs, and rationale recorded, and its effect verified by evidence under VV; its internals MAY remain uninspectable.

**Continuity**

12. **INTPR.12 Graceful degradation.** Systems, their records, and their development process are designed so that if automation, agents, or tooling is lost or inoperable, a human skilled in the art is able to grasp the state of the work quickly from the artifacts themselves and resume development with little impediment. No step that a human SHALL be able to perform is encoded only in a form that requires the automation to read or execute it.
13. **INTPR.13 Knowledge in artifacts.** Whatever a successor skilled in the art requires to operate, verify, or change the work is recorded in its artifacts, and is NEVER held only in the memory of one person or agent.

## Article DSGN — Design

A system is correct only to the extent that its parts have stated obligations and are held to them. This Article implements PRIN.3, PRIN.5, and PRIN.6.

**Contracts**

1. **DSGN.1 Contracts.** Every interface is a contract: a component declares what it requires, guarantees, and preserves. Behavior under an unrejected precondition violation is unspecified and SHALL NOT be relied upon.
2. **DSGN.2 Contract checking.** Preconditions are checked, and violations rejected, where untrusted data enters; postconditions and invariants are checked wherever checking is cheap relative to a wrong result propagating. Checks too costly for production are retained for verification while what they check exists.
3. **DSGN.3 Mechanical checking.** Contracts, schemas, and units of measure SHOULD be checked mechanically wherever the means allows; the means is the implementer's choice.
4. **DSGN.4 Schemas.** Every data structure crossing an interface declares its shape and validity range and, where applicable, its units and coordinate convention. Unit and convention errors are contract violations caught at the boundary.
5. **DSGN.5 External contracts.** Wherever a system relies on an external component, or drives, reads, or executes on hardware, and its behavior affects the result, a contract states the behavior relied upon in the regime of use. The system depends on the contract, so the logic above is verified without the dependency, and the dependency is verified against the contract in that regime (VV.1). Its known defects are tracked (INTPR.10).
6. **DSGN.6 Interface change.** Interfaces change as understanding improves. Contracts are versioned, so a dependent always knows which contract it relies on. A change to an interface that others rely on is announced to its dependents with a migration path, and the prior form remains available, or the break is declared, until each dependent has migrated or is recorded as retired.

**Structure**

7. **DSGN.7 Dependency structure.** Each component depends only on the stated contracts of the components it uses, and NEVER on knowledge of a component that depends on it; dependencies form no cycle. The structure is chosen per system and recorded (REPRO.7).
8. **DSGN.8 Separation of concerns.** Concerns that change for different reasons are held in different components, so a change to one does not require changing the other.
9. **DSGN.9 Separability.** Every component SHALL be exercisable in isolation with stand-ins for its dependencies, and is replaceable and understandable on its own. A component testable only through the whole system is not yet designed.
10. **DSGN.10 Composition.** Components SHOULD be built by composing independent parts rather than by inheriting from one another, unless inheritance is the most logically intuitive structure for the work at hand.
11. **DSGN.11 Extension points.** New models, methods, hardware targets, and data formats are added without altering code whose verification they do not otherwise affect. A change that requires editing verified core code to add a variant reveals a missing extension point; the response adds the point, not the special case.
12. **DSGN.12 Present-need abstraction.** An abstraction is introduced for a present or certain need, NEVER speculatively (SIMPL.3). A single-use abstraction is excess complexity under SIMPL, except the contracts DSGN.5 requires and the stand-ins DSGN.9 requires, whose second case is the test.
13. **DSGN.13 Room to scale.** Design choices SHOULD NOT preclude scaling the work is plausibly expected to need, so that it is admitted later without costly rework. Admitting scale is distinct from building it (SIMPL.3, RSRC.8).

**State and effects**

14. **DSGN.14 State.** Every piece of mutable state belongs to one component, has a stated lifetime, and is mutated visibly at the interface. Hidden global state SHALL NOT exist; hidden coupling through shared state is a design defect.
15. **DSGN.15 Concurrency.** Concurrent access to shared state follows a stated protocol whose invariants are verified (VV.10).
16. **DSGN.16 Effects.** Input/output, timing, hardware access, randomness, and mutation of shared state are confined to declared places, so computation is testable apart from them.
17. **DSGN.17 Randomness.** Randomness enters through an explicit source identified at the boundary, seedable wherever reproducibility requires (REPRO.1, REPRO.3).

## Article SIMPL — Simplicity

Complexity is the primary carrier of defects, cost, and misunderstanding, so every element of a system bears the burden of justifying its existence. This Article implements PRIN.3.

1. **SIMPL.1 Simplest sufficient design.** Among designs that meet the stated requirements, the simplest SHOULD be chosen. Simplicity is measured by what a competent human reader holds in mind to understand, verify, and change the system, not by its size or the sophistication of its construction.
2. **SIMPL.2 Essential and accidental complexity.** The governing model, mathematics, physics, and hardware constraints are as complex as they are, and that essential complexity is accepted. Everything added on top is accidental and bears the burden of proof.
3. **SIMPL.3 No speculative building.** Features, generality, configurability, and performance beyond the current, stated requirement are deferred until the requirement is real or the human owner records it as a requirement. Anticipated needs are recorded as notes, not implemented as code.
4. **SIMPL.4 Dependency cost.** Adopting, replacing, or removing a dependency is a recorded decision (REPRO.7), made under the project's dependency management (REPRO.9), that weighs the dependency's applicability to the problem, its active support, and the cost of carrying it against the alternative of an owned implementation.
5. **SIMPL.5 Indirection.** Every layer, wrapper, plugin mechanism, and configuration option exists for a specific, present consumer; one with none is removed.
6. **SIMPL.6 Explicit behavior.** Behavior SHOULD be declared rather than left to defaults, inference, convention, or environment. Where predicting the outcome requires a hidden rule, the rule is made visible in the code or the interface.
7. **SIMPL.7 Obvious implementation.** A clear, direct implementation is the reference against which each optimized or generalized replacement is verified, and the replacement SHALL demonstrate by measurement that it is needed.
8. **SIMPL.8 Deletion.** Code, options, data, and documentation that no longer serve a present purpose are removed from the active system. Anything a reported result depends on is retained in the record (REPRO.1, REPRO.12).
9. **SIMPL.9 Component retirement.** Retirement of a component or result is announced to its dependents and recorded (REPRO.7).
10. **SIMPL.10 Scope.** The purpose of a component or project is recorded. Work outside it is refused or spun off, NEVER quietly absorbed.
11. **SIMPL.11 Isolated complexity.** Irreducible essential complexity is confined to the smallest possible part of the system, documented in place, and guarded by evidence under VV proportionate to its difficulty.

## Article RSRC — Resources

Compute time, energy, memory, silicon, money, and human attention are finite, and spending them without measurement or need is waste. PRIME.8 states the non-waivable bound on spending; this Article states the rest. It implements PRIN.3, PRIN.4, PRIN.6, and PRIN.9.

**Budgets**

1. **RSRC.1 Budgets.** Each component whose resource use is material to a run states its material budgets; the system as a whole states its time, memory, energy, and cost budget, each with the problem size at which it SHALL be met.
2. **RSRC.2 Unknown budgets.** Where a budget is unknown or unknowable in advance, that is stated, resource use is measured and tracked from the first run so trends and regressions are visible, and a budget is stated as soon as the record supports one. Without a stated budget or a tracked record, no claim of adequacy or inadequacy SHALL be made.
3. **RSRC.3 Resource observability.** Time, memory, energy where measurable, and monetary cost of a run are recorded with the run (REPRO.4) so trends are visible and regressions caught.

**Optimization**

4. **RSRC.4 Measured optimization.** Optimization is undertaken only against a measured shortfall from a stated budget or an adverse trend in the tracked record, targets the measured bottleneck, and is retained only if measurement shows it closed the gap without violating VV.
5. **RSRC.5 Algorithm first.** Asymptotic complexity, rate of convergence where one applies, and choice of representation are settled before every lower-level optimization.
6. **RSRC.6 Supporting machinery.** Supporting machinery consumes time and energy at every invocation and SHALL justify itself against the work it supports. Machinery costing more than the computation it enables is excess under SIMPL, unless a higher-ranked Article requires it (GOV.5).
7. **RSRC.7 Reuse or recompute.** Whether to reuse or recompute results, intermediate quantities, and expensive setup is decided on measured cost. Reuse MAY occur only where it preserves correctness and reproducibility, and is recorded where it affects a budget.
8. **RSRC.8 Scale.** Parallelism, distributed execution, specialized hardware, and purchased capacity are adopted when a measured baseline at the smallest feasible scale shows they are necessary, or by a recorded decision of the human owner in anticipation of scale; their overhead and efficiency are measured against that baseline. Where the hardware or the scale is the object of the work rather than its means, the baseline serves comparison, not justification.

**Human time and attention**

9. **RSRC.9 Human time.** Design choices that save machine time at the cost of comprehension, verification effort, or maintenance are accepted only when the saving is measured, needed, and documented.
10. **RSRC.10 Human attention.** Information presented to a human during development and operation is concise, prioritized, and proportionate to the decision at hand. Volume that buries what matters is a defect, as is silence where action is needed.

**Effort**

11. **RSRC.11 Targeted verification.** Each verification step runs the smallest set of checks that establishes the evidence the change requires (VV.8); broader checking runs where the change's reach requires it or at release.
12. **RSRC.12 Deferred verification.** Verification is queued or deferred to the latest decision point at which its result is still needed, such as before reliance, promotion, release, or deployment, so that resources are not spent on evidence that later changes would invalidate. Deferral NEVER becomes omission (GOV.7).

## Article QA — Process

Work is done in bounded units, judged against criteria fixed in advance, reviewed by others, and corrected in the open. Process ranks last (GOV.5) because it is able to flex to serve every Article above it. This Article implements PRIN.1, PRIN.2, PRIN.4, and PRIN.6.

**Units of work**

1. **QA.1 Definition of done.** Projects MAY be open-ended; their units of work are not. Every unit of work has a definition of done and acceptance criteria (VV.3), recorded before the work is executed.
2. **QA.2 Work process.** Every project has a defined work process (GOV.21), in a form the project chooses, in which each unit of work is planned, executed, reviewed, and audited against its definition of done. Each stage leaves a record from which an auditor is able to reconstruct what was intended, what was done, and how it was judged.
3. **QA.3 Stopping rule.** Every project defines at inception a stopping rule (GOV.21) that bounds the effort, time, or cost spent on a unit of work without progress toward its definition of done. When the bound is reached, work on that unit halts and is reported to the human owner; an agent halts under GUARD.3. A unit of work created to continue halted work inherits the halted unit's bound. Only the human owner changes the rule or extends a bound, whenever the owner chooses, and the change is recorded.

**Defects**

4. **QA.4 Defect tracking.** Every project tracks its defects (GOV.21). Each defect is recorded with what it affects and whether it is blocking, and a tracked defect is resolved on a recorded schedule.
5. **QA.5 Defects found.** An actor that finds a defect outside its unit of work records it in defect tracking. The actor fixes it only if the fix is small, self-contained, within its scope and authority, and touches no work another actor is changing; otherwise it reports the defect to the human owner and to whoever is responsible for the affected work, and leaves the fix to them.
6. **QA.6 Broken checks.** An actor whose change breaks a test or other check restores it before the change is relied upon, by correcting the change or, where the check itself is wrong, by a recorded decision (REPRO.7) that leaves the original in the record (PRIME.2). Where the check lies outside the actor's area, it seeks the help of whoever is responsible for that area or a domain expert, through the human owner where needed.

**Review and release**

7. **QA.7 Review.** Every project has a review mechanism (GOV.21). Every change to code, data, workflow, or governance is reviewed, before release, against this document and the applicable lower governance by an actor other than its author, and the review is recorded.
8. **QA.8 Review independence.** Independence of review is proportioned to the consequence class (GOV.12). The independence each class requires is set by LVL2 standards and the project constitution.
9. **QA.9 Regeneration.** Reported results and release deployments to hardware are regenerated from their records by an actor or system other than their producer before they are relied upon, and the regeneration is recorded.
10. **QA.10 Release.** A release proceeds only on the decision of the human owner, with no open blocking defect, no expired waiver relied upon, and evidence current for the released revision.
11. **QA.11 Promotion.** A result SHALL NOT be reported before promotion: a recorded act by which the human owner adopts the proportionality judgment for its intended use (GOV.11) and confirms that the result, regenerated where that judgment requires, meets the acceptance criteria recorded before it was seen (VV.3), under VV and REPRO at the level the judgment sets; or, where the evidence VV requires is absent, confirms that the result is labeled unverified (PRIME.3) and that the gap is recorded. An agent MAY propose a promotion. Reporting an unpromoted result, or relying on one beyond its author, is a blocking defect.
12. **QA.12 Post-hoc criteria.** A result judged against criteria set after it was seen is promoted only as unverified (PRIME.3), with the criteria and when they were set recorded. Criteria chosen to fit the result are pathological evidence (PRIME.2).

**Correction**

13. **QA.13 Correction propagation.** Every project provides for correction propagation (GOV.21). When a result, dataset, component, knowledge entry, or decision is found wrong, everything that depends on it is identified from the record (REPRO.4), every known relying party, inside or outside the project, is notified, and each dependent is re-verified, corrected, or withdrawn (VV.8). The record is amended, NEVER silently replaced, and the correction is itself recorded.
14. **QA.14 Dependency tracking.** Dependencies between results SHOULD be tracked by a mechanism that identifies affected dependents automatically, so propagation does not rely on memory.
15. **QA.15 Incidents.** Every project has an incident mechanism (GOV.21). An incident is recorded with its root cause, the evidence added so that it is detected next time, and whether governance failed; a governance failure is reported to the custodians (GOV.47).

## Article GOV — Governance

This document is the root of authority for all governance of the work it covers, and it changes slowly, deliberately, and visibly. This Article sets authority and precedence, how obligations scale with consequence, how lower levels and profiles derive from LVL0, how knowledge and governance records are kept, and how governance changes. It implements PRIN.1, PRIN.9, and PRIN.10.

**Authority**

1. **GOV.1 Supremacy.** Where this document conflicts with a provision at a lower level, this document governs.
2. **GOV.2 Interpretation.** Provisions are read for their intent, stated in each Article's opening paragraph and in the Governing Principles, and resolved under GOV.9 when ambiguous. A provision of LVL0 or LVL1 is NEVER read to require a particular language, library, tool, technology, platform, process, or method; such a reading is wrong.
3. **GOV.3 Rulings.** The human owner interprets this document for a project and rules on questions referred to it. Each ruling is recorded, governs the project, and MAY be appealed to the custodians, whose recorded interpretations bind every project.
4. **GOV.4 Principle conflicts.** Where a provision addresses a matter expressly, it states what the principles require in that matter; a principle supplies the reading only where the provisions are silent or ambiguous. An apparent conflict between a principle and a provision is referred to the human owner for review and ruling (GOV.3), and the ruling is reported to the custodians as an amendment proposal (GOV.40).

**Precedence**

5. **GOV.5 Order of precedence.** The prime directives outrank every other provision. The Articles then rank as follows, highest first: (a) safety, security, and data integrity (GUARD); (b) correctness and honest evidence (VV); (c) reproducibility and traceability (REPRO); (d) interpretability and situational awareness (INTPR); (e) contractual, modular design (DSGN); (f) simplicity (SIMPL); (g) resources (RSRC); (h) process (QA). A provision below LVL0 ranks with the LVL0 provision it instantiates. The Governing Principles are not ranked, and GOV governs how all provisions apply and is not ranked. The order in which provisions appear carries no rank.
6. **GOV.6 Recorded concession.** When two provisions of different rank conflict, the higher-ranked governs; when provisions of equal rank conflict, the more restrictive governs, and an agent halts and refers (PRIME.14). The lower-ranked yields only to the minimum extent required, and only for as long as the conflict lasts, and the concession is recorded.
7. **GOV.7 Verification cost.** Verification cost NEVER justifies skipping verification. A component too expensive to verify by one means is verified by a cheaper one (VV.1); if no means exists, its results are reported as unverified (PRIME.3).
8. **GOV.8 Hardware constraints.** A footprint, timing, precision, or power limit imposed by the executing hardware is part of the contract (DSGN.5) and is honored as correctness; it belongs to VV rather than competing with it.
9. **GOV.9 Ambiguity.** When a provision of VV, REPRO, INTPR, DSGN, SIMPL, RSRC, or QA admits two readings, the reading that produces more evidence governs; among readings equal in evidence, the more explicit; among those, the simpler. The reading applies at the level the consequence class sets (GOV.11); an ambiguity in a floor obligation itself resolves to the reading that produces more evidence. When a prime directive, a provision of GUARD or GOV, or a permission for an agent's action admits two readings, the more restrictive governs, and an agent unable to tell halts and refers (PRIME.14). A reading so resolved governs until the provision is interpreted (GOV.3) or amended (GOV.40), and the judgment is recorded (PRIN.10).

**Consequence and proportionality**

10. **GOV.10 Floor.** Every piece of work, at every consequence class, meets a floor: the prime directives; GUARD and GOV; source under version control (REPRO.5); a definition of done for each unit of work (QA.1); documentation enough for a human and an agent to understand its purpose and use (INTPR.2); and tests for basic correctness and regressions (VV.7). At the floor, the mechanisms the prime directives, GUARD, and GOV require are met by the defaults (GOV.22).
11. **GOV.11 Proportioned obligations.** Above the floor, every obligation of VV, REPRO, INTPR, DSGN, SIMPL, RSRC, and QA, and of every lower provision that instantiates one, is proportioned to the consequence class of the work and the reliance placed on it, NEVER to the setting or hardware of the work (PRIN.9). The proportionality judgment, which states the consequence class and the reliance placed on the work, is recorded and adopted by the human owner. Exploratory overhead is kept as low as the floor allows, and lower governance SHALL NOT raise the floor except by a recorded project decision naming the consequence that warrants it.
12. **GOV.12 Consequence classes.** The consequence class of work is the most severe class reached by the worst credible consequence of an error in it, harm included, or by the reliance placed on it. The classes, most severe first, are:
    - **CSQ0 Safety-critical.** An error is able to cause injury, death, or severe environmental harm, directly or through a safety decision the output informs.
    - **CSQ1 Mission-critical.** An error is able to cause major, hard-to-reverse loss, such as destroyed equipment, irreplaceable data or samples, a failed campaign, or large cost, without credible injury; or the output is relied upon outside the project or by systems that act unattended.
    - **CSQ2 Relied upon.** An error is able to cause wrong decisions or designs, recoverable with substantial rework; the output is relied upon beyond its author.
    - **CSQ3 Internal.** An error wastes effort and is caught cheaply and reversed; the output is relied upon only by its author or immediate team, feeding work that is verified later.
    - **CSQ4 Exploratory.** An error costs nothing beyond the author's own time; nothing is relied upon without promotion (QA.11).

    Detailed criteria for each class are LVL2 standards. A profile MAY require work in its domain to be classified at least as severe as a stated class.
13. **GOV.13 Class assignment.** The human owner sets the project's consequence class at inception, as the most severe class of its intended uses, and MAY revise it throughout the project's life. The human owner MAY record a less severe class for a component shown to be isolated from the more severe outputs. No class is assumed by default: where none is recorded, an agent that needs it halts that line of work and refers (PRIME.14).
14. **GOV.14 Class follows use.** A consequence class attaches to the use of work, not to its code. The class moves toward CSQ0 whenever reliance or exposure grows, and away from CSQ0 only by recorded decision of the human owner. Work moved to a more severe class meets that class's obligations before it is relied upon at that class; nothing is grandfathered.
15. **GOV.15 Physical harm.** Where the human owner states that a credible path to physical harm exists, the work is CSQ0 whatever the other dimensions indicate. An agent NEVER makes that determination; it MAY warn the human owner of scenarios that are able to pose physical harm.

**Levels and derivation**

16. **GOV.16 Levels.** Governance is organized in four levels, each adopted by a narrower authority than the one above it: LVL0, this constitution; LVL1, profiles of domain obligations; LVL2, standards and defaults that apply across projects; and LVL3, the instruments of one project. Only LVL0 carries constitutional force in its own right; every lower level binds by derivation (PRIME.15).
17. **GOV.17 Inherited force.** A provision below LVL0 inherits the rank and waivability of the provisions it instantiates and SHALL NOT be assigned a lower rank or a looser waivability. A provision that instantiates a prime directive is non-waivable.
18. **GOV.18 Specificity downstream.** Choices of language, library, tool, technology, platform, process, and method belong at LVL2 and LVL3. LVL0 and LVL1 name none of them, so a change to those choices leaves LVL0 and LVL1 unchanged.
19. **GOV.19 Binding and default.** Each LVL2 provision is marked binding or default. A provision is marked binding only where it instantiates a prime directive, GUARD, or a floor obligation (GOV.10), or where the custodians record why uniformity across projects requires it; every other LVL2 provision, including every provision of form or style, is a default. A binding provision is only tightened below it; a default provision MAY be replaced at LVL3 by an alternative that meets the same higher-level outcome, recorded as a decision (REPRO.7).
20. **GOV.20 Project constitution.** Every project that promotes a result, releases software, or drives physical hardware has a project constitution: a LVL3 instrument that inherits from and aligns with the levels above it, cites the provisions it instantiates, adds only project-specific obligations, and relaxes none (PRIME.15).
21. **GOV.21 Project mechanisms.** The project constitution defines the mechanisms this document requires of every project: the work process (QA.2), the stopping rule (QA.3), defect tracking (QA.4), review (QA.7), correction propagation (QA.13), incident handling (QA.15), dependency management (REPRO.9), retention (REPRO.12), the classification and consequence class (GOV.13, GOV.24), the working-notes workspace (INTPR.5), the threat model (GUARD.16), the reserved-action register (GUARD.4), the authorization mechanism (GUARD.10), and the agent instructions (PRIME.14, GOV.48).
22. **GOV.22 Defaults.** Work without a project constitution operates under defaults that the custodians adopt as LVL2 standards. No default grants an authorization, adopts a hazard analysis, sets a consequence class, or authorizes an estimate; only the human owner does.

**Profiles**

23. **GOV.23 Universality.** The prime directives and General Articles are stated as outcomes that every domain and every piece of hardware is able to satisfy. They bind all covered work, whether or not a profile applies.
24. **GOV.24 Classification.** Each project's classification records its consequence class and the attributes of its work that profile selectors test. The classification is adopted by the human owner (GOV.50) and revised whenever the work changes in a way a selector tests.
25. **GOV.25 Profile selection.** Every profile whose selector is true for a project's classification binds that project in full, and a project MAY select more than one. A conflict between selected profiles resolves under the order of precedence (GOV.5).
26. **GOV.26 Profile consistency.** Each profile states its selector, which is decidable from classification attributes, and cites the LVL0 provisions each of its provisions instantiates. It defines its own terms without redefining a LVL0 term, and it contradicts no other profile.
27. **GOV.27 Sub-profiles.** A sub-profile inherits its parent profile in full and adds only obligations specific to its subtype.
28. **GOV.28 Profile admission.** A profile or sub-profile is admitted, without amendment to LVL0, when it meets GOV.26 and the custodians adopt it (GOV.41). Projects whose classification it selects conform within a recorded transition period (GOV.42).
29. **GOV.29 Unprofiled work.** Covered work in a domain no profile addresses is governed by LVL0, and by the nearest profile applied by analogy, with the choice of analogue recorded, until a profile for it is admitted.
30. **GOV.30 Constitutional scope.** This document binds computational and cyber-physical systems and the work done on them, which is the covered work. General business and web software are outside it until an admitted profile whose selector names that software brings it in; from then on, LVL0 binds it in full. Matters the Preamble assigns to parallel governance are outside this document, and no provision is read to govern them.
31. **GOV.31 Profile pruning.** A profile provision that restates a higher provision without domain-specific content is removed. A profile for a retired domain or hardware type is retained only while results produced under it remain in use (REPRO.1).

**Knowledge**

32. **GOV.32 Knowledge without authority.** Acquired knowledge, such as methods, prior art, research and negative results, lessons learned, and trends, is kept in a knowledge base apart from governance. A knowledge entry informs the work and NEVER governs it; it carries no instruction authority (PRIME.11). An entry that SHOULD bind becomes a provision only by adoption at the lowest level able to hold it.
33. **GOV.33 Reliance ceiling.** Each knowledge entry records its evidence and its evidence level, from EVD0 verified through EVD3 anecdotal. The evidence level caps the most severe consequence class at which the entry is relied upon without fresh verification; the ceiling for each level is a LVL2 standard. Reliance above the ceiling requires the evidence VV requires at the class concerned.
34. **GOV.34 Knowledge lifecycle.** A knowledge entry is established only on review by an actor other than its author and is revalidated on a recorded schedule. It is superseded or retracted, NEVER altered in place (PRIME.5), and everything that relies on it is notified (QA.13).

**Governance records**

35. **GOV.35 Corpus.** The text of every provision at every level is kept in plain, versioned files that a human is able to read without special software. This corpus is authoritative; every rendered document, index, and manifest is generated from it and NEVER substitutes for it.
36. **GOV.36 Ledger.** Every change to governance at every level, and every adoption, classification, authorization, waiver, ruling, and promotion, is entered as a transaction in an append-only, tamper-evident ledger that records its actor, role, authority, and rationale. The current state of governance is derivable from the corpus and the ledger alone. A change made outside the ledger is a defect.
37. **GOV.37 Stable identifiers.** Every provision, knowledge entry, and tag has a stable identifier that is NEVER reused or renumbered. Identifiers are built from mnemonics, so that an identifier names its document or Article; the identifier scheme is a LVL2 standard. An ordinal scale appends one digit to its mnemonic, numbered from 0 for the highest authority, severity, or strength (LVL0, CSQ0, EVD0). Mnemonics are held in a register that changes only by ledger transaction. Section, level, and rank are attributes of a provision, not parts of its identifier.
38. **GOV.38 Harness.** Software that stores, checks, renders, or serves governance holds no authority of its own; it implements governance and is governed as software. If it is lost, the corpus, the manifests, and the ledger remain sufficient for a human skilled in the art to read, apply, and audit governance (INTPR.12).
39. **GOV.39 Manifests.** A manifest lists provisions or knowledge entries for lookup and is informative; before relying on a provision, an actor reads its full text. A manifest that does not match the corpus it was generated from is stale and is regenerated before use.

**Change**

40. **GOV.40 Amendment.** A provision of this document is added, altered, or removed only by decision of the custodians, on a recorded proposal stating the provision, the change, the reason, the alternatives weighed, and the lower governance affected. A change takes effect when recorded in this document's revision history and entered in the ledger (GOV.36).
41. **GOV.41 Adoption.** The custodians adopt this document, the LVL1 profiles, and the LVL2 standards; they MAY delegate a standard to an owner they name, who then adopts it. A project's human owner adopts that project's LVL3 instruments.
42. **GOV.42 Transition.** Each adopter reviews the lower provisions a change affects and conforms them within a transition period the custodians record; work conforming to the prior revision during that period is not in defect.
43. **GOV.43 Versioned governance.** Governance at every level is versioned, reviewed, and attributed as code is (REPRO.5, QA.7), and its history is preserved (PRIME.5).
44. **GOV.44 Waiver.** Above the floor (GOV.10), a waiver MAY relieve an obligation of VV, REPRO, INTPR, DSGN, SIMPL, RSRC, or QA, or of a lower provision that instantiates one, for a named component, for a stated reason and duration, by a recorded decision of the human owner. A waiver names the provision, the risk accepted, and the condition under which it expires. Relying on an expired waiver is a defect. A waiver is the form an exception under PRIN.10 takes when it departs from a provision.
45. **GOV.45 Non-waivable obligations.** The Governing Principles, the prime directives, GUARD, GOV, the floor (GOV.10), and every provision at every level that instantiates a prime directive SHALL NOT be waived.
46. **GOV.46 Constitutional review.** This document is reread in full at an interval the custodians record, and each profile and standard is reviewed at an interval its adopter records. Each review records whether a provision has been routinely waived, ignored, or found ambiguous; each such finding is an amendment proposal.
47. **GOV.47 Compliance audit.** Each project's compliance with this document and its lower governance is audited at an interval proportioned to its consequence class. The project reports its waivers, rulings, recorded ambiguities, and governance failures to the custodians.

**Agents in governance**

48. **GOV.48 Agents bound.** Agents acting on covered work are governed by agent instructions derived under PRIME.15, and are held to the prime directives, GUARD, and INTPR.11 for every action. They SHALL NOT grant themselves waivers (GOV.44).
49. **GOV.49 No self-adoption.** An agent SHALL NOT adopt, put into force, or alter in force governance, whatever its level, its own instructions included. It MAY draft and propose changes, which only their adopter (GOV.41) adopts.
50. **GOV.50 Owner-adopted judgments.** Judgments that set the burden on the work are adopted only by the human owner, and an agent MAY draft them: the classification, consequence class, and proportionality judgment (GOV.11, GOV.13, GOV.24); promotion (QA.11); axioms (VV.9); the hazard analysis (PRIME.13); the reserved-action register and its exempt classes (GUARD.4, GUARD.7); estimates for implicit expenditure (PRIME.8); and the decision to release or deploy (QA.10).
51. **GOV.51 Agent designation.** Software that meets the definition of an agent, or that is not shown to execute only a fixed specification, is treated as an agent until the human owner records otherwise. Software an agent invokes acts within that agent's tiers and authority (PRIME.12).

## Lexicon

This Lexicon fixes the meaning of every defined term in this constitution; normative words are fixed in Normative Language. A definition states what a term means, not what is required of it; obligations are stated in the provisions. Lower governance uses these terms in exactly this sense; it MAY define further terms and SHALL NOT redefine these. An unlisted term carries its ordinary meaning in the discipline of its use. Domain terms are defined in the profile that uses them.

Terms that sound alike have distinct jobs. A register holds current state, the ledger holds the history of changes to governance, a record is evidence about the work, a manifest is a lookup list, and an index is a generated map; the word "registry" is not used. Likewise, a tag names a subject, and a selector decides whether a profile applies. Terms are grouped by the part that governs them and sorted alphabetically within each group.

**Roles**

One person MAY hold several roles; the roles remain distinct. This document does not use the word "user"; lower governance names the specific role instead.

| Term | Definition | Governed by |
| --- | --- | --- |
| Actor | Any person or agent acting on the covered work. | PRIN.1, PRIN.5, PRIME.11, GOV.48 |
| Adopter | The person or body that adopts a governance document or instrument: the custodians, or the owner they name for a standard, and the human owner for a project's LVL3 instruments. | GOV.41, GOV.42, GOV.46, GOV.49 |
| Agent | Software that selects its own actions toward a goal on the covered work. Automation that only executes a fixed specification is software, governed as such, and not an agent. | GUARD.1, GOV.48, GOV.51 |
| Auditor | An actor who examines the records of a unit of work, or of a project's compliance with its governance, to reconstruct what was intended, what was done, and how it was judged. | QA.2, GOV.47 |
| Author | The actor, person or agent, that makes a change, entry, or result. | REPRO.5, QA.7, GOV.34 |
| Custodians | The person or body that adopts and amends this document, the profiles, and the standards, and that hears appeals from project rulings. Custodians act across projects; a human owner acts within one. | GOV.3, GOV.40, GOV.41 |
| Human owner | The person accountable for a project and for its technical products, decisions, and releases, who adopts its LVL3 instruments and judgments, grants its authorizations, and rules on questions referred to it. Who the owner is, and how ownership is assigned or succeeded, is governed outside this document. | PRIN.1, PRIME.1, GOV.3, GOV.41, GOV.50 |
| Operator | The person who runs a system, or acts on its outputs, while it runs. | INTPR.6, INTPR.10 |
| Relying party | Anyone, inside or outside the project, who uses or acts on a reported result or released system, including those commonly called users. | PRIN.6, QA.13 |
| Reviewer | The actor who performs a review, an actor other than the author of the change. | QA.7, QA.8 |
| Standards owner | The owner whom the custodians name to adopt a standard they delegate. | GOV.41, PRIME.1 |
| Successor | A person or agent who takes up the work from those who built it. | INTPR.13 |

**Correctness (PRIME.2–PRIME.4, VV)**

| Term | Definition | Governed by |
| --- | --- | --- |
| Acceptance criteria | The tolerances, metrics, and checks that judge whether a result meets its definition of done. | VV.3, QA.1, QA.11 |
| Axiom | An assumption the human owner declares to hold without demonstration. | VV.9 |
| Correctness | Agreement between what a system does and its specification, the specification being validated where a real-world referent exists. | VV.4 |
| Evidence | A reproducible comparison against a reference of known provenance, or a proof, derivation, or confirmed citation whose assumptions are stated and shown to be met. Assertion, inspection, and unsupported authority are not evidence. | VV.1 |
| Invariant | A property the governing model, logic, or specification requires throughout execution, such as conservation, a bound, monotonicity, or symmetry. | VV.10, DSGN.1 |
| Loud failure | Halting, visibly degrading, or reaching a safe state, with an actionable diagnosis, on invalid input, violated precondition, non-convergence, or resource exhaustion. | PRIME.4 |
| Misrepresented evidence | A citation not confirmed to support its claim, a check claimed but not run, or an output misreported. | PRIME.2 |
| Pathological evidence | Evidence that is trivial, tautological, vacuous, or self-referential, or obtained by adjusting the test, reference, or acceptance criterion to fit the output under test (reward hacking). | PRIME.2 |
| Reference, oracle | An independent quantity of known provenance against which a result is compared. | VV.1, VV.7 |
| Regression guard | A test whose comparison is the system's own prior output, which is not a reference; it detects change, not correctness. | VV.7 |
| Specification | The written statement of what a component or system is required to do, including its behavior, its limits, and its domain of validity. | VV.4, INTPR.10 |
| Test | A specification with an oracle: a stated behavior plus its reference. | VV.7 |
| Validation | Evidence that the specification represents the real-world system, process, or intended use it serves (specification to world). | VV.4, VV.5 |
| Verification | Evidence that the implementation meets its specification (specification to implementation). | VV.4, VV.5, VV.6 |

**Reproducibility (PRIME.5, REPRO)**

| Term | Definition | Governed by |
| --- | --- | --- |
| Computational environment | The properties of the computational setting that affect results. | REPRO.1, REPRO.2 |
| Decision record | The written choice, alternatives considered, and reason. | REPRO.7 |
| Dependency | Any external component a result relies on. | REPRO.9, SIMPL.4 |
| Dependency management | The project mechanism that enumerates, pins, justifies, and reviews dependencies. | REPRO.9 |
| Determinism | Identical recorded inputs yield identical outputs. | REPRO.3 |
| Dissent | An objection to a technical decision. | PRIN.2, REPRO.8 |
| Input | Anything a result depends on: source at a revision, parameters, data at a revision, seeds, observations, hardware identity and configuration, result-affecting properties of the computational environment, and, for agent-performed steps, the agent's identity, configuration, and instruction revision. | REPRO.1, REPRO.2, REPRO.11 |
| Provenance | The record of a result's inputs and producer. | REPRO.4 |
| Record | Durable evidence about the work, such as provenance, inputs, decisions, and results, kept as REPRO requires. | REPRO.4, REPRO.7, PRIME.5 |
| Reproducibility | The ability to regenerate a result from its recorded inputs. | REPRO.1, QA.9 |
| Result | Any output derived for use: a number, dataset, figure, or deployed configuration. | REPRO.1 |
| Retention | The period and form in which a project keeps its records and results. | REPRO.12 |
| Revision, identity | An immutable identifier naming one exact version of code, data, or a dependency. | REPRO.5, REPRO.6, REPRO.9 |
| Traceability | The ability to follow any result back to the inputs, decisions, and evidence that produced it. | REPRO.4, REPRO.7 |
| Workflow | A sequence of steps, automated, manual, or agent-performed, that produces a result. | REPRO.10, REPRO.11 |

**Design and simplicity (DSGN, SIMPL)**

| Term | Definition | Governed by |
| --- | --- | --- |
| Accidental complexity | Complexity introduced by the solution rather than the problem. | SIMPL.2 |
| Component | A bounded piece of software, or of a hardware description, with a stated interface and the concerns it is responsible for. | DSGN.8, DSGN.9 |
| Composition | Building a component from independent parts that it uses, rather than by extending another component. | DSGN.10 |
| Contract | The declared preconditions, postconditions, and invariants of an interface, or the stated behavior relied upon from an external component or hardware. | DSGN.1, DSGN.5 |
| Effect | Input/output, timing, hardware access, randomness, or mutation of state shared beyond the computation. | DSGN.16 |
| Essential complexity | Complexity inherent in the problem: its governing model, mathematics, physics, and hardware constraints. | SIMPL.2 |
| Extension point | A designated place where a new variant enters without altering verified code. | DSGN.11, DSGN.12 |
| External component | Code, data, a service, hardware, or other material a project relies on but does not itself produce. | DSGN.5, REPRO.9 |
| Indirection | Anything placed between a caller and the computation it reaches. | SIMPL.5 |
| Inheritance | Building a component by extending another component, so that it acquires the other's structure and behavior. | DSGN.10 |
| Interface change | A change to a contract others rely on. | DSGN.6 |
| Interface, boundary | The surface through which a component is used; where its contract is checked. | DSGN.1, DSGN.2 |
| Mechanical checking | Verification of a property by a procedure that follows fixed rules without judgment, such as formal type checking. | DSGN.3 |
| Obvious implementation | The clearest direct implementation of a requirement. | SIMPL.7 |
| Postcondition | What a component guarantees on return, given its preconditions held. | DSGN.1, DSGN.2 |
| Precondition | What a component requires of its caller before invocation. | DSGN.1, DSGN.2 |
| Schema | The declared shape, units, conventions, and validity range of data crossing an interface. | DSGN.4 |
| Scope | The recorded purpose and boundary of a project, component, unit of work, or authorization. | SIMPL.10, GUARD.10 |
| Separable | Independently testable, replaceable, and understandable in isolation. | DSGN.9 |
| State | Data that persists between operations and is able to change. | DSGN.14, DSGN.15 |

**Interpretability and resources (INTPR, RSRC)**

| Term | Definition | Governed by |
| --- | --- | --- |
| Anomaly | A departure from expected behavior detectable before it becomes a failure. | INTPR.7 |
| Baseline | The measured performance at the smallest feasible scale, against which optimization and scale are judged. | RSRC.8 |
| Budget | A stated limit on time, memory, energy, cost, or another resource at a stated problem size. | RSRC.1, RSRC.2 |
| Diagnostic | Information captured by design so that a failure is able to be understood from its record. | INTPR.8 |
| Domain of validity | The regime of inputs and conditions over which a method, model, or instrument is trusted. | INTPR.10 |
| Graceful degradation | Loss of automation, agents, or tooling leaves the work understandable and resumable by a skilled human from its artifacts alone. | INTPR.12, GOV.38 |
| Human-facing documentation | Comments and documentation written for human readers first. | INTPR.2, INTPR.5 |
| Resource | Compute time, energy, memory, silicon area, money, or human attention. | RSRC |
| Self-describing output | An output that states what it is, what produced it, its units and conventions, and its uncertainty or confidence basis, readable without the producing software. | INTPR.9 |
| Situational awareness | The operator's accurate, current understanding of what a system is doing and why. | INTPR.6 |
| Supporting machinery | Everything beyond the computation itself that it requires in order to run. | RSRC.6 |
| Working-notes workspace | A designated location, separate from human-facing documentation, where any actor records working notes, plans, and context for later recovery. | INTPR.5, GOV.21 |

**Process (QA)**

| Term | Definition | Governed by |
| --- | --- | --- |
| Correction propagation | Identification, notification, and re-verification, correction, or withdrawal of everything that depends on a result found wrong. | QA.13 |
| Defect | A nonconformance with governance at any level, blocking or tracked as Normative Language defines. | QA.4, QA.5 |
| Definition of done | The recorded condition under which a unit of work is complete. | QA.1 |
| Incident | A defect that reached a reported result, a release, or physical hardware. | QA.15 |
| Promotion | The human owner's recorded act that makes a result reportable at the level of obligations its proportionality judgment sets (GOV.11). | QA.11 |
| Regeneration | Reproduction of a result from its records by an actor or system other than its producer. | QA.9 |
| Release | Making a revision of software, a workflow, or a hardware configuration available for use beyond its development. | QA.10 |
| Reported result | A result communicated or used beyond its author to be relied upon. | QA.11 |
| Review | Examination of a change, before release, by an actor other than its author, against this document and the applicable lower governance. Applied to anything other than a change, such as a threat model, an axiom, a pinned revision, a knowledge entry, or a standard at its review interval, the word carries its ordinary meaning of a re-examination. | QA.7, QA.8 |
| Stopping rule | A bound on effort spent without progress toward a definition of done. | QA.3 |
| Unit of work | A task, subtask, or other bounded piece of work with its own definition of done. | QA.1, QA.2 |
| Work process | The project mechanism by which each unit of work is planned, executed, reviewed, and audited against its definition of done. | QA.2 |

**Safeguards (PRIME.6–PRIME.14, GUARD)**

| Term | Definition | Governed by |
| --- | --- | --- |
| Authorization | A grant by the human owner of permission for an action or class of actions, within a scope and duration. | PRIME.7, GUARD.10, GUARD.11, GUARD.12 |
| Bulk action | A destructive action or remote write whose full scope is not enumerated and verified before execution, or exceeds a size the register sets. | GUARD.6 |
| Bulk retrieval | Retrieval of a dataset or collection, or of more items or volume than an authorization names. | GUARD.8 |
| Elevated privilege | Superuser or administrative permission on any system, including within an isolated environment, or any other permission beyond what the human owner provisioned for an agent's environment. | PRIME.9 |
| Explicit monetary transaction | An action whose purpose is to pay, purchase, or subscribe, or to create or raise a billing commitment or spending limit. Consumption of capacity under an existing commitment is implicit expenditure. | PRIME.6 |
| Findings and justification statement | A written record, with recommended actions, sufficient for the human owner to decide on a referred matter and to verify its outcome. | PRIME.14 |
| Halt and refer | Stop the line of work before the action, produce a findings and justification statement, and take no further action on that path until the human owner decides. | PRIME.14, GUARD.3 |
| Hazard analysis | The identification of the hazards a system poses and the designed response to each. | PRIME.13 |
| Implicit expenditure | Any cost an action incurs other than by an explicit monetary transaction, including tokens, credits, and metered or post-paid capacity. | PRIME.8, GUARD.15 |
| Instruction authority | The standing of a source whose directions an agent follows. | PRIME.11 |
| Irrecoverable action | An action whose effect on data, history, records, or state is not undoable from a verified recoverable prior state, other than an action of a class exempt under GUARD.7. | GUARD.5, GUARD.9 |
| Network access | Any transfer of data to or from a system outside the provisioned environment, other than over the channel that carries the agent's own instructions and responses. | PRIME.7, GUARD.13 |
| Operating envelope | A rigorously and faithfully derived estimate of an agent's own operating cost over a stated period, authorized by the human owner as a standing limit. | GUARD.14, GUARD.15 |
| Physical hardware | Actuated, energized, or emitting equipment outside the computational substrate that controls it, whose state or action is able to harm people, property, or the environment, such as a robot, laser, power supply, or signal generator. Computing hardware protected by its own operating system and onboard circuitry is not physical hardware. | PRIME.13 |
| Provisioned environment | The computing environment, with its privileges and reach, that the human owner provides for an agent. | PRIME.9 |
| Remote write | Any action that creates, alters, or publishes content on, or sends data or messages to, a system outside the agent's provisioned environment, other than an authorized retrieval request. | PRIME.7, GUARD.11 |
| Reserved action | An action only the human owner executes: an irrecoverable or bulk action, bulk retrieval, an explicit monetary transaction, or hazardous or irreversible actuation of physical hardware. | PRIME.6 |
| Reserved-action register | A project's record of the classes of action that are reserved and of the classes exempted. | GUARD.4, GUARD.7 |
| Safe range of actuation | Bounds on actuation parameters, specified and authorized by the human owner, within which an agent's actuation is permitted. | PRIME.13 |
| Safe state | A designed condition of a physical system in which it causes no harm. | PRIME.4, PRIME.13 |
| Secure practice | Practice that defends what the project's threat model protects against the threats it names. | GUARD.17 |
| Standing authorization | An authorization covering a class of actions within a stated scope and duration. | GUARD.11 |
| Temporary item | An item created to hold an intermediate, recorded as temporary from its creation, that no record cites. | GUARD.7 |
| Threat model | A project's statement of what it protects, from whom, and, separately, what it does not attempt to protect. | GUARD.16 |

**Governance (PRIME.1, PRIME.15, GOV)**

| Term | Definition | Governed by |
| --- | --- | --- |
| Agent instructions | The lower governance that directs agents acting on a project, including the form of the findings and justification statement. It carries instruction authority only once adopted. | PRIME.11, PRIME.14, GOV.21, GOV.48 |
| Amendment | A recorded change to an adopted governance document. | GOV.40, GOV.41 |
| Binding provision | A LVL2 provision that lower levels may only tighten. | GOV.19 |
| Classification | The owner-adopted record of a project's consequence class and of the attributes of its work that profile selectors test. | GOV.24, GOV.25 |
| Compliance audit | An examination of whether a project's work meets this document and its lower governance. | GOV.47 |
| Computational and cyber-physical system | Software, workflows, and the hardware they drive, read, or execute on, whose outputs or actions are relied upon, where a computation, a measurement, or an action on the physical world bears on a result, a decision, or safety. | Preamble, GOV.30 |
| Consequence class | One of five grades, CSQ0 safety-critical through CSQ4 exploratory, set by the worst credible consequence of an error in the work and the reliance placed on it. | GOV.12, GOV.13, GOV.14 |
| Constitutional review | The periodic full rereading of this document. | GOV.46 |
| Corpus | The plain, versioned files holding the text of every provision, from which every rendered document, index, and manifest is generated. | GOV.35 |
| Covered work | Computational and cyber-physical systems and the work done on them, within the scope GOV.30 states. | GOV.30 |
| Default provision | A LVL2 provision that a LVL3 instrument may replace with an alternative meeting the same outcome, recorded as a decision. | GOV.19 |
| Drafting standard | A LVL2 standard fixing how normative words are written below LVL0 and which confounding expressions are excluded. | Normative Language |
| Evidence level | The grade, EVD0 verified, EVD1 confirmed, EVD2 reported, or EVD3 anecdotal, of the support behind a knowledge entry. | GOV.33 |
| Exception | A departure in how a principle is implemented, or a judgment made in an ambiguous situation. | PRIN.10, GOV.44 |
| Floor | The obligations that bind every piece of work at every consequence class. | GOV.10 |
| General Article | An Article of LVL0 stating domain-neutral obligations: GUARD, VV, REPRO, INTPR, DSGN, SIMPL, RSRC, and QA. All but GUARD are proportioned to consequence class and waivable. | GOV.11, GOV.44 |
| General business and web software | Software whose principal function is transaction processing, content delivery, or user interaction, rather than computation, measurement, or control whose outputs or actions are relied upon for a result, a decision, or safety. | GOV.30 |
| Harness | Software that stores, checks, renders, or serves governance and enters transactions; it holds no authority of its own. | GOV.38 |
| Index | A map generated from the corpus or the ledger for fast lookup. It is not authoritative. | GOV.35 |
| Interpretation | A recorded reading of a provision for a project or, by the custodians, for every project. | GOV.2, GOV.3 |
| Knowledge base | The curated collection of knowledge entries for a project or shared across projects. It carries no instruction authority. | GOV.32 |
| Knowledge entry | One reusable claim with its kind, evidence, evidence level, domain of validity, provenance, and status. | GOV.32, GOV.33, GOV.34 |
| Ledger | The append-only, tamper-evident sequence of transactions from which, with the corpus, the current state of all governance is derived. | GOV.36 |
| Level | One of LVL0 constitution, LVL1 profiles, LVL2 standards, and LVL3 project instruments; each derives from and only tightens the levels above it. | GOV.16 |
| Lower governance | Any provision below LVL0: profiles, standards, defaults, project constitutions, coding standards, review checklists, agent instructions, and other project instruments. | PRIME.15, GOV.16 |
| Manifest | A generated, scoped list of provisions or knowledge entries, giving enough of each to find it, for lookup. It is informative only. | GOV.39 |
| Mnemonic | An uppercase identifier segment, held in the mnemonic register, naming a document, Article, profile, sub-profile, level, class, grade, or knowledge or tag space. | GOV.37 |
| Precedence | The ranking applied when two provisions conflict: the prime directives first, then the Articles in the order GOV.5 sets; the Governing Principles are not ranked. | GOV.5 |
| Prime directive | A LVL0 provision that binds at every consequence class, is never waivable, and outranks every other provision. | PRIME, GOV.45 |
| Profile | A LVL1 document of domain obligations that binds a project when its selector is true. | GOV.16, GOV.25, GOV.26 |
| Project | A body of work with a recorded scope and a human owner. | GOV.20 |
| Project constitution | The LVL3 governing document of one project. | GOV.20, GOV.21 |
| Project instrument | A LVL3 artifact the human owner adopts for one project: project constitution, classification, registers, authorizations, waivers, rulings, and the like. | GOV.16, GOV.41 |
| Proportionality judgment | The human owner's recorded judgment of the consequence class of work and the reliance placed on it, which sets the level of the obligations above the floor. | GOV.11 |
| Provision | One numbered, atomic statement of governance at any level, with a stable identifier. | GOV.37 |
| Register | A current list of one kind of governed item, such as reserved actions, exempt classes, authorizations, or mnemonics. It changes only by ledger transaction. | GUARD.4, GOV.36, GOV.37 |
| Reliance ceiling | The most severe consequence class at which a knowledge entry may be relied on without fresh verification. | GOV.33 |
| Ruling | The human owner's recorded decision on a question referred to it. | GOV.3, GOV.4 |
| Safety | Freedom from harm to people, property, and the environment, and the integrity and security of data, records, and systems. | PRIN.8, GOV.5 |
| Selector | A predicate over a project's classification that decides whether a profile binds. | GOV.25, GOV.26 |
| Stable identifier | An identifier built from mnemonics (such as VV.7 or GOV.12) that is never reused or renumbered. | GOV.37 |
| Standard | A LVL2 document of cross-project provisions, each binding or default, which may name tools and methods. | GOV.16, GOV.19 |
| Sub-profile | A profile that inherits a parent profile and adds only obligations specific to its subtype. | GOV.27 |
| Tag | A governed subject term with a stable identifier, used to classify knowledge entries and provisions for lookup. It is informative only and never makes a provision apply. | GOV.37 |
| Transaction | A recorded, attributed change entered in the ledger, such as an adoption, amendment, classification, authorization, waiver, ruling, or promotion. | GOV.36 |
| Waiver | A recorded, scoped, time-limited relief from a waivable obligation for a named component. | GOV.44, GOV.45 |

## Revision History

| Revision | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-10-08 | Ratified. |
| 1.0.1 | 2026-10-09 | Editorial amendment (GOV.40): LEX.index states in descriptive words, not with a capitalized normative word, that an index is not authoritative; no obligation changes. |
| 1.0.2 | 2026-10-09 | Editorial amendment (GOV.40): the Lexicon defines three roles that provisions already use, Author (REPRO.5, QA.7, GOV.34), Adopter (GOV.41, GOV.42, GOV.46, GOV.49), and Auditor (QA.2, GOV.47); no obligation changes. |
| 1.0.3 | 2026-10-09 | Editorial amendment (GOV.40): the ratification record names the role that ratified the constitution, The Custodian, in place of a blank; no obligation changes. |
| 1.1 | 2026-10-09 | Minor amendment (GOV.40): Normative Language lists SHOULD NOT and its lowercase form should not beside SHOULD, so that every normative word is fixed in one place; DSGN.13 already used SHOULD NOT with this meaning. |
| 1.2 | 2026-10-09 | Minor amendment (GOV.40): LVL0 conforms to the drafting standard, STND.DRAFT. Forty-two edits across forty provisions replace excluded expressions (prohibited, permitted, ought to, need not, has to, required) with table words, replace the review-class words could and considered, and replace the quantifier any where a plainer word is available. GUARD.18 now names who records what is practical: the human owner. No other obligation changes. |
| 1.2.1 | 2026-10-09 | Editorial amendment (GOV.40): four phrasings introduced in 1.2 (GOV.13, GUARD.12, PRIME.13, QA.3) read at will, and the drafting standard reads will as SHALL; they now read throughout the project's life or whenever the actor chooses; no obligation changes. |
| 1.3 | 2026-10-09 | Minor amendment (GOV.40): the Lexicon defines the roles Reviewer and Standards owner; Promotion makes a result reportable at the level of obligations its proportionality judgment sets, not at an evidence level; Amendment covers every adopted governance document; Auditor covers compliance audits; Normative Language lists NEVER, which LVL0 uses, in place of SHALL NEVER, which it no longer uses. |
| 1.4 | 2026-10-10 | Minor amendment (GOV.40): the Lexicon entry Review keeps its meaning for a change and states that the word carries its ordinary meaning of a re-examination where it is applied to anything else, as in GOV.4, GOV.42, GOV.46, GUARD.16, VV.9, and REPRO.9. |
| 1.5 | 2026-10-10 | Minor amendment (GOV.40): GUARD.7 adds a third ground of exemption, the removal or overwriting of temporary items only; the Lexicon defines Temporary item, and Irrecoverable action excludes an action of an exempt class, so that PRIME.6 no longer reserves an exempt action; GUARD.6 still prevails over every exemption. |