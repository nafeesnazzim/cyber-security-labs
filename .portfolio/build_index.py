#!/usr/bin/env python3
"""Regenerate progress views for the Self Study Journey portfolio.

Reads .portfolio/roadmap.json and every entry file in phase-*/week*-*/, then rewrites:
  - README.md          (only between <!-- PROGRESS:START --> and <!-- PROGRESS:END -->)
  - phase-*/README.md  (fully generated)
  - CHANGELOG.md       (fully generated journal log)

An entry is a markdown file named YYYY-MM-DD-learn-<slug>.md or YYYY-MM-DD-lab-<slug>.md
inside a week folder, with YAML front matter containing at least `title`.
A week is "complete" when it has at least one learn entry AND one lab entry.

Run from the repo root:  python3 .portfolio/build_index.py
"""
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
ENTRY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(learn|lab)-(.+)\.md$")


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    data = {}
    if not m:
        return data
    for line in m.group(1).splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"').strip("'")
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
        data[k.strip()] = v
    return data


def collect(roadmap):
    weeks = []
    for p in roadmap["phases"]:
        for w in p["weeks"]:
            folder = ROOT / p["folder"] / w["folder"]
            entries = []
            if folder.is_dir():
                for f in sorted(folder.iterdir()):
                    m = ENTRY_RE.match(f.name)
                    if f.is_file() and m:
                        fm = front_matter(f)
                        entries.append({
                            "date": m.group(1), "type": m.group(2),
                            "title": fm.get("title") or m.group(3).replace("-", " ").title(),
                            "attack": fm.get("attack") or [],
                            "tools": fm.get("tools") or [],
                            "path": f.relative_to(ROOT).as_posix(),
                        })
            types = {e["type"] for e in entries}
            status = "complete" if {"learn", "lab"} <= types else ("started" if entries else "not-started")
            weeks.append({"phase": p, "week": w, "entries": entries, "status": status,
                          "span": w["last"] - w["first"] + 1})
    return weeks


def week_label(w):
    return f"Week {w['first']}" if w["first"] == w["last"] else f"Weeks {w['first']}–{w['last']}"


ICON = {"complete": "✅", "started": "🟡", "not-started": "⬜"}


def link(path, from_dir=""):
    rel = path[len(from_dir) + 1:] if from_dir and path.startswith(from_dir + "/") else path
    return quote(rel)


def build_readme_block(roadmap, weeks):
    total = roadmap["total_weeks"]
    done = sum(x["span"] for x in weeks if x["status"] == "complete")
    started = sum(x["span"] for x in weeks if x["status"] == "started")
    n_entries = sum(len(x["entries"]) for x in weeks)
    pct = round(100 * done / total) if total else 0
    def shield(label, msg, colour):
        esc = lambda s: quote(s.replace("-", "--").replace("_", "__"), safe="")
        return f"https://img.shields.io/badge/{esc(label)}-{esc(msg)}-{colour}"
    badge = shield("roadmap", f"{done}/{total} weeks ({pct}%)", "2ea44f")
    badge2 = shield("in progress", f"{started} weeks", "dbab09")
    out = [f"![Roadmap progress]({badge}) ![In progress]({badge2})", "",
           f"**{n_entries} entries** across the roadmap. ✅ complete (notes + hands-on) · 🟡 started · ⬜ not started", "",
           "| Phase | Weeks | Progress | Entries |", "|---|---|---|---|"]
    for p in roadmap["phases"]:
        pw = [x for x in weeks if x["phase"] is p]
        span = sum(x["span"] for x in pw)
        pdone = sum(x["span"] for x in pw if x["status"] == "complete")
        pent = sum(len(x["entries"]) for x in pw)
        rng = f"{pw[0]['week']['first']}–{pw[-1]['week']['last']}"
        bar = "".join(ICON[x["status"]] for x in pw)
        out.append(f"| [{p['number']}. {p['title']}]({quote(p['folder'])}/) | {rng} | {bar} {pdone}/{span} | {pent} |")
    recent = sorted((e | {"wk": x} for x in weeks for e in x["entries"]), key=lambda e: e["date"], reverse=True)[:8]
    if recent:
        out += ["", "### Latest entries", "", "| Date | Entry | Type | Week | ATT&CK |", "|---|---|---|---|---|"]
        for e in recent:
            att = ", ".join(f"[{t}](https://attack.mitre.org/techniques/{t.replace('.', '/')}/)" for t in e["attack"]) or "—"
            out.append(f"| {e['date']} | [{e['title']}]({link(e['path'])}) | {'Notes' if e['type']=='learn' else 'Lab'} | {week_label(e['wk']['week'])} | {att} |")
    out += ["", "Full history: [CHANGELOG.md](CHANGELOG.md)"]
    return "\n".join(out)


def build_phase_readme(p, weeks):
    pw = [x for x in weeks if x["phase"] is p]
    out = [f"# Phase {p['number']}: {p['title']}", "",
           "*Generated by `.portfolio/build_index.py`. Don't edit by hand.*", ""]
    if p["cert_alignment"]:
        out += [f"**🎓 Certification alignment:** {p['cert_alignment']}", ""]
    out += ["| Week | Topic | Status | Entries |", "|---|---|---|---|"]
    for x in pw:
        w = x["week"]
        ents = "<br>".join(f"[{'📘' if e['type']=='learn' else '🧪'} {e['title']}]({link(e['path'], p['folder'])})" for e in x["entries"]) or "—"
        topic = ("🔄 Checkpoint: " if w["checkpoint"] else "") + w["title"]
        out.append(f"| {week_label(w)} | {topic} | {ICON[x['status']]} | {ents} |")
    out += ["", "📘 learning notes · 🧪 hands-on lab", "", "[← Back to the overview](../README.md)"]
    return "\n".join(out) + "\n"


def build_changelog(weeks):
    ents = sorted((e | {"wk": x} for x in weeks for e in x["entries"]), key=lambda e: (e["date"], e["path"]), reverse=True)
    out = ["# Journal log", "", "Every entry added to this portfolio, newest first.",
           "*Generated by `.portfolio/build_index.py`.*", ""]
    month = None
    for e in ents:
        if e["date"][:7] != month:
            month = e["date"][:7]
            out += ["", f"## {month}", ""]
        kind = "📘 Notes" if e["type"] == "learn" else "🧪 Lab"
        out.append(f"- **{e['date']}** · {kind} · [{e['title']}]({link(e['path'])}) · Phase {e['wk']['phase']['number']}, {week_label(e['wk']['week'])}")
    return "\n".join(out) + "\n"


def main():
    roadmap = json.loads((ROOT / ".portfolio/roadmap.json").read_text(encoding="utf-8"))
    weeks = collect(roadmap)
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    block = build_readme_block(roadmap, weeks)
    new, n = re.subn(r"(<!-- PROGRESS:START -->\n).*?(<!-- PROGRESS:END -->)",
                     lambda m: m.group(1) + block + "\n" + m.group(2), text, flags=re.S)
    if n != 1:
        raise SystemExit("README.md must contain exactly one PROGRESS:START/END marker pair")
    readme.write_text(new, encoding="utf-8")
    for p in roadmap["phases"]:
        d = ROOT / p["folder"]
        d.mkdir(exist_ok=True)
        (d / "README.md").write_text(build_phase_readme(p, weeks), encoding="utf-8")
    (ROOT / "CHANGELOG.md").write_text(build_changelog(weeks), encoding="utf-8")
    done = sum(x["span"] for x in weeks if x["status"] == "complete")
    print(f"OK: {sum(len(x['entries']) for x in weeks)} entries, {done}/{roadmap['total_weeks']} weeks complete")


if __name__ == "__main__":
    main()
