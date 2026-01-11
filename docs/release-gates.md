# Release Gates for AI Systems

AI-enabled features require release gates that go beyond traditional software readiness checks.

This document outlines example gates that can be adapted based on system risk and regulatory context.

## Example AI release gates

### 1. Domain and data coverage
- Intended operating conditions are explicitly defined
- Known limitations and out-of-scope scenarios are documented

### 2. Uncertainty handling
- Confidence thresholds or uncertainty indicators are defined
- Behavior under ambiguous or low-confidence inputs is specified

### 3. Fallback and degraded-mode behavior
- Safe fallback behavior is implemented and tested
- Conditions for degraded operation are clearly defined

### 4. Monitoring and observability
- Key signals are monitored in production
- Alerting thresholds are defined for abnormal behavior

### 5. Human escalation and override
- Clear criteria exist for when human intervention is required
- Humans have sufficient context and authority to act

### 6. Incident response and recovery
- Incident response playbooks are prepared
- Rollback or disablement mechanisms are validated

## Applying gates by risk tier

Release gates should be applied proportionally to system risk.

Higher-risk systems require:
- Stricter gate enforcement
- More frequent review
- Stronger accountability and oversight
