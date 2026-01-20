import argparse, subprocess, sys, os
from pathlib import Path
from config import TRANSFORMED_DIR 

def run(cmd):
    print(">>>", " ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode != 0:
        sys.exit(res.returncode)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--clean", action="store_true")
    args = ap.parse_args()

    transf_dir = Path(TRANSFORMED_DIR)

    # transform
    run([sys.executable, "src/Transform.py", "--data", args.data])

    # validate CSVs exist
    for name in ["venues","artists","events","event_price_history"]:
        if not (transf_dir / f"{name}.csv").exists():
            sys.exit(f"Missing {name}.csv. Transform failed.")

    # load
    run([sys.executable, "src/db/Load.py", "--db", args.db])

    # optional cleanup: remove the transformed/normalized datasets
    if args.clean:
        for name in ["venues","artists","events","event_price_history"]:
            try: 
                os.remove(transf_dir / f"{name}.csv")
            except FileNotFoundError: 
                pass
        try: 
            transf_dir.rmdir()
        except OSError: 
            pass
        print("Cleaned intermediate CSVs.")

if __name__ == "__main__":
    main()
