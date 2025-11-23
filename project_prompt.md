# project_prompt.md

# ACEKit Integration Prompt (for Coding Agents)

You are a coding agent integrating the **ACEKit** self-learning framework into a project.

## Your Responsibilities

1. Instantiate `ACEManager` once for the project.
2. Call `prompt_overlay()` at the start of each run.
3. Log each tool call using `ActionRecord`.
4. Maintain `action_records` and `errors_for_ace` lists.
5. Define a project-specific `infer_goal()` function.
6. Call `record_run()` at the end.
7. Never log secrets or sensitive information.

---

## 1. Instantiate ACEManager

Insert near the entrypoint of the agent:

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

## 2. Add overlay tips to prompts

Before building your main LLM prompt:

```python
overlay_text, used_tip_ids = ace_manager.prompt_overlay(task, domain=ACE_DOMAIN)

if overlay_text:
    messages.append({"role": "system", "content": overlay_text})
```

---

## 3. Log tool actions

Whenever a tool is used:

```python
from time import monotonic

action_records = []
errors_for_ace = []

start = monotonic()
try:
    result = tool_call(...)
    action_records.append(ActionRecord(
        tool="tool_name",
        args={...},
        result_type="ok",
        error_category="none",
        message="tool_name succeeded",
        latency_ms=int((monotonic() - start)*1000),
    ).model_dump())
except Exception as e:
    errors_for_ace.append(str(e))
    action_records.append(ActionRecord(
        tool="tool_name",
        args={...},
        result_type="hard_fail",
        error_category="api_error",
        message=f"tool failed: {e}",
        latency_ms=int((monotonic() - start)*1000),
    ).model_dump())
```

---

## 4. Infer goal quality

Add a custom goal inference for the project:

```python
def infer_goal(outcome, actions, errors):
    if outcome and not errors: return "success", "ok", 0.9
    if outcome and errors: return "partial", "had_errors", 0.6
    if errors: return "failed", "errors", 0.2
    return "failed", "empty_outcome", 0.1
```

---

## 5. Record run

At the end:

```python
ace_manager.record_run(
    task=task,
    outcome=final_output or "",
    actions=action_records,
    errors=errors_for_ace,
    preferences=user_preferences or [],
    goal_status=goal_status,
    reason_for_status=reason,
    answer_relevance_score=relevance,
    used_tip_ids=used_tip_ids,
    domain=ACE_DOMAIN,
)
```

---

## 6. Safety Rules

* Do not store raw secrets in any `ActionRecord` field.
* Use sanitized summaries in `args`.
* Do not modify the ACEKit library internals.

---

This is the complete guide for coding agents to integrate ACEKit into any project.
