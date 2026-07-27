import sys
sys.stdout.reconfigure(encoding='utf-8')

from backend.database import engine

print("Engine Created Successfully ✅")
print(engine)
