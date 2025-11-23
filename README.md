# README.md

# ACEKit

**ACEKit** is a small, generic, ACE-style “self-learning” framework you can plug into any agent-style project:

* browser agents (Playwright, Selenium, HTTP fetchers)
* email drafting agents
* financial analyst / report agents
* CLI / batch tools, etc.

ACEKit does three things:

1. **Logs structured telemetry** about each run (task, actions, errors, outcome).
2. **Maintains a playbook of tips** that can be injected into prompts for future runs.
3. **Optionally uses an LLM Reflector** to turn past runs into new, concise strategy tips.

You don’t rewrite your agent for this.
You just:

* call `prompt_overlay()` at the start of a run to get tips + preferences, and
* call `record_run()` at the end with structured actions and an overall outcome label.

Everything else remains your normal agent logic.

---

## Installation

Clone the repo and install in editable mode:

```bash
git clone https://github.com/yourname/acekit.git
cd acekit
pip install -e .
```

Optional: install OpenAI extras for the Reflector:

```bash
pip install "acekit[openai]"
```

Set `OPENAI_API_KEY` if you want the Reflector:

```bash
export OPENAI_API_KEY="sk-..."
```

---

## Concepts

### ActionRecord

One **step** or **tool call**:

```python
from acekit import ActionRecord

action = ActionRecord(
    tool="navigate",                  # or "query_db", "draft_email", etc.
    args={"url": "https://example.com"},
    result_type="ok",                 # "ok" | "soft_fail" | "hard_fail"
    error_category="none",            # "timeout" | "api_error" ...
    message="Navigated to example.com",
    latency_ms=342,
    url="https://example.com",
    retries=0,
)
```

---

### RunEntry

One **agent run**: captures the task, outcome, all actions, errors, preferences, final goal status, and more. Automatically created via `record_run()`.

---

### Tip

A **small, reusable bullet** ACE injects into future prompts.

These are generated automatically from:

* heuristic curation in `record_run()`
* (optional) LLM reflection

---

## Basic Usage

### 1. Instantiate

```python
from acekit import ACEManager

ACE_DOMAIN = "browser_agent"

ace_manager = ACEManager(
    playbook_path="./ace_playbook.json",
    guardrails_path="./guardrails_default.json",
    domain=ACE_DOMAIN,
)
```

---

### 2. Get overlay tips at the start

```python
overlay_text, used_tip_ids = ace_manager.prompt_overlay(task, domain=ACE_DOMAIN)

messages = []
if overlay_text:
    messages.append({"role": "system", "content": overlay_text})

messages.append({"role": "system", "content": "You are a helpful agent..."})
messages.append({"role": "user", "content": task})
```

---

### 3. Log actions

```python
from time import monotonic

action_records = []
errors_for_ace = []

start = monotonic()
try:
    result = tool_call()
    log_action(...)
except Exception as e:
    log_action(...)
```

---

### 4. Infer outcome

```python
def infer_goal(outcome, actions, errors):
    if outcome and not errors: return "success", "ok", 0.9
    if outcome and errors: return "partial", "had_errors", 0.6
    if errors: return "failed", "errors", 0.2
    return "failed", "empty_outcome", 0.1
```

---

### 5. Record the run

```python
goal_status, reason, relevance = infer_goal(
    final_output or "",
    action_records,
    errors_for_ace,
)

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
