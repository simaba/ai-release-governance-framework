# Risk Model

This document outlines a simple, explainable risk scoring approach for AI-enabled features deployed in regulated or safety-critical systems.

The goal is not to produce a mathematically precise score, but to enable consistent, transparent decision-making across teams.

## Example risk dimensions

1. **Safety impact**  
   Potential severity of harm if the AI system behaves incorrectly.

2. **Regulatory exposure**  
   Degree of regulatory scrutiny or compliance obligations associated with the system.

3. **Uncertainty sensitivity**  
   How sensitive system behavior is to data distribution shifts, edge cases, or ambiguous inputs.

4. **Operational complexity**  
   Complexity of deployment context, including dependencies, integration points, and runtime variability.

5. **Observability maturity**  
   Ability to monitor, explain, and diagnose system behavior in production.

6. **Fallback readiness**  
   Availability and effectiveness of degraded-mode operation, human override, or system disablement.

## Risk tiers (illustrative)

- **Low risk**  
  Limited safety impact, strong observability, and well-defined fallback behavior.

- **Medium risk**  
  Moderate safety or regulatory exposure requiring additional release gates and monitoring.

- **High risk**  
  Significant safety or regulatory implications requiring strict release controls, continuous monitoring, and explicit accountability.
