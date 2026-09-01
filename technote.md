Workshop note · Who Controls, Who Answers?
Building the Front Door
Four objections from the people who would have to implement the rule — two of which rest on a misreading the Article invites, and two of which are gaps in the Model Act.

Zhang & Zhao, Harv. J.L. & Tech. (submission draft)
4 objections · 2 real gaps · 2 draft provisions
01 · The common premise
Three of the four assume the rule asks for telemetry.
Read Table 3 as a specification and notice where each field would actually come from. Identity and scope: asset inventory and release management. Risk and release owners: the approval workflow. Evaluation and decision record: whatever already documents a go/no-go. Feedback and escalation: the incident queue. Intervention: the runbook and the access-control matrix. Provenance and retention: vendor contracts and the retention schedule.

Almost none of it is application logs. The Article says so once — release and asset-management systems supply version and supplier identity, transaction and incident systems supply event fields Part IV.B — and then never returns to it. That single sentence is doing the work of answering the entire feasibility objection, and it is buried.

The minimum record is a register of organizational decisions, not a capture of system behavior. An engineer who reads it as a logging mandate will estimate a cost that the rule does not impose, and will be right to refuse the thing he thinks he is being asked for.
That misreading is the Article's fault, not the reader's. The remedy is not argument; it is vocabulary. Sections 02 and 03 below separate the objections that dissolve on a correct reading from the two that survive it.

02 · The objections
What survives contact with the statutory text.
One · Reconstruction
A request crosses five hundred services. Nobody can answer in thirty days.
Objection
Pinpointing which model version, which A/B branch, which vector store and which safety filter handled one message, across dozens of teams' logging systems, is not a thirty-day task without distributed tracing that was in place beforehand. The rule ignores how messy real infrastructure is.

Answer
This is a description of the world without the rule, offered as a reason not to have the rule.

The thirty days do not run against a forensic investigation. They run against a record that § 2 already required to exist before the deployment went live. If the record exists, the first answer is a lookup by event identifier against a schema fixed at designation — the Article's own phrase is retrieving a defined record "rather than assembling an organizational history after the event" Part IV.A. If it does not exist, the problem is a § 2 violation, and no length of clock cures it. That is the entire thesis: discovery cannot recreate what was never recorded, which is why the duty is ex ante.

The scope is also smaller than the objection assumes. § 4 asks for the application and model versions active for the event, whether a named function ran, and who supplied, configured, held and could stop each material component. It does not ask for the call graph. A vector store enters the custodian map as a supplier and a custodian, not as a traced hop.

What the objection is right about
The mechanism it names is the correct one, and the Article never names it. § 2's three identifiers — deployment, component-version, event — are a correlation identifier propagated across the call path and bound to a fixed field set. Engineers have a name for that pattern and a standard for it. Saying so converts the objection from impossible to you already run this; the statute fixes which fields ride on it.

Two · Allocation
The employer misconfigured it, and the vendor pays for the discovery.
Objection
In Mobley, the employer set the screening threshold and supplied the historical data. Yet the employer answers with a short receipt while Workday produces model validation reports and customer-impact analyses. The rule punishes the technology supplier and indulges the business that misused it.

Answer
The premise is inverted. The rule allocates by function, not by role, and on these facts the employer is squarely a covered control holder.

§ 5 keeps an enterprise in Stage Two on a showing of risk specificity, practical authority and information materiality. An employer that set the threshold and uploaded the training data satisfies all three for its own configuration lane: the threshold is specifically connected to the asserted disparity, configuring is named practical authority, and both sit on the event path. The Article says this in terms — a downstream actor that removes safeguards or selects a new high-impact purpose "can occupy the relevant lane instead" Part II.C. Visibility buys the employer the first-answer duty. It does not buy it an exit from Stage Two.

Conversely, Table 1 gives the vendor the exit the objection assumes it lacks: records addressing a different feature or hazard, a feature inactive for the event, authority prohibited and unused, or requested information unrelated to the asserted path.

The part a supplier should actually want
Today a vendor sued over a customer's configuration must prove that configuration without access to it. Under the rule, the customer's own first answer must identify configuration authority and custodianship — produced by the customer, at the customer's cost, before any merits fight. The custodian map is the supplier's exculpatory exhibit. Part IV.F calls the record a defense asset; on a divided stack it is specifically the upstream party's defense asset, and the Article never says so.

Three · Purpose and retention
Logs exist to debug, not to litigate, and they roll over in weeks.
Objection
Logging captures token counts and latency, not whether a decision affected someone's rights, and it is overwritten a few releases later to control storage cost. Requiring a separate immutable human-readable control record means a second pipeline that does nothing for system performance. Engineers will hate the dual track and route around it.

Answer
The dual track being objected to is not the one being asked for.

The rule does not want the log. Every component of Table 3 is an organizational fact with an existing owner, as section 01 sets out, and the Article's own feasibility claim is that for a firm already doing version control, release management, access logging, vendor management, incident response and legal retention, the proposal connects those systems for designated deployments Part IV.D. The genuinely new artifact is one control sheet per designated deployment per version family. That is a form, not a stream.

Retention is answered by the three clocks Part IV.C, and the storage argument mostly dissolves once they are read as a cost design. The identity record is small and long-lived: versions, owners, components, intervention rights. The feedback record aggregates. The event record freezes a bounded slice only when a consequential action or identified incident occurs. Nothing here retains ordinary traffic, and Part IV.E affirmatively refuses a retain-everything mandate.

Where the objection lands
Immutability. The Article's position is the cheap and correct one — "integrity requires lineage rather than a self-authenticating compliance certificate," with hashes or append-only controls "where appropriate" and ordinary version control and attestation elsewhere, the goal being a contestable trail rather than proof that every control operated as designed. That is one clause carrying the requirement engineers price highest. Stated once and in passing, it reads as an unfunded mandate for WORM storage. Stated plainly, it is version control plus an approval signature.

Four · Certification
We passed SOC 2. Can that substitute for the record duty?
Objection
A firm with SOC 2 or ISO/IEC 27001 and a mature DevOps monitoring practice has already been audited against an authoritative control framework. Let technical compliance stand in for a bespoke legal standard and exempt part of the ex ante duty.

Answer
No as a substitute, yes as evidence of form and burden. The reason is structural, not territorial.

Those frameworks certify that the information system is protected — confidentiality, integrity, availability, access control. They do not ask which model version governed one person's decision or who could have stopped it, and no control in either produces an event receipt or a custodian map. A system can be flawlessly certified and completely opaque as to attribution. An AI management-system standard sits nearer but commits the same category error one step in: it certifies that processes exist, not that a particular deployment's record exists and resolves for a particular event.

The deeper reason is the one the Article already relies on elsewhere. A certificate is the most regulator-facing artifact there is; the first answer runs to a person about an event. And accepting certification as a substitute would convert the rule from a description into a measure — firms would optimize for the certificate, auditors would sell it, and the fields would drift to whatever the auditor checks. That is precisely the Goodhart exposure the design otherwise avoids by specifying facts rather than scores.

What certification should do
Carry weight on the architecture and on burden. Certified change management, access logging, asset inventory and retention are good evidence that § 2's creation, retrieval and preservation duties are satisfiable, and a designation can authorize a simplified record form on that basis — the Article already contemplates simplified forms Part II.A; Part IV.D. It should also support a § 6 objection asserting documented unavailability. What it must never do is excuse nonperformance: where a certified operator cannot produce a § 4 field, the certificate is evidence that the omission was systemic rather than incidental. The certificate cuts against the excuse, not for it.

03 · What the Model Act is missing
Two gaps, confirmed against the source.
There is no transition provision
"Transition" appears once in the manuscript, in an unrelated companion-service context. Nothing in §§ 1–11 addresses a deployment already running when its category is designated — which is every deployment, on day one of every designation. Without it, objection one is correct rather than misdirected: the operator is being asked for a record of decisions taken before any duty to record them existed. This is the single most exploitable omission in the Model Act, and it is also the cheapest to close.

Certification is addressed only by implication
The manuscript rejects certificate-as-substitute in one clause — integrity requires lineage "rather than a self-authenticating compliance certificate" — and never engages the question a compliance officer will actually ask. Leaving it implicit invites a designating legislature to write the substitution in, which would hollow out the whole scheme. Better to answer it in the Act.

And one vocabulary gap that is not a design gap
The words trace, correlation and telemetry appear nowhere in the manuscript. The identifier triple in Part IV.B is a correlation-identifier pattern with an existing standard, and every technical reader will recognize it the moment it is named. Not naming it is why a reader who builds these systems reads Part IV as a demand for something new.

04 · Draft provisions
Language for the two gaps.
Drafted to sit alongside §§ 1–11 without disturbing the merits firewall or the staged structure. Numbering assumes they follow the existing sections.

Section 12. Transition for existing deployments
For a covered deployment in operation on the designation's effective date, the visible operator shall, within the period the designation fixes, create the deployment record prospectively and record the identity and scope, risk and release owners, intervention authority, custodian and retrieval fields then ascertainable from records it holds.

The operator is not required to reconstruct evaluations, approvals, material changes, or event fields for any period preceding the effective date, and the absence of such fields for that period supports no inference under this Act or under governing law. The first-answer duty under Section 4 attaches to a covered adverse event occurring after the deployment record is due.

Section 13. Assessed control frameworks
A designation may recognize an information-security, quality-management, or AI-management certification, or an equivalent independently assessed control framework, as evidence that an operator's change-management, access-logging, asset-inventory and retention controls are adequate to the creation, retrieval and preservation architecture required by Section 2, and may on that basis authorize a simplified record form.

Such recognition bears on the form of compliance and on the sufficiency of an objection under Section 6 asserting documented unavailability. It does not substitute for the event receipt or custodian map required by Section 4, does not excuse nonperformance of the first-answer duty, and creates no presumption under Section 8. Where a recognized operator cannot supply a Section 4 field, the recognition is evidence that the omission was systemic rather than incidental.

05 · Where each answer goes
Five insertions.
Location	Insertion	Length
Part IV.B
At the three identifiers
Name the pattern. The deployment, component-version and event identifiers are a correlation identifier bound to a fixed legal field set, and propagated trace context is the existing engineering form of exactly this. One footnote to the relevant standard. Highest-value edit on this page: it retires the feasibility objection by recognition rather than by argument.

1 sent. + fn
Part IV opening
Before Table 3
State where each component comes from — asset inventory, approval workflow, incident queue, runbook, vendor contract — so the table reads as a register of organizational decisions rather than a logging mandate. The claim exists in Part IV.B and Part IV.D; it needs to arrive before the table, not after.

~90 w
Part IV.B
Integrity paragraph
Promote the lineage-not-tamper-proofing position from a clause to its own short passage, and say what it excludes: no WORM requirement, no cryptographic notarization, version control plus an approval signature is sufficient where the sector does not require more.

~80 w
Model Act, new §§ 12–13
After § 11
Transition and assessed control frameworks, as drafted in section 04. Add a sentence to Part II.A noting that a designation must fix the transition period.

~230 w
Part III.B
Mobley application
Say explicitly that the employer's configuration is itself a control lane, and that the custodian map is the upstream supplier's defense asset. Both follow from § 5 and Part IV.F but neither is stated where the divided-stack reader will look for it.

~110 w
Objection scope checked against article/*.tex as of this session. "Transition", "certification", "trace", "correlation" and "telemetry" were searched across all seven Parts; the counts behind the two gaps in section 03 are from that pass. Draft statutory language in section 04 is a starting point for the authors, not verified against any enacted analogue.