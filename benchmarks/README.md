# LCM Benchmark Harness

The benchmark harness compares recorded agent runs against the same versioned ground truth. It does not claim that token count alone proves quality: successful task completion and retrieval recall remain first-class metrics.

## Run format

Each result records observable measurements from one agent attempt:

- `success`: whether the task acceptance checks passed;
- `files_read` and `symbols_selected`;
- `dependencies_found`, `tests_found`, and `constraints_found`;
- input/output `tokens`, tool calls, and wall-clock duration.

Use the same model, repository commit, task prompt, tool permissions, and timeout for every compared configuration. Run tasks in clean worktrees and retain raw transcripts outside this repository when available.

```bash
python scripts/benchmark.py \
  --suite benchmarks/suites/lcm-self.json \
  --run baseline=/path/to/baseline.json \
  --run lcm=/path/to/lcm.json \
  --markdown-output benchmark-report.md \
  --json-output benchmark-report.json
```

Copy `benchmarks/run-template.json` for each recorded configuration. Empty ground-truth categories are excluded from aggregate precision and recall and appear as `n/a` in reports.
