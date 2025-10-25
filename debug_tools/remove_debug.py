import os

path = r'C:\Users\setsu\OneDrive\Documents\claude\keiba\horse_evaluator.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 115行目のデバッグ出力を削除
debug_line = '        print(f"[DEBUG] horses_stats count: {len(horses_stats)}, data: {horses_stats[:2]}")  # デバッグ出力\n'
if lines[114] == debug_line:
    del lines[114]
    print(f"削除完了: {debug_line.strip()}")
else:
    print("該当行が見つかりませんでした")
    print(f"実際の内容: {lines[114]}")

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
