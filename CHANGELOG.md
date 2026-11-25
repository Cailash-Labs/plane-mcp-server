# Changelog

## Cailash fork

[Cailash-Labs/plane-mcp-server](https://github.com/Cailash-Labs/plane-mcp-server) is a fork of
[makeplane/plane-mcp-server](https://github.com/makeplane/plane-mcp-server) (MIT), based on upstream
0.3.7, for our self-hosted Plane Community (v1.4.3). It changes as little as possible so it rebases
cleanly.

### What differs from upstream

- **Intake triage works on Community.** `intake` action `update` sends `status`, `snoozed_till` and
  `duplicate_to` through the classic `PATCH /intake-issues/{issue_id}/`. Upstream uses
  `PATCH /intake-issues/{issue_id}/status`, which Community does not register (404). Triage still
  requires the API key's user to be a project **Admin**: for a Member, Plane answers 200 and leaves
  the status unchanged.
- **`PLANE_EDITION`** (default `community`) stops advertising tools whose routes Community lacks:
  `project_estimate`, `workitem_type`, `workitem_property`, `customer`, `customer_property`,
  `customer_request`. Their retired per-operation names stop resolving too. Set
  `PLANE_EDITION=full` to get the upstream catalogue.

Fork-only code: `plane_mcp/tools/editions.py`, the filter in `plane_mcp/tools/__init__.py`, the
`update` branch in `plane_mcp/tools/intake.py`, and `tests/tools/test_cailash_fork.py`. The test
suite runs with `PLANE_EDITION=full` (set in `tests/conftest.py`) so upstream's tests apply unchanged.

### Syncing with upstream

```bash
git fetch upstream
git switch -c chore/sync-upstream origin/main
git rebase upstream/main        # or: git merge upstream/main
uv pip install -e ".[dev]" && pytest
git push -u origin chore/sync-upstream   # then open a PR against Cailash-Labs main
```

Never push to, or open pull requests against, `upstream`. Conflicts are expected only in
`plane_mcp/tools/intake.py` (the `update` branch) and `plane_mcp/tools/__init__.py`
(`register_tools`). If upstream adds a tool that 404s on Community, add its name to
`COMMUNITY_HIDDEN` in `plane_mcp/tools/editions.py`.
