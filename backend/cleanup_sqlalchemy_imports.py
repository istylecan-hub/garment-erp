import os
import re

target_file = "main.py"

if not os.path.exists(target_file):
    print("main.py not found")
    exit()

with open(target_file, "r") as f:
    code = f.read()

patterns = [
    r"from\s+models\s+import\s+.*",
    r"from\s+database\s+import\s+.*",
    r"Base\.metadata\.create_all\(.*\)",
    r"engine\s*=\s*create_engine\(.*\)",
    r"SessionLocal\s*=.*",
    r"from\s+sqlalchemy\s+import\s+.*",
    r"from\s+sqlalchemy\.orm\s+import\s+.*"
]

for p in patterns:
    code = re.sub(p, "", code)

with open(target_file, "w") as f:
    f.write(code)

print("SQLAlchemy cleanup complete.")
