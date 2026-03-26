# ADR 007: Shell-Bridge Execution

## Status

Accepted

## Context

The Sentinel Orchestrator needs to interact with the agentic worker environment. There are two approaches:
1. Use the Python Docker SDK directly
2. Invoke the existing `devcontainer-opencode.sh` shell script

## Decision

We will interact with the worker environment **exclusively** via the `devcontainer-opencode.sh` shell script.

## Rationale

The existing shell infrastructure handles complex Docker logic including:
- Volume mounting
- SSH-agent forwarding
- Host-to-container port mapping
- Network configuration

Re-implementing this in Python would create a maintenance nightmare and introduce "Configuration Drift" — where the agent runs in a different environment than a local developer.

## Consequences

### Positive
- Perfect environment parity between AI and human developers
- Python code remains lightweight and focused on logic/state
- Clear separation of concerns between "Logic Layer" and "Infra Layer"
- Leverages existing, tested infrastructure

### Negative
- Dependency on external shell script
- Less programmatic control from Python

## References

- Architecture Guide §3 ADR 07
- Implementation Specification §Features
