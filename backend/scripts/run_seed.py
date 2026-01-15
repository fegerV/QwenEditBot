import sys
import os
# Ensure backend directory is on sys.path so 'app' package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, seed_presets_if_empty


def main():
    db = SessionLocal()
    try:
        seed_presets_if_empty(db)
        print("Seed completed")
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    main()
