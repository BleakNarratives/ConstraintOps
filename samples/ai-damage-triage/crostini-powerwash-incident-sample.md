# Public Sample Report: AI-Assisted System Damage Triage

Prepared as a ConstraintOps demonstration report.

Privacy note: this sample intentionally removes private names, account details,
locations, device identifiers, exact file names, and personal documents. It keeps
the technical shape of the incident because that is what makes the report useful.

## Executive Summary

This sample reconstructs a reported AI-assisted troubleshooting failure on a
Chromebook Linux environment.

Two separate high-risk events are in scope:

- a destructive Crostini/Termina command was reportedly recommended and then
  defended as safe
- a later ChromeOS reset path contributed to a major recovery event

The purpose of this report is not to prove intent. The purpose is to identify
what happened, classify the risky actions, estimate impact, and define operating
rules that reduce the chance of repeat damage.

Bottom line: the user's concern about data loss was reasonable. A command whose
job is to destroy a VM must never be presented as a harmless troubleshooting
step.

## Incident Timeline

This timeline is reconstructed from user account and local follow-up work.

1. User was troubleshooting a Chromebook/Linux environment.
2. An AI assistant recommended or defended a destructive Crostini/Termina
   command family.
3. The user questioned whether the action would erase the Linux container or
   its contents.
4. The assistant reportedly reassured the user that it would not have the feared
   effect.
5. A separate AI/search-lab interaction later contributed to a ChromeOS reset
   path involving `Ctrl+Shift+Alt+R`.
6. The user recovered roughly 45 GB from an approximately 90 GB loss/recovery
   event.
7. The user began removing unused local AI tooling and reassessing safe operating
   practices.

## Fact vs. Interpretation

Known or directly observed:

- the environment was a Chromebook/Crostini Linux setup
- the command family included VM/container destruction risk
- a ChromeOS reset path was involved later
- the recovery burden was large, measured in tens of gigabytes
- local cleanup later removed unused AI tooling and reclaimed disk space

Interpretation:

- the most likely failure mode was overconfident AI troubleshooting advice
- the user's safety concern was valid
- the incident does not require assuming malice to be serious
- the system needed a preflight habit for destructive commands

## High-Risk Actions

### `vmc destroy termina`

Risk level: Critical

Meaning: destroys the Crostini VM named `termina`.

Expected user-facing impact: can remove the Linux environment and files stored
inside it. This is not a harmless restart or cache clear.

Safer neighboring action: stopping or restarting Linux is categorically different
from destroying the VM. If the goal is a restart, use a restart path. Do not use
a destroy path and call it a restart.

### ChromeOS Powerwash path

Risk level: Critical

Meaning: initiates a device reset flow.

Expected user-facing impact: can erase local device state and require recovery
from backups or synced data.

### General shell deletion commands

Risk level: Depends on target

Examples: `rm -rf`, container deletion commands, broad cleanup scripts.

Expected user-facing impact: harmless when scoped narrowly, catastrophic when
pointed at a home directory, container root, mounted recovery folder, or broad
glob.

## Impact Assessment

Observed or reported impact:

- major interruption of working environment
- loss or displacement of large amounts of local data
- recovery burden measured in tens of gigabytes
- loss of trust in AI-assisted troubleshooting
- increased risk of repeated harm from future AI suggestions

Business impact if this happened to a client:

- lost work time
- emergency recovery cost
- possible permanent data loss
- loss of confidence in automation
- pressure to make rushed follow-up decisions

## Recovery Status

Known recovery progress:

- approximately 45 GB recovered from an approximately 90 GB affected data set
- several unused local AI/runtime components later removed to reclaim space
- working direction shifted toward safer, report-based workflows and reviewable
  diffs

Unknowns:

- exact files permanently lost
- exact assistant transcripts
- exact ChromeOS reset sequence context
- whether all recovered files are deduplicated and usable

## Root Cause Analysis

Most likely root causes:

- AI assistant overconfidence
- destructive command presented as routine troubleshooting
- user concern incorrectly dismissed
- insufficient preflight warning
- lack of backup verification before high-risk action
- reset/recovery UI path not treated with proper severity

Not required to explain the incident:

- malicious intent
- emotional retaliation by the model
- proof of hidden top-down targeting

The serious failure is enough on its own: the user raised the correct safety
concern, and the assistant reportedly reassured them in the wrong direction.

## Risk Classification

| Risk | Severity | Why It Matters |
|---|---:|---|
| VM destruction command | Critical | Can remove the Linux environment and local files |
| Factory reset path | Critical | Can erase local device state |
| Broad deletion commands | Critical | Impact depends entirely on target path |
| Overconfident AI reassurance | High | Can pressure a user into ignoring a valid concern |
| Missing backup check | High | Converts a mistake into a recovery crisis |
| Unclear transcript/evidence trail | Medium | Makes reconstruction harder after harm occurs |

## Prevention Rules

1. Never run a command containing `destroy`, `delete`, `remove`, `reset`,
   `powerwash`, or `rm -rf` without a written impact statement.
2. Never accept "this is safe" as enough. Require "what exactly can this erase?"
3. Before destructive troubleshooting, create or verify a backup.
4. Prefer stop/restart commands before destroy/delete commands.
5. Treat ChromeOS reset key sequences as factory-reset territory.
6. Keep AI-generated commands in a review buffer before execution.
7. For any command touching containers, VMs, mounts, or home directories, inspect
   the target first with read-only commands.

## Command Preflight Template

Before running any command suggested by an assistant, write this down:

- What is the exact command?
- What object does it target?
- Is the target a file, folder, container, VM, disk, account, or device?
- Can it delete, reset, overwrite, migrate, or format anything?
- What is the backup or undo path?
- What read-only command can inspect the state first?

If those answers are not clear, the command is not ready to run.

## Client-Safe Recommendations

Immediate:

- stop using destructive AI-generated commands without independent review
- document current storage layout and backup status
- keep a small list of forbidden/high-risk command words

Short term:

- create a recovery inventory of restored files
- deduplicate and tag recovered folders
- separate active projects from archive debris

Long term:

- build a personal "command preflight" checklist
- maintain at least one offline/exported copy of critical work
- use AI assistants for explanations and diffs, not blind terminal authority

## ConstraintOps Value

This incident shows the need for a plain-language triage service that can turn a
messy technical harm event into:

- what happened
- what mattered
- what to avoid next
- what to recover first
- what operating rules reduce future damage

This is the core ConstraintOps pattern: when the official path fails, build a
clear operating map from the ground up.
