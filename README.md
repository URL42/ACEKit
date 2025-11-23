# ACEKit

**ACEKit** is a small, ACE-style “self-learning” agentic framework you can plug into any agent-driven project:

* browser agents (Playwright, Selenium, HTTP fetchers)
* email drafting agents
* financial analyst / report agents
* CLI / batch tools, etc.

**See the original Agentic Context Engineering paper here: https://arxiv.org/html/2510.04618v1


* Browser agents (Playwright, Selenium, HTTP fetchers)
* Email drafting agents
* Financial analyst / report agents
* Automation/n8n agents
* Any agent that uses tools or performs multi-step reasoning

---

# What ACEKit Does

ACEKit provides three core capabilities:

1. **Run Logging** — records structured actions, errors, outcomes.
2. **Dynamic Playbook** — builds and maintains a set of short, reusable guidance tips.
3. **LLM Reflection (optional)** — generates improvement suggestions from past runs.

You integrate ACEKit into a project through:

* `prompt_overlay()` at the start of each run.
* `record_run()` at the end of each run.

Everything else is normal agent logic.

---

# Installation

```bash
git clone https://github.com/yourname/ACEKit.git
cd ACEKit
pip install -e .
```

Optional for reflection:

```bash
pip install "acekit[openai]"
export OPENAI_API_KEY="sk-..."
```

---

# Concepts

## ActionRecord

Represents a single tool call.

## RunEntry

Represents an entire run from start to finish.

## Tip

Short guidance bullets ACEKit injects into future prompts.

All details of these structures are in `acekit/models.py`.

---

# Basic Usage Pattern

## 1. Instantiate ACEManager

```python
from acekit import ACEManager

ACE_DOMAIN = "browser_agent"

ace = ACEManager(
    playbook_path="./ace_playbook.json",
    guardrails_path="./guardrails_default.json",
    domain=ACE_DOMAIN,
)
```

---

## 2. Start of Run: Get Tips

```python
overlay_text, used_tip_ids = ace.prompt_overlay(task, domain=ACE_DOMAIN)

messages = []
if overlay_text:
    messages.append({"role": "system", "content": overlay_text})
```

Add any system / developer / user messages as usual.

---

## 3. Log Actions

Wrap each tool call with start/end timing and produce an ActionRecord.

---

## 4. Infer Outcome Quality

Define a small function in each project: success, partial, failed, blocked, etc.

---

## 5. Finish Run: Record

```python
ace.record_run(
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

# Examples

ACEKit now provides two minimal examples inside `examples/`.

---

# Example 1 — Minimal Agent

This is the simplest runnable ACEKit demonstration.

Path: `examples/minimal_agent/ace_runner.py`

```python
from acekit import ACEManager, ActionRecord
from time import monotonic

ACE_DOMAIN = "demo"

ace = ACEManager(
    playbook_path="playbook_demo.json",
    guardrails_path="acekit/guardrails_default.json",
    domain=ACE_DOMAIN,
)

def demo_run(task: str):
    overlay, used_ids = ace.prompt_overlay(task)

    actions = []
    errors = []

    # fake action
    start = monotonic()
    actions.append(ActionRecord(
        tool="echo",
        args={"task": task},
        result_type="ok",
        error_category="none",
        message=f"Echoed task: {task}",
        latency_ms=int((monotonic() - start)*1000)
    ).model_dump())

    final_output = f"Completed: {task}"

    # simple inference
    goal_status = "success"
    reason = "ok"
    relevance = 0.9

    ace.record_run(
        task=task,
        outcome=final_output,
        actions=actions,
        errors=errors,
        preferences=[],
        goal_status=goal_status,
        reason_for_status=reason,
        answer_relevance_score=relevance,
        used_tip_ids=used_ids,
        domain=ACE_DOMAIN,
    )

if __name__ == "__main__":
    demo_run("demo task")
```

### Example 1 Playbook Template

Path: `examples/minimal_agent/playbook_template.json`

```json
{
  "entries": [],
  "active_tips": [],
  "preferences": []
}
```

---

# Example 2 — Skeleton Browser Agent (Optional)

You can add a browser agent skeleton by copying your own project structure, then stripping any private logic.

---

# Multiple Domains

ACEKit supports one shared playbook across many domains or separate playbooks per domain.

---

# Guardrails & Privacy

ACEKit sanitizes text fields for secrets and limits the length of logged text. Projects should still avoid putting any real secrets into `args` or `message` fields.

---

# Reflection

If an OpenAI API key is available, ACEKit will automatically request "tips for improvement" from the Reflector LLM and merge them into the playbook.

---

# License

MIT (or select your own)

---


All coding agents should follow this guide exactly when integrating ACEKit into new projects.

