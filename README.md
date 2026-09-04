# Carbon Ledger
## Scope of the experiment
Carbon Ledger compares a registry record, a methodology/additionality document and a beneficiary claim. Its purpose is to record a source-bound integrity judgment about a stated quantity of credits.

**RETIRED is a state in this contract only.** The implementation does not retire credits in an external registry, transfer ownership or prevent the same underlying asset from being presented to another contract.

### Inputs and observations
Registration fixes a project, vintage, positive tonne quantity and three distinct HTTPS URLs. Vintage must be at least 2000. The caller owns the record.

The leader retrieves bounded document bodies and proposes VALID, DUPLICATE, MISMATCH or INSUFFICIENT. A reported external retirement forces DUPLICATE; a VALID proposal with the wrong quantity becomes MISMATCH.

Validators independently retrieve the documents, compare digests and assess the proposed status, quantity and issue indexes. Up to 15,000 body units per source are processed.

### Experimental procedure
1. `register(i, project, vintage, tonnes, registry_url, method_url, claim_url)`
2. Owner calls `verify_and_retire(i)`.
3. Read `get_certificate(i)`.

VALID ends as RETIRED; other verdicts end as REJECTED. Both states prevent replay of that record. Duplicate protection is scoped to the caller-supplied normalized ID inside this contract.

### What the example establishes
The Forest Delta fixture describes 50 tonnes, vintage 2025, using synthetic repository documents. The recorded run stored VALID and then RETIRED. It demonstrates the contract-local transition and source digests, not an actual environmental offset.

### Identity and trust limitations
The submitted record ID is not included in the adjudication prompt as a required registry serial. Another local ID can therefore refer to the same underlying certificate. Do not interpret ID deduplication as global double-retirement prevention.

The validator prompt also does not explicitly repeat project and vintage as independent comparison targets. There is no registry signature verification, issuer allowlist, ownership proof or external retirement API. Rationale is not independently validated. Unavailable pages or malformed model output may fail execution.

### Review materials

#### Reproduction boundaries

There are two different artifacts to inspect: [the synthetic documentary inputs](specimens/) and [the contract-local retirement result](records/retirement.json). Neither is a registry-issued retirement certificate.

A local reproduction requires `python -m pip install -r requirements.txt`, then `python -m pytest tests/direct -q`. Run `genvm-lint ledger.py` separately. Mocked assertions check contract behavior, not authenticity of environmental claims.

The executable [network experiment](research/smoke.py) registers a fresh local ID and requests owner-authorized verification. It expects account 3 in an untracked `accounts.env` four directories above the repository. Reconfigure credential lookup before running outside that workspace; the script sends transactions and overwrites its local result file.

[Deployment provenance](records/deployment.json) identifies the code revision. When reviewing the smoke output, distinguish the fixture's registry serial from the local record ID; this implementation does not prove that mapping.

[Implementation](ledger.py) · [Executable direct tests](tests/direct/test_contract.py) · [Recorded transition](records/retirement.json)

This is an experimental advisory ledger. It is not a carbon registry or a verified credit issuance system.

Deployment and network-run files are generated after execution; use the paths referenced above to inspect the current evidence.
