# DEF-0034 working-directory check (development run DEV-6, Rössler)

**DEVELOPMENT (DEV-6): a check that the frozen analysis tool gives the same result when run from another working directory with relative paths. Not a sealed result.** Main session (claude-opus-5-5), 2026-10-28, before the sealed analysis.

- **Tool:** `tools/lpc_contrib.py` of the worktree `lpcstudy-wt/run/conf-j` at `freeze-j` (c19ad486b93a2ee96d64ce069ec42fd440428211), run from `lpcstudy-wt/run/phj-reh-54975c7/runs/dev` as `../../../conf-j/tools/lpc_contrib.py reh-DEV-6/phasej --replication --jobs 4 --systems rossler --out <scratch>/cwdtest`, with exit 0 after 458 s.
- **Reference:** the rehearsal analysis `reh-DEV-6/contrib-reh/contrib.json` (sha256 84852fecec9ecd5ead1a61a89789319ff5aeb069305b45feebfc2f8068b27581, listed in `docs/agent/notes/2026-10-27-phase-j-rehearsal.md`).
- **Output:** `contrib.json` sha256 f56203d1aa6dff9f9828aee08cdcb2075491203bd8eb42ae61c6dbf2f8290698. The file was kept in the session scratch directory only and is not in the repository.
- **Result:** of the 22,816 Rössler leaves, 1 differs (`/seconds`, the run time) and 0 are one-sided.
