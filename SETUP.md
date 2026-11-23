# Setup (Windows commands first, Mac/Linux in brackets)
1. Install Python 3.11+ and VS Code with the Python extension.
2. Open the rov-gcs folder in VS Code (File > Open Folder).
3. Terminal (Ctrl+`):
   python -m venv .venv
   .venv\Scripts\activate          (source .venv/bin/activate)
   pip install -r requirements.txt
   pip install -e .
4. Ctrl+Shift+P > "Python: Select Interpreter" > pick the .venv one.
5. Run:   python -m gcs.main      (stop with Ctrl+C)
   Test:  pytest
   Lint:  ruff check .            (ruff check . --fix auto-fixes simple things)
6. Git:
   git init
   git add .
   git commit -m "Phase 1 skeleton"
   (create an empty repo on github.com, then)
   git remote add origin <your-repo-url>
   git branch -M main
   git push -u origin main
   Commit after every working change, e.g. git commit -am "Add deadzone"

# Using it
- Click the small window so it has keyboard focus.
- W/A/S/D show up as surge/sway actions. Controller moves appear as axes.
- F5 = reload profiles file, F6 = save profiles, F7 = next profile.
- Unplug/replug the controller: you'll see [-]/[+] messages and it won't crash.
- If your controller isn't recognised, copy its name from the log into
  config/profiles.json under "controller_profiles".
