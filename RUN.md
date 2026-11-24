# Run the checks

From the project folder, create and activate the virtual environment, install dependencies, then run the full test suite:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
```

The contract tests currently include expected failures that document app defects. Do not treat those failures as a setup problem.
