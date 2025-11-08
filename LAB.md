# Signals Lab Vision

## Why a Lab Exists
- **Faster signal feedback loops:** Today our Prefect flows emit signals that we do not fully trust; debugging requires editing production code, rerunning flows, and reading DB rows after the fact. A lab gives us a safe sandbox to iterate on the exact same datasets and strategies before they touch `pipe/`.
- **Interactive research workspace:** Marimo’s reactive notebooks (see [examples](https://docs.marimo.io/examples/) and [recipes](https://docs.marimo.io/recipes/)) combine markdown, UI widgets, and Python modules in one file. That lowers the barrier for exploring indicators, plotting outputs, and sharing runnable experiments.
- **Bridging data + strategy logic:** By pointing the notebooks at our local Postgres (`docker-compose`) and reusing the `lib/strategies` registry, we can validate hypotheses (e.g., RSI thresholds, momentum filters) with real bars before promoting code to Prefect tasks.
- **Learning-friendly surface area:** The lab doubles as a place to learn Marimo, Polars, Altair, and quant techniques without jeopardizing production; every notebook can cite resources such as [working with dataframes](https://docs.marimo.io/guides/working_with_data/dataframes/), [reusing functions](https://docs.marimo.io/guides/reusing_functions/), and community notebooks on [Molab](https://molab.marimo.io/notebooks/nb_TWVGCgZZK4L8zj5ziUBNVL).

## Proposed Scope
**In-bounds**
- Exploratory signal generation, indicator tuning, and backtest prototypes backed by our local database.
- Shared helper modules (DB access, strategy adapters, visualization utilities) that power multiple notebooks.
- Educational content: runnable Marimo notebooks illustrating quant concepts or repo-specific workflows.

**Out-of-bounds**
- Production flows, schedules, or deployments; anything promoted must graduate into `pipe/` with tests.
- One-off scripts with no documentation; every artifact should be reproducible (checked-in notebooks + data provenance notes).

## Folder Layout (top-level `/lab`)
```
/lab
  pyproject.toml        # uv project; depends on marimo, polars[native], psycopg[binary], plotly/altair, plus editable ../pipe
  README.md             # quickstart, data access instructions, publishing checklist
  /notebooks            # marimo apps (strategy_lab.py, backtest_suite.py, data_quality.py, etc.)
  /lib                  # shared helpers: db.py, strategies.py, viz.py, scenarios.py
  /data                 # optional cached exports or mock datasets (gitignored)
  /outputs              # generated artifacts (CSV/JSON/HTML exports), also gitignored by default
  /templates            # reusable notebook scaffolds or code snippets
```

## Tooling & Dependencies
- **uv-first workflow:** `uv init lab`, `uv add marimo polars[native] psycopg[binary] plotly altair`, and declare `pipe = { path = "../pipe", editable = true }` so notebooks import `pipe.lib.strategies`.
- **Database connectivity:** `lib/db.py` centralizes pulling `DATABASE_URL` from the environment (or `pipe.settings`) and exposes helpers such as `fetch_price_history(symbol, start, end) -> pl.DataFrame`.
- **Strategy adapters:** `lib/strategies.py` wraps `get_strategy` and `StrategyInputs`, stitching Polars frames (indicators, prices) into the exact objects our Prefect tasks expect. Supports overrides so Marimo widgets can tune parameters inline.
- **Visualization stack:** Plotly for interactive charts, Altair for quick statistical views (see [Altair on PyPI](https://pypi.org/project/altair/)). Encapsulate styling defaults in `lib/viz.py` so notebooks remain consistent.

## Workflow
1. **Setup**
   - `cd lab && uv sync`
   - Export `DATABASE_URL` (same string used by backend/pipe) and ensure `docker-compose up -d` is running.
2. **Experiment**
   - `uv run marimo run notebooks/strategy_lab.py` to open an interactive UI with symbol pickers, date ranges, and parameter sliders.
   - Use Marimo components (`mo.ui.slider`, `mo.ui.table`, etc.) to adjust strategy parameters; reactive recomputation gives immediate visual + textual feedback.
3. **Share / Review**
   - `uv run marimo export notebooks/strategy_lab.py html --output outputs/strategy_lab_<date>.html` to ship a snapshot with reasoning and charts.
   - Document key findings in README or inline markdown cells; capture SQL queries or dataset hashes for reproducibility.
4. **Promote**
   - When logic stabilizes, port the functions into `pipe/lib/strategies` (plus tests under `pipe/tests/`), file a PR, and retire the experimental cell or tag it as “graduated.”

## Success Criteria
- Confidently validate new or updated strategies (RSI guardrails, momentum filters, etc.) inside Marimo before touching Prefect.
- Reduce “unknown unknowns” in the signal pipeline by pairing every change with a lab notebook that demonstrates expected behavior on historical data.
- Provide a structured learning path for Marimo + quant analysis so contributors can ramp quickly without breaking production code.

## Reference Material
- Marimo overview + gallery: [docs.marimo.io/examples](https://docs.marimo.io/examples/), [docs.marimo.io/recipes](https://docs.marimo.io/recipes/)
- Guides worth bookmarking: [Reusing Functions](https://docs.marimo.io/guides/reusing_functions/), [Working with Dataframes](https://docs.marimo.io/guides/working_with_data/dataframes/)
- Molab inspiration: [Example notebook 1](https://molab.marimo.io/notebooks/nb_TWVGCgZZK4L8zj5ziUBNVL), [Example 2](https://molab.marimo.io/notebooks/nb_jJiFFtznAy4BxkrrZA1o9b), [Example 3](https://molab.marimo.io/notebooks/nb_WuoXgs7mjg5yqrMxJXjRpF), [Example 4](https://molab.marimo.io/notebooks/nb_vXxD13t2RoMTLjC89qdn6c)
- Visualization stack: [Altair PyPI](https://pypi.org/project/altair/)

## Next Actions
1. Confirm `/lab` naming and create the directory with the structure above.
2. Bootstrap the uv project (`pyproject.toml`, `README.md`, `.gitignore`) and wire the editable dependency on `../pipe`.
3. Implement `lib/db.py` + `lib/strategies.py` so notebooks can load Postgres data and call the existing registry.
4. Draft `notebooks/strategy_lab.py` with at least one end-to-end flow: select symbol → fetch candles/indicators → run strategy → visualize results + reasoning.
