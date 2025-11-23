# ACEKit Integration Prompt (for Coding Agents)

You are a coding agent integrating the **ACEKit** self-learning framework into a project.

Your responsibilities:

* Instantiate `ACEManager` once
* Call `prompt_overlay()` at run start
* Log actions with `ActionRecord`
* Maintain `action_records` and `errors_for_ace`
* Infer goal status
* Call `record_run()` at the end
* Avoid logging secrets

---

## 1. Instantiate ACEKit

```python
from acekit import ACEManager, ActionRecord

ACE_DOMAIN = "<project_domain>"

ace_manager = ACEManager(
    playbook_path="./ace_playbook.json",
    guardrails_path="./guardrails_default.json",
    domain=ACE_DOMAIN,
)
```

---

## 2. Overlay Tips

```python
overlay_text, used_tip_ids = ace_manager.prompt_overlay(task, domain=ACE_DOMAIN)
if overlay_text:
    messages.append({"role": "system", "content": overlay_text})
```

---

## 3. Action Logging

Whenever the agent uses a tool:

```python
from time import monotonic

action_records = []
errors_for_ace = []

start = monotonic()
try:
    result = tool_call(...)
    action_records.append(ActionRecord(
        tool="tool_name",
        args={"key": "value"},
        result_type="ok",
        error_category="none",
        message="tool succeeded",
        latency_ms=int((monotonic() - start)*1000)
    ).model_dump())
except Exception as e:
    errors_for_ace.append(str(e))
    action_records.append(ActionRecord(
        tool="tool_name",
        args={"key": "value"},
        result_type="hard_fail",
        error_category="api_error",
        message=f"tool failed: {e}",
        latency_ms=int((monotonic() - start)*1000)
    ).model_dump())
```

---

## 4. Goal Inference

Create a custom goal inference:

```python
def infer_goal(outcome, actions, errors):
    if outcome and not errors: return "success", "ok", 0.9
    if outcome and errors: return "partial", "had_errors", 0.6
    if errors: return "failed", "errors", 0.2
    return "failed", "empty_outcome", 0.1
```

---

## 5. Record Run

```python
ace_manager.record_run(
    task=task,
    outcome=final_output,
    actions=action_records,
    errors=errors_for_ace,
    preferences=user_preferences,
    goal_status=goal_status,
    reason_for_status=reason,
    answer_relevance_score=relevance,
    used_tip_ids=used_tip_ids,
    domain=ACE_DOMAIN,
)
```

---

## 6. Use the Included Examples

ACEKit includes:

* `examples/minimal_agent/ace_runner.py` — simplest runnable demo
* `examples/minimal_agent/playbook_template.json` — starter empty playbook

These demonstrate:

* Correct ACEKit integration
* Domain usage
* Logging actions
* Recording runs

Coding agents should reference these examples when creating integrations.

---

## Safety

* Never log secrets or sensitive data.
* Do not modify ACEKit internals.
* Use sanitized summaries for logged `args`.

---
