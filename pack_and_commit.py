import os, shutil, subprocess, sys

# 1. Tim file .pyd
pyd_file = None
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.pyd') and '_sqlite3' in f:
            pyd_file = os.path.join(root, f)
            break

if not pyd_file:
    print("LOI: Khong tim thay file .pyd! Sep hay build lai nhe.")
    sys.exit(1)

print(f"Da tim thay: {pyd_file}")

# 2. Dua vao dung cau truc package
dest_dir = "sqlcipher3"
if not os.path.exists(dest_dir): os.makedirs(dest_dir)
shutil.copy2(pyd_file, os.path.join(dest_dir, "_sqlite3.pyd"))

# 3. Tao file setup_wheel.py de dong goi
setup_code = """
from setuptools import setup, find_packages
setup(
    name='sqlcipher3-binary',
    version='4.12.0',
    packages=['sqlcipher3'],
    package_data={'sqlcipher3': ['*.pyd']},
    include_package_data=True,
    zip_safe=False,
)
"""
with open("setup_wheel.py", "w") as f: f.write(setup_code)

# 4. Chay lenh dong goi
subprocess.run([sys.executable, "setup_wheel.py", "bdist_wheel"])
print("HOAN TAT! File whl nam trong thu muc 'dist'")
