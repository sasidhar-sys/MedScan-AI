import os
import shutil
import stat

base = r"c:\Projects\MedScan-AI"
seds_target = os.path.join(base, "applications", "SEDS")

os.makedirs(seds_target, exist_ok=True)

folders_to_move = [
    "backend",
    "frontend",
    "datasets",
    "models",
    "explainability",
    "uploads",
    "reports",
    "notebooks",
    "deployment",
    "logs",
    "alembic",
]

files_to_move = [".env", ".env.example", "requirements.txt", "alembic.ini"]

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    try:
        func(path)
    except Exception:
        pass

for folder in folders_to_move:
    src = os.path.join(base, folder)
    dst = os.path.join(seds_target, folder)
    if os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        try:
            shutil.rmtree(src, onerror=remove_readonly)
        except Exception as e:
            print(f"Notice: Could not fully delete {src}: {e}")

for file in files_to_move:
    src = os.path.join(base, file)
    dst = os.path.join(seds_target, file)
    if os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
        shutil.copyfile(src, dst)
        try:
            os.remove(src)
        except Exception:
            pass

for f in os.listdir(base):
    if f.startswith("test_") and f.endswith(".py"):
        src = os.path.join(base, f)
        dst = os.path.join(seds_target, f)
        shutil.copyfile(src, dst)
        try:
            os.remove(src)
        except Exception:
            pass

for legacy in ["model", "dataset", "dataset.zip", "BACKUPAPP.txt", "app.py"]:
    p = os.path.join(base, legacy)
    if os.path.exists(p):
        if os.path.isdir(p):
            try:
                shutil.rmtree(p, onerror=remove_readonly)
            except Exception:
                pass
        else:
            try:
                os.remove(p)
            except Exception:
                pass

medscan_platform = os.path.join(base, "applications", "MedScan-Platform")
univ_cdss = os.path.join(base, "applications", "Universal-CDSS")
if os.path.exists(univ_cdss):
    if os.path.exists(medscan_platform):
        try:
            shutil.rmtree(univ_cdss, onerror=remove_readonly)
        except Exception:
            pass
    else:
        try:
            os.rename(univ_cdss, medscan_platform)
        except Exception:
            pass

for app_name in [
    "SEDS",
    "SLDS",
    "SOCDS",
    "SSLDS",
    "SBTDS",
    "SBCDS",
    "SLDDS",
    "SRDS",
    "MedScan-Platform",
]:
    app_path = os.path.join(base, "applications", app_name)
    os.makedirs(os.path.join(app_path, "documentation"), exist_ok=True)
    for f in ["README.md", "roadmap.md"]:
        fp = os.path.join(app_path, f)
        if not os.path.exists(fp):
            with open(fp, "w", encoding="utf-8") as handle:
                handle.write(f"# {app_name}\n")

print("SEDS Relocation and MedScan AI v2 Architecture Completed Successfully!")
