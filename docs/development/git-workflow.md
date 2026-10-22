# Git workflow

<!-- dev-workflow:base:start - written by /setup-dev-workflow; edit the base in JavierTapiaMx/dev-workflow, not here -->

This repository has one developer. Every change goes issue -> branch -> pull request into `develop` -> release pull request into `main`. Why two long-lived branches and merge commits: [dev-workflow ADR 0001](https://github.com/JavierTapiaMx/dev-workflow/blob/develop/docs/adr/0001-develop-and-main-with-merge-commits.md). Why CalVer: [dev-workflow ADR 0002](https://github.com/JavierTapiaMx/dev-workflow/blob/develop/docs/adr/0002-calver-for-every-version.md).

Values that differ per repository (GitHub Project number, deploy, checks) are in [Project-specific](#project-specific) at the end of this file.

## Branches

| Branch | Purpose |
| --- | --- |
| `main` | What is released. Changes only through a release, hotfix, or sync pull request. |
| `develop` | Default branch. Integrated work waiting for the next release. |
| `feature/*`, `bugfix/*`, `chore/*`, `refactor/*`, `docs/*` | One branch per issue, created from `develop`. |
| `hotfix/*` | Urgent fix of a release, created from `main`. |
| `research/*`, `prototype/*` | Pushed by `/wayfinder` without a pull request. Never deleted, because their tickets link to them. |
| `dependabot/*` | Opened by Dependabot. No issue. |

Name branches `<type>/<issue-number>-<short-kebab-description>`, for example `feature/42-add-login-form`.

Rulesets enforce the table: `main` and `develop` take changes only through a pull request merged with a merge commit, with the `checks` CI job passing where the repository has CI, and nobody can force-push or delete them. `research/**` and `prototype/**` cannot be deleted. As admin, the developer can merge a pull request past a red check in an emergency, but cannot push to `main` or `develop` directly. A private repository needs GitHub Pro for rulesets; without it these rules hold only by convention.

## Issues

Every change starts with an issue, except Dependabot pull requests. A repository may also have a GitHub Project for planning; [Project-specific](#project-specific) says whether it does. When it does, GitHub adds every new issue to it.

### Creating an issue

Write the title and body in the language [`AGENTS.md`](../../AGENTS.md) sets for GitHub text. An implementation issue gets, without being asked:

- Labels from `gh label list`: one type label (`Bug`, `Feature`, `Refactor`, `Documentation`, `Question`), the technology labels the issue touches, and the domain labels for the areas its scope covers. Pick the central ones, not every related one. Triage labels follow `docs/agents/triage-labels.md`.
- In a repository with a GitHub Project: Priority and Size as Project fields, never as labels. Estimate both from the scope; ask only when it is unclear. The issue is already in the Project, so do not run `gh project item-add`. Without a Project, the issue has no Priority or Size.

```bash
gh project item-edit <project-number> --owner JavierTapiaMx --url <issue-url> --field Priority --value <High|Medium|Low>
gh project item-edit <project-number> --owner JavierTapiaMx --url <issue-url> --field Size --value <XS|S|M|L|XL>
```

Wayfinder maps and tickets (labels `wayfinder:*`) hold decisions, not implementation work. They carry only their `wayfinder:*` label: no other labels, no Priority, no Size.

### Starting work

Assign the issue to yourself before any other write: `gh issue edit <n> --add-assignee @me`. A Wayfinder claim does the same. In a repository with a GitHub Project, the `project-fields-on-assign` workflow then sets Iteration to the current iteration and Status to In progress.

### Closing

| Issue type | How it closes |
| --- | --- |
| Feature, bugfix, chore, refactor, docs | The pull request body starts with `Closes #<n>`. Merging into `develop` closes the issue. |
| Hotfix | The pull request targets `main`, which is not the default branch, so `Closes` does nothing. `/hotfix` runs `gh issue close <n>` after the merge. |
| Wayfinder ticket | The Wayfinder skill closes it when it records the resolution. |

Only the first line of a pull request body may hold a closing keyword (`close`, `closes`, `fix`, `fixes`, `resolve`, `resolves` followed by `#n`). GitHub closes every issue that follows one, wherever it appears, so mention any other issue as "see #n".

Read an issue before proposing to close it. A `wayfinder:map` stays open until the whole map is done.

## Daily workflow

1. Create the issue and assign it to yourself.
2. Create the branch from `develop`:

   ```bash
   git switch develop && git pull
   git switch -c feature/42-add-login-form
   ```

   In T3 Code, start the thread in a new worktree and begin the first message with `Issue #42:`. The branch naming setting turns that into the branch name.

3. Implement. `/implement` ends with `/code-review`; for a change made without `/implement`, run `/code-review origin/develop` before opening the pull request.
4. Commit. The subject is imperative, starts with a capital letter, has no `feat:`-style prefix, and ends with the issue number: `Add login form validation (#42)`. Write it in the language `AGENTS.md` sets for GitHub text. Merge commits keep every commit in history, so each commit describes one change.
5. Push and open the pull request. The base defaults to `develop`. The title describes the change without the issue number: GitHub adds the pull request number to the merge commit, and `Closes #n` links the issue. The body is `.github/pull_request_template.md` filled in, starting with `Closes #42`. Pass it with `--body-file -`, not `--fill`, which writes the body from the commits and skips the template:

   ```bash
   git push -u origin feature/42-add-login-form
   gh pr create --title "Add login form validation" --body-file - <<'EOF'
   Closes #42

   <the other sections of .github/pull_request_template.md, filled in>
   EOF
   ```

   In T3 Code, link the pull request to the thread with `link_pull_request`.

6. Stop. Check the preview where the repository has one, and wait for the developer to say "merge".
7. On "merge", read the head commit, wait for the required checks, then merge with a merge commit. `--match-head-commit` makes GitHub refuse the merge if a commit landed on the branch after the checks started, so nothing merges that no check or review saw. If GitHub refuses the merge because the head moved, stop and report the new commit:

   ```bash
   sha=$(gh pr view --json headRefOid --jq .headRefOid)
   gh pr checks --watch --required
   gh pr merge --merge --match-head-commit "$sha"
   ```

   Never pass `--delete-branch`. The repository setting "Delete branch on merge" already deletes the branch on GitHub, and step 8 or T3 Code deletes the local one. From a worktree, `gh` before 2.99.0 fails after the merge when it tries to switch to `develop`, and `gh` 2.99.0 or later run from another checkout removes the worktree that holds the branch.

   If `develop` moved ahead, press Update branch on the pull request first. It merges `develop` into the branch.

8. Update `develop` and delete merged local branches. In a T3 Code worktree, skip this step: `develop` is checked out in the main checkout, so `git switch develop` fails. T3 Code deletes the worktree after the merge, and the next `git cleanup` in the main checkout deletes the branch.

   ```bash
   git switch develop && git pull
   git cleanup
   ```

## Release (`develop` -> `main`)

`/release` runs these steps. They are written here so a release can also be done by hand.

Versions use CalVer `vYEAR.MONTH.N`, with no zero padding on the month. `N` starts at 0 each month and goes up by one for every release or hotfix in that month: `v2026.10.0`, `v2026.10.1`, `v2026.11.0`.

1. Check that `main` has nothing `develop` lacks except merge commits. A non-merge commit here is an unsynced hotfix: stop and sync it first.

   ```bash
   git fetch && git log --no-merges origin/develop..origin/main
   ```

2. Pick the version: the latest tag from `gh release list`, plus one in the same month, or `.0` in a new month.
3. Open the release pull request. On "merge", read its head commit, wait for the checks, and merge it with a merge commit pinned to that commit:

   ```bash
   gh pr create --base main --head develop --title "Release v2026.10.0" --body "Release v2026.10.0"
   sha=$(gh pr view <release-pr> --json headRefOid --jq .headRefOid)
   gh pr checks <release-pr> --watch --required
   gh pr merge <release-pr> --merge --match-head-commit "$sha"
   ```

4. Wait for the deploy described in [Project-specific](#project-specific), if the repository has one.
5. Tag and publish the release. GitHub lists the merged pull requests in the notes:

   ```bash
   gh release create v2026.10.0 --target main --generate-notes
   ```

6. Sync `develop` with `main` through a pull request, because the ruleset blocks pushing to `develop`. It carries no new work, so it merges without waiting for "merge". "Delete branch on merge" deletes the head branch of every merged pull request, so the head is `main` only when the ruleset forbids deleting it; otherwise it is a temporary `sync/v2026.10.0` branch at `main`:

   ```bash
   gh api repos/{owner}/{repo}/rules/branches/main --jq '[.[].type] | index("deletion") != null'
   git push origin origin/main:refs/heads/sync/v2026.10.0   # only when the line above prints false
   gh pr create --base develop --head <main or sync/v2026.10.0> --title "Sync main into develop after v2026.10.0" --body "Sync main into develop after v2026.10.0"
   sha=$(gh pr view <sync-pr> --json headRefOid --jq .headRefOid)
   gh pr checks <sync-pr> --watch --required
   gh pr merge <sync-pr> --merge --match-head-commit "$sha"
   ```

## Hotfix (`hotfix/*` -> `main`)

`/hotfix` runs these steps.

1. Create the issue and the branch from `main`:

   ```bash
   git switch main && git pull
   git switch -c hotfix/88-fix-auth-crash
   ```

2. Commit, push, and open the pull request against `main`. The title and body follow step 5 of the daily workflow:

   ```bash
   git push -u origin hotfix/88-fix-auth-crash
   gh pr create --base main --title "Fix auth crash" --body-file - <<'EOF'
   Closes #88

   <the other sections of .github/pull_request_template.md, filled in>
   EOF
   ```

   `Closes #88` neither closes nor links the issue, because `main` is not the default branch; it only shows as a mention in the issue's timeline. `/hotfix` closes the issue after the merge.

3. On "merge", read the head commit, wait for the checks, merge pinned to that commit as in step 7 of the daily workflow, wait for the deploy, release with the next version, and close the issue:

   ```bash
   sha=$(gh pr view --json headRefOid --jq .headRefOid)
   gh pr checks --watch --required
   gh pr merge --merge --match-head-commit "$sha"
   gh release create v2026.10.1 --target main --generate-notes
   gh issue close 88
   ```

4. Sync `develop` with `main`, as in step 6 of the release.

## Dependabot

Dependabot opens security pull requests as soon as a fix exists, and version pull requests once a month: one grouped pull request for GitHub Actions and one for npm minor and patch updates, each waiting 7 days after a version is published. Major npm versions never come from Dependabot; plan them as an issue. A Dependabot pull request has no issue and no `Closes` line. Merge it like any other pull request once its checks pass.

## Branch cleanup

- GitHub deletes a pull request's branch when it merges.
- `fetch.prune` removes local `origin/*` references to branches deleted on GitHub.
- `git cleanup` deletes local branches already merged into `develop`. It skips `main`, `develop`, the current branch, and branches open in another worktree, and it uses `git branch -d`, which refuses to delete unmerged work.
- Check what is on GitHub with `gh api repos/{owner}/{repo}/branches`, not `git branch -r`, which can list stale references.
- Before deleting any branch by hand, show the list and confirm each one is merged: `git rev-list --count origin/develop..origin/<branch>` is 0.
- T3 Code deletes worktrees after their pull request merges, after 14 inactive days, or when their thread is deleted.

## Machine setup

Once per clone:

```bash
git config fetch.prune true
git config alias.cleanup '!git fetch --prune && git branch --merged develop | grep -vE "^[*+]|^ *(main|develop)$" | xargs -r git branch -d'
```

Once per machine:

```bash
git config --global core.longpaths true   # Windows: worktree paths get long
gh auth login && gh auth setup-git        # git, and the dev-workflow plugin, use the gh credential
```

T3 Code settings (Settings -> Source Control, with this machine selected as the environment):

- Default merge method: Merge
- Source control writing style: Repository conventions
- Follow change request templates: on
- Worktree branch naming, custom instructions: `Name the branch <type>/<issue-number>-<short-kebab-description>. Type is one of: feature, bugfix, hotfix, chore, refactor, docs. Take the issue number from the prompt; if none is given, omit it.`

Settings -> Storage: delete worktrees with deleted threads, delete inactive worktrees after 14 days, delete merged worktrees.

<!-- dev-workflow:base:end -->

## Project-specific

Owned by this repository. `/setup-dev-workflow` never overwrites this section.

### GitHub Project

No GitHub Project.

### Checks

El job `checks` de `.github/workflows/ci.yml` corre `python -m py_compile` sobre cada archivo `.py` y `bash -n` sobre cada archivo `.sh` del repositorio. Un merge en `main` publica los scripts de inmediato, así que un error de sintaxis no debe llegar a `main`. Los mismos comandos están en el bloque `Commands` de [`AGENTS.md`](../../AGENTS.md) para correrlos en local.

### Deploy

El skill clona este repositorio desde `main` en cada ejecución (`SKILL.md`, paso 3 de la obtención de `scripts/`), así que un merge en `main` publica de inmediato los scripts y `datos_revision.plantilla.json`. `SKILL.md` no se actualiza solo: después de cada release, reinstálalo en Claude (opción 1 o 2 del README) y comprueba que aparezca `argos-revision-paralela` con su descripción.

### Other rules

- El repositorio es público y debe seguir siéndolo: si se vuelve privado, la descarga de los scripts falla.
- Nunca agregues expedientes, digitalizaciones, resultados de revisiones ni datos de contratos reales. Antes de cada pull request, confirma que `SKILL.md` y los scripts no tengan datos de un expediente real.
