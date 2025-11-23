# examples/minimal_agent/ace_runner.py

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

    # pretend action
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

    # simple success inference
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
