# Proposal: 0007 - Secrets broker

Overview
--------

Prevent direct injection of long-lived secrets into execution runtimes by introducing a secrets broker that performs privileged operations on behalf of workers.

Deliverables
------------

1. `spec.md` defining broker API and threat model.
2. `tasks.md` for implementing and testing a proof-of-concept broker.
