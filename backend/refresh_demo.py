"""Re-apply the demo labor roster (labor categories, capacity, the functional teams and the Depot
demo personas) to the CURRENT database. Idempotent, by name.

    cd backend && .venv/bin/python refresh_demo.py
"""

from app import create_app
from demo_roster import apply_demo_roster

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print(apply_demo_roster())
