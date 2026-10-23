# argos-revision-paralela

Claude skill that runs the Argos review of a public procurement file (70-point Operational Matrix) by splitting the work across subagents: unique neutral facts, parallel grading by groups of points, centralized consolidation, and independent verification of serious findings. The skill holds no review rules; it only organizes the work. `argos-revision-paralela/scripts/` holds the generic scripts the skill downloads from this repository on every run.

## Language

<!-- Owned by this repository. Delete the exceptions that do not apply. -->

Everything is in English, except these, which are in Spanish:

- Conversation with the developer.
- Documentation: `README.md`, `GLOSSARY.md`, and everything under `docs/`, ADR file names included.
- Git and GitHub text: commit subjects, pull request titles and bodies, issue titles, bodies, and comments, label descriptions.
- Code comments.
- Anything the client sees: the skill's `SKILL.md` body, deliverables, and their file names.

These stay in English even inside the exceptions: code, identifiers, and file names not covered above; names a tool imposes (`SKILL.md`, `CHANGELOG.md`, `LICENSE.txt`, label names, `Closes #n`, text a skill looks for); and files a tool generates from its own template (`/setup-matt-pocock-skills`, `/setup-dev-workflow`), including the base section of `docs/development/git-workflow.md` and the pull request template.

Use a regular hyphen `-` in every text. Never an em dash or an en dash.

## Commands

<!-- Owned by this repository -->

```bash
# Lo que corre el job checks del CI
find . -name '*.py' -not -path './.git/*' -print0 | xargs -0 python -m py_compile
find . -name '*.sh' -not -path './.git/*' -print0 | xargs -0 -n1 bash -n

# Desde la carpeta de trabajo que contiene scripts/
bash scripts/setup.sh                                                  # dependencias del entorno (tesseract spa, utilerías PDF, tipografías)
ARGOS_DATOS=datos_revision.json ARGOS_SALIDA=. bash scripts/build_all.sh   # capturas, entregables y qc.py
ARGOS_DATOS=datos_revision.json ARGOS_SALIDA=. python3 scripts/qc.py       # solo el control de calidad mecánico
```

<!-- dev-workflow:git-workflow:start - written by /dev-workflow:setup-dev-workflow -->
## Git workflow

Before creating a branch, committing, opening or merging a pull request, or releasing, read [`docs/development/git-workflow.md`](docs/development/git-workflow.md).
<!-- dev-workflow:git-workflow:end -->

<!-- dev-workflow:working-with-the-developer:start - written by /dev-workflow:setup-dev-workflow -->
## Working with the developer

- Work one step at a time. Before each step, say what it changes and why.
- Commit each step on its own, then stop until the developer replies "next" (or "siguiente").
- Under `/mattpocock-skills:implement` or `/mattpocock-skills:implement-spec`, assign each issue to yourself before any other write.
- Under `/mattpocock-skills:implement` or `/mattpocock-skills:implement-spec`, do every step and commit each one without stopping.
- When the work is done, open the pull request and stop. Merge only when the developer replies "merge".
<!-- dev-workflow:working-with-the-developer:end -->

## Agent skills

### Issue tracker

Issues live in GitHub Issues for JavierTapiaMx/argos-revision-paralela-skill, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Uses the five default labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and one `docs/adr/` at the repo root. See `docs/agents/domain.md`.
