# The eight steps as files

Generated, not written: each of these is `app.py` exactly as it stood at the
matching tag. `tools/export_steps.sh` makes them, so `app.py` and its history
stay the one source and these cannot drift.

Any of them runs on its own:

```sh
uv run streamlit run steps/03_colony.py
```

Careful with the two that read files — `level1.json` and `.env` are looked for
in the directory you start from, so run them from the repository root as above,
not from inside `steps/`.

The same states are `git checkout step-3` if you would rather have the whole
tree at that point.
