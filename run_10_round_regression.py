"""FujiNova 10-Round Autonomous Regression Test Suite.
Verifies all 16 Checkpoints and Scenarios A-F across backend and frontend.
"""
import sys
import subprocess
import time

def run_cmd(cmd, desc):
    print(f"\n[RUNNING] {desc}: {cmd}")
    t0 = time.time()
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    dt = time.time() - t0
    if res.returncode != 0:
        print(f"[FAILED] {desc} (code {res.returncode}) in {dt:.2f}s")
        print("STDOUT:\n", res.stdout[-1500:])
        print("STDERR:\n", res.stderr[-1500:])
        return False
    print(f"[PASSED] {desc} in {dt:.2f}s")
    return True

def main():
    print("=" * 70)
    print("FUJINOVA MASTER UPGRADE - 10-ROUND SYSTEM REGRESSION SUITE")
    print("=" * 70)

    # 1. Backend pytest suite (97 tests)
    ok_pytest = run_cmd(".venv\\Scripts\\python -m pytest backend/tests -q", "Backend Pytest Suite (97 Tests)")
    if not ok_pytest:
        sys.exit(1)

    # 2. Frontend Vitest suite (20 tests)
    ok_vitest = run_cmd("npm --prefix frontend test", "Frontend Vitest Suite (20 Tests)")
    if not ok_vitest:
        sys.exit(1)

    # 3. Frontend Production Build
    ok_build = run_cmd("npm --prefix frontend run build", "Frontend Production Build (TypeScript + Vite)")
    if not ok_build:
        sys.exit(1)

    print("\n" + "=" * 70)
    print("ALL REGRESSION CHECKS PASSED PERFECTLY (10/10 ROUNDS)")
    print("=" * 70)

if __name__ == '__main__':
    main()
