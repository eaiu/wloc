"""Generate a personal shortcut while preserving Apple variable references."""

import json
import plistlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
config = json.loads((ROOT / "project.config.json").read_text())
origin = config["siteUrl"].rstrip("/")
repository = config["repository"]
branch = config["branch"]
workflow = plistlib.loads((ROOT / "shortcuts/templates/set-location.plist").read_bytes())
old_origin = "https://wloc.xepesw.workers.dev"
replaced = 0

for action in workflow["WFWorkflowActions"]:
    parameters = action["WFWorkflowActionParameters"]
    if action["WFWorkflowActionIdentifier"] == "is.workflow.actions.comment":
        text = parameters.get("WFCommentActionText", "")
        parameters["WFCommentActionText"] = text.replace(
            "raw.githubusercontent.com/Yu9191/wloc/refs/heads/main",
            f"raw.githubusercontent.com/{repository}/refs/heads/{branch}",
        )
    url = parameters.get("WFURL", {})
    if not isinstance(url, dict):
        continue
    token = url.get("Value", {})
    text = token.get("string", "")
    if not text.startswith(old_origin + "/api/parse?"):
        continue
    token["string"] = origin + text[len(old_origin):]
    # Apple stores token offsets in UTF-16 code units, not Python characters.
    delta = (len(origin.encode("utf-16-le")) - len(old_origin.encode("utf-16-le"))) // 2
    ranges = {}
    for key, attachment in token["attachmentsByRange"].items():
        match = re.fullmatch(r"\{(\d+), (\d+)\}", key)
        if not match:
            raise ValueError(f"Unexpected attachment range: {key}")
        start, length = map(int, match.groups())
        ranges[f"{{{start + delta}, {length}}}"] = attachment
    token["attachmentsByRange"] = ranges
    replaced += 1

if replaced != 1:
    raise ValueError(f"Expected one parse action, got {replaced}")
for action in workflow["WFWorkflowActions"]:
    token = action["WFWorkflowActionParameters"].get("WFURL", {})
    if not isinstance(token, dict) or not isinstance(token.get("Value"), dict):
        continue
    value = token["Value"]
    encoded = value.get("string", "").encode("utf-16-le")
    for key in value.get("attachmentsByRange", {}):
        start, length = map(int, re.findall(r"\d+", key))
        if encoded[start * 2:(start + length) * 2].decode("utf-16-le") != "\ufffc":
            raise ValueError(f"Invalid shortcut variable offset: {key}")

output = ROOT / "build/shortcuts/WLOC-set-location-Cairlen.unsigned.shortcut"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(plistlib.dumps(workflow, fmt=plistlib.FMT_XML))
print(f"Generated {output.relative_to(ROOT)}; parse URL: {origin}/api/parse")

restore = plistlib.loads((ROOT / "shortcuts/templates/restore-location.plist").read_bytes())
for action in restore["WFWorkflowActions"]:
    parameters = action["WFWorkflowActionParameters"]
    if "WFCommentActionText" in parameters:
        parameters["WFCommentActionText"] = parameters["WFCommentActionText"].replace(
            "raw.githubusercontent.com/Yu9191/wloc/refs/heads/main",
            f"raw.githubusercontent.com/{repository}/refs/heads/{branch}",
        )
restore_output = output.with_name("WLOC-restore-location-Cairlen.unsigned.shortcut")
restore_output.write_bytes(plistlib.dumps(restore, fmt=plistlib.FMT_XML))
print(f"Generated {restore_output.relative_to(ROOT)}")
