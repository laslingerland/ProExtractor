# ProExtractor Agent Instructions

## Python environment

Use the shared virtual environment of the Scripts workspace: run tests with
`/home/leonard/Scripts/.venv/bin/python -m pytest`. Add `/home/leonard/Scripts`
to `PYTHONPATH` when sibling packages such as `Shared` must be importable.

## Agent skills

### Issue tracker

Local markdown tickets under `.scratch/` in this repository. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage labels, recorded on a `Labels:` line. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` and `docs/adr/` at the repository root. See `docs/agents/domain.md`.
