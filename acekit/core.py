# acekit/core.py

# Error tips
for err in entry.errors[:3]:
err_tip = self._make_tip(
domain=domain,
task=entry.task,
signature=signature,
content=f"Avoid repeating this failure for similar tasks: {err[:120]}",
category="error",
confidence=0.5,
)
curated_tips.append(err_tip)

# Action pattern tip (coarse)
if entry.actions:
steps = []
for a in entry.actions[:4]:
tool = a.get("tool", "?")
res = a.get("result_type", "?")
err_cat = a.get("error_category", "none")
steps.append(f"{tool} -> {res} ({err_cat})")
steps_str = "; ".join(steps)
act_tip = self._make_tip(
domain=domain,
task=entry.task,
signature=signature,
content=f"Recent action pattern: {steps_str}",
category="pattern",
confidence=0.4,
)
curated_tips.append(act_tip)

# Reflective tips from LLM (optional)
reflective_tips = self._reflect_on_entry(entry)
all_new_tips = curated_tips + reflective_tips

# Update active tips with new tips
self._update_active_tips(all_new_tips)

# Update preferences
if entry.preferences:
prefs = self.playbook.get("preferences", []) or []
for p in entry.preferences:
if p not in prefs:
prefs.append(p)
# keep it small
self.playbook["preferences"] = prefs[-12:]

# Update helpful / harmful counts based on used_tip_ids
self._update_tip_feedback(used_tip_ids or [], goal_status)

# Persist
self._save_playbook()

def _update_tip_feedback(self, used_tip_ids: List[str], goal_status: str) -> None:
if not used_tip_ids:
return
tips = self.playbook.get("active_tips", [])
for tip in tips:
if tip.get("id") not in used_tip_ids:
continue
if goal_status == "success":
tip["helpful_count"] = int(tip.get("helpful_count", 0)) + 1
tip["confidence"] = min(1.0, float(tip.get("confidence", 0.5)) + 0.05)
elif goal_status in {"failed", "blocked"}:
tip["harmful_count"] = int(tip.get("harmful_count", 0)) + 1
tip["confidence"] = max(0.1, float(tip.get("confidence", 0.5)) - 0.05)
