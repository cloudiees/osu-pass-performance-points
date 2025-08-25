import argparse
import sqlite3
parser = argparse.ArgumentParser(description="idk man")

parser.add_argument(
    "--users", 
    action="store_true",
    help="Nuke users table"
)
parser.add_argument(
    "--scores",
    action="store_true",
    help="Nuke scores table"
)
parser.add_argument(
    "--maps",
    action="store_true",
    help="Nuke map table"
)

args = parser.parse_args()

with sqlite3.connect("osu_pass.db") as conn:
    cursor = conn.cursor()
    if args.maps:
        try:
            cursor.execute("DELETE FROM maps")
            cursor.execute("DELETE FROM scores")
            cursor.execute("UPDATE users SET total_performance_points = 0")
            conn.commit()
        except Exception as e:
            print(f"FAILED: {e}")
    elif args.scores:
        try:
            cursor.execute("DELETE FROM scores")
            cursor.execute("UPDATE maps SET top_acc = NULL")
            cursor.execute("UPDATE users SET total_performance_points = 0")
            conn.commit()
        except Exception as e:
            print(f"FAILED: {e}")
    elif args.users:
        try:
            cursor.execute("DELETE FROM scores")
            cursor.execute("DELET FROM users")
            cursor.execute("UPDATE maps SET top_acc = NULL")
            conn.commit()
        except Exception as e:
            print(f"FAILED: {e}")