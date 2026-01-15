import sqlite3
from pathlib import Path

ROOT_DB = Path.cwd() / "qwen.db"
BACKEND_DB = Path.cwd() / "backend" / "qwen.db"

def inspect(db_path: Path):
    print(f"\nInspecting: {db_path}  ({round(db_path.stat().st_size/1024/1024,6)} MB)")
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("PRAGMA integrity_check;")
        res = cur.fetchone()
        print(f"PRAGMA integrity_check -> {res[0] if res else res}")

        cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name;")
        objs = cur.fetchall()
        print(f"Found {len(objs)} tables/views")
        for row in objs:
            name = row[0]
            typ = row[1]
            print(f"\n--- {typ.upper()}: {name}")
            try:
                cur.execute(f"PRAGMA table_info('{name}');")
                cols = cur.fetchall()
                col_names = [c[1] for c in cols]
                print("Columns: " + ", ".join(col_names) if col_names else "Columns: (none)")
            except Exception as e:
                print(f"  (cannot get columns: {e})")
            try:
                cur.execute(f"SELECT COUNT(*) AS cnt FROM '{name}';")
                cnt = cur.fetchone()[0]
            except Exception as e:
                cnt = f"ERR: {e}"
            print(f"Rows: {cnt}")
            try:
                cur.execute(f"SELECT * FROM '{name}' LIMIT 3;")
                samples = cur.fetchall()
                if samples:
                    for r in samples:
                        print("  " + ", ".join(f"{k}={r[k]!s}" for k in r.keys()))
                else:
                    print("  (no sample rows)")
            except Exception as e:
                print(f"  (cannot fetch sample rows: {e})")

        conn.close()
    except Exception as e:
        print(f"ERROR opening {db_path}: {e}")


def main():
    print("Database inspection script")
    for p in [ROOT_DB, BACKEND_DB]:
        if p.exists():
            inspect(p)
        else:
            print(f"\nNot found: {p}")

if __name__ == '__main__':
    main()
