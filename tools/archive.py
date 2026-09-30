#!/usr/bin/env python3
"""記事データの過去版を archive/ に残す（1週間分）。

使い方（新しい articles.json を置いたあと、git add の前に実行する）:
    python3 tools/archive.py articles.json
    python3 tools/archive.py hotel/articles.json
    python3 tools/archive.py design/articles.json

直前の版（HEAD の内容）を archive/<その日の日付>.json として保存し、
archive/index.json を作り直して、古いものを KEEP 日分だけ残して削除する。
"""
import json, os, subprocess, sys

KEEP = 7
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main(path):
    adir = os.path.join(REPO, os.path.dirname(path), "archive")
    os.makedirs(adir, exist_ok=True)
    new = json.load(open(os.path.join(REPO, path), encoding="utf-8"))
    today = new["generated_at"][:10]

    prev_raw = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=REPO,
                              capture_output=True, text=True).stdout
    try:
        prev = json.loads(prev_raw)
    except Exception:
        prev = None
    if prev and prev.get("articles"):
        day = prev["generated_at"][:10]
        if day != today:
            with open(os.path.join(adir, day + ".json"), "w", encoding="utf-8") as f:
                json.dump(prev, f, ensure_ascii=False, separators=(",", ":"))
            print(f"archived {day} ({len(prev['articles'])}件)")

    days = sorted((f[:-5] for f in os.listdir(adir)
                   if f.endswith(".json") and f != "index.json"), reverse=True)
    for old in days[KEEP:]:
        os.remove(os.path.join(adir, old + ".json"))
        print(f"removed {old}")
    days = days[:KEEP]

    idx = []
    for day in days:
        d = json.load(open(os.path.join(adir, day + ".json"), encoding="utf-8"))
        idx.append({"date": day, "count": len(d.get("articles", []))})
    with open(os.path.join(adir, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"app": new.get("app", ""), "today": today, "dates": idx},
                  f, ensure_ascii=False, indent=1)
    print(f"{path}: 過去{len(idx)}版 {[i['date'] for i in idx]}")

if __name__ == "__main__":
    main(sys.argv[1])
