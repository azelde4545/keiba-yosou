import sqlite3
import json

# データベース接続
conn = sqlite3.connect('dark_horse.db')
cursor = conn.cursor()

# テーブル一覧を取得
print("=== テーブル一覧 ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

print("\n=== テーブル構造 ===")
for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\n【{table_name}】")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

print("\n=== データサンプル（最初の5件） ===")
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cursor.fetchall()
    print(f"\n【{table_name}】 - {len(rows)}件")
    for row in rows:
        print(f"  {row}")

print("\n=== 全件数 ===")
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"{table_name}: {count}件")

conn.close()
