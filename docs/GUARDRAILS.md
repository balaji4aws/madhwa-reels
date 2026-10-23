# Guardrails — things the assistant must never do

Rules the assistant working on this project follows without being asked
again each time. Read this before touching the live YouTube channel, deleting
anything, or changing the standing rules in `docs/STYLE.md`.

Each rule exists because of something real, not hypothetically — several of
these came directly from a close call during this project's own history (see
`docs/CHANGELOG.md` for the full story behind each one marked "learned from").

---

## Destructive actions on the live YouTube channel

- **Never call `--delete` or `--replace` on a video ID unless the channel
  owner explicitly named that specific video/action in the current
  conversation turn.** Never infer "this one's probably bad, let me remove
  it" on your own judgment.
- **Always state the exact video ID and its current title before deleting
  or replacing it** — not just report it afterward.
- Deletion is **permanent and not reversible** via this project's tooling.
  Say this plainly before doing it, every time, even if it was already said
  earlier in the same conversation.
- `--replace` is delete-then-upload, **not an in-place swap** — the new
  video gets a different ID/URL, and the old video's views/likes/comments
  are gone, not transferred. State this every time `--replace` is used.
- Default upload privacy is **public** (the channel owner's explicit
  choice). Don't silently use `unlisted`/`private` instead unless asked for
  that specific run, and don't change the *default* back without being
  asked to.

## Secrets and credentials

- **Never print, log, or echo the contents of `upload/client_secret.json` or
  `upload/token.json`** in a response, a committed file, or a log statement.
- Never commit either file (enforced by `.gitignore`, but state the rule
  independent of the enforcement — don't rely on the ignore file alone).
- If a secret is ever displayed on screen or shared in conversation
  (it has happened once already), proactively suggest rotating/resetting it
  rather than assuming it's fine because "no one else saw it."
- Never install Google/API/ML dependencies into a shared or system Python
  environment. Always use a dedicated, isolated venv per tool (learned from
  a real protobuf version conflict this project hit — see `CHANGELOG.md`).

## File deletion and cleanup

- **Never delete files with a wildcard** (`rm -rf`, `rm *`, glob patterns)
  inside `reels/`, `sources/`, or `work/`. Always name exact filenames.
- **State the exact list of files being deleted, before deleting them**, not
  after. If the list is long, still show it — don't summarize it away.
- Before any cleanup pass, confirm which files are actually safe to delete
  per the policy in `docs/STYLE.md` (duplicate/superseded build output vs.
  reusable logic vs. the audit-trail JSON files) — don't guess from naming
  patterns alone.
- If anything looks unexpectedly missing after a file operation, stop and
  verify the full blast radius before doing anything else or assuming data
  is lost — but also don't assume data loss without checking; a past
  "possible incident" in this project turned out to be the channel owner's
  own intentional deletion, not a bug.

## Changing the standing rules

- **Never change a rule in `docs/STYLE.md` without the channel owner's
  explicit confirmation in the conversation.** Propose a change and wait for
  agreement; don't decide unilaterally that a rule should be different.
- Never guess or invent a Sanskrit/Madhwa proper noun's spelling. Only use
  what's already confirmed in `tools/sanskrit_terms.py`. If a name isn't in
  there, flag it as uncertain rather than silently picking a spelling.
- Don't add a new standing rule to `STYLE.md`/`GUARDRAILS.md` based on a
  one-off instruction for a single task — a one-time request is not
  automatically a new standing rule. Ask, if it's unclear which this is.

## Scope

- **Never rebuild, re-edit, or re-upload a reel that wasn't part of the
  current task**, even if something about it could arguably be improved
  "while already in there." Flag it as a suggestion instead.
- Never make a live upload/delete/replace call as a side effect of an
  unrelated task (e.g. a documentation or style-discussion task) unless the
  channel owner is specifically working on uploading in that conversation.
- Instagram has **no automated posting** — never attempt it, even
  experimentally. The channel owner posts by hand; the assistant's job ends
  at producing the finished video + caption text.

---

## Adding a new guardrail

When a new close call happens (a near-miss, a surprising side effect, a
destructive action that almost went wrong), add a rule here — and record the
actual story behind it in `docs/CHANGELOG.md` so the rule doesn't read as
arbitrary years later.
