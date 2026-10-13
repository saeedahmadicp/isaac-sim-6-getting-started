"""Render slide frames (PNG) and narration text for every lesson video.

    python3 learning_resource/videos/_build/make_slides.py [lesson_id ...]

Output per lesson in learning_resource/videos/_work/<lesson_id>/:
    sNN_fK.png    frame K of slide NN (steps slides reveal one bullet per frame)
    sNN.txt       narration for the slide (sent to ElevenLabs)
    plan.json     slide/frames/segment texts used by assemble.py
"""

import html
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from content import LESSONS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # learning_resource
WORK = os.path.join(ROOT, "videos", "_work")
DIAG = os.path.join(ROOT, "diagrams")
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600"
         "&family=Geist+Mono:wght@400;500;600&display=swap")

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;background:#f5f5f5;color:#2d3142;font-family:'Geist',sans-serif;overflow:hidden}
.top{position:absolute;left:96px;right:96px;top:56px;display:flex;justify-content:space-between;
     font-family:'Geist Mono',monospace;font-size:18px;letter-spacing:.16em;text-transform:uppercase;color:#4f5d75}
.foot{position:absolute;left:96px;right:96px;bottom:48px;display:flex;align-items:center;gap:24px;
      font-family:'Geist Mono',monospace;font-size:16px;color:#7a8399}
.bar{flex:1;height:3px;background:rgba(45,49,66,.10);position:relative}
.bar i{position:absolute;left:0;top:0;bottom:0;background:#eb6c36}
h1{font-family:'Instrument Serif',serif;font-weight:400;letter-spacing:-.02em}
.title h1{position:absolute;left:96px;right:96px;top:330px;font-size:112px;line-height:1.05}
.title .eb{position:absolute;left:96px;top:280px;font-family:'Geist Mono',monospace;font-size:22px;letter-spacing:.18em;
           text-transform:uppercase;color:#eb6c36}
.title .sub{position:absolute;left:96px;right:96px;top:600px;font-size:38px;color:#4f5d75}
.title .rule{position:absolute;left:96px;top:690px;width:160px;height:4px;background:#eb6c36}
.slide h1{position:absolute;left:96px;right:96px;top:110px;font-size:64px}
.diagram img{position:absolute;left:96px;top:240px;width:1728px;height:790px;object-fit:contain;object-position:top}
.diagram .cap{position:absolute;left:96px;right:96px;top:196px;font-family:'Instrument Serif',serif;font-style:italic;
              font-size:30px;color:#4f5d75}
ul{position:absolute;left:96px;right:96px;top:260px;list-style:none}
li{display:flex;gap:28px;align-items:flex-start;margin-bottom:44px;transition:none}
li .n{flex:none;width:56px;height:56px;border:1.5px solid #2d3142;border-radius:6px;display:flex;align-items:center;
      justify-content:center;font-family:'Geist Mono',monospace;font-size:24px}
li .t{font-size:40px;font-weight:600;line-height:1.2}
li .c{display:inline-block;margin-top:12px;font-family:'Geist Mono',monospace;font-size:27px;color:#4f5d75;
      background:#fff;border:1px solid rgba(45,49,66,.14);border-radius:6px;padding:6px 14px}
li.hidden{visibility:hidden}
li.now .n{border-color:#eb6c36;background:rgba(235,108,54,.08);color:#eb6c36}
li.done{opacity:.55}
.call{position:absolute;left:96px;right:96px;top:250px;padding:56px 64px;border-radius:8px;background:#fff;
      border:1.5px solid rgba(45,49,66,.16)}
.call.trap{border:1.5px dashed rgba(235,108,54,.6);background:rgba(235,108,54,.05)}
.call .k{font-family:'Geist Mono',monospace;font-size:20px;letter-spacing:.16em;text-transform:uppercase;color:#eb6c36;
         margin-bottom:28px}
.call.tip .k{color:#2e5aa8}
.call p{font-size:42px;line-height:1.35;font-weight:500}
.call code{display:block;margin-top:44px;font-family:'Geist Mono',monospace;font-size:28px;color:#2d3142;
           background:#f5f5f5;border:1px solid rgba(45,49,66,.12);border-radius:6px;padding:18px 22px;word-break:break-all}
"""


def esc(s):
    return html.escape(s or "")


def page(body, lesson_title, idx, total):
    pct = 100 * (idx + 1) / total
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><link href="{FONTS}" rel="stylesheet">
<style>{CSS}</style></head><body>
<div class="top"><span>Isaac Sim 6.1 · learning_resource</span><span>{esc(lesson_title)}</span></div>
{body}
<div class="foot"><span>{idx + 1:02d} / {total:02d}</span><div class="bar"><i style="width:{pct:.1f}%"></i></div></div>
</body></html>"""


def render(page_html, png):
    tmp = png + ".html"
    with open(tmp, "w") as f:
        f.write(page_html)
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
                    "--window-size=1920,1080", "--force-device-scale-factor=1.5", "--virtual-time-budget=8000",
                    f"--screenshot={png}", "file://" + tmp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(tmp)


def bullets_html(bullets, shown):
    items = []
    for i, (t, c) in enumerate(bullets):
        cls = "hidden" if i >= shown else ("now" if i == shown - 1 else "done")
        chip = f'<br><span class="c">{esc(c)}</span>' if c else ""
        items.append(f'<li class="{cls}"><span class="n">{i + 1}</span><span class="t">{esc(t)}{chip}</span></li>')
    return "<ul>" + "".join(items) + "</ul>"


def build(lid):
    les = LESSONS[lid]
    out = os.path.join(WORK, lid)
    os.makedirs(out, exist_ok=True)
    slides = les["slides"]
    plan = {"lesson": lid, "title": les["title"], "slides": []}
    for si, s in enumerate(slides):
        frames, segments = [], []
        if s["type"] == "title":
            body = (f'<div class="title"><div class="eb">{esc(s["eyebrow"])}</div><h1>{esc(s["title"])}</h1>'
                    f'<div class="sub">{esc(s["sub"])}</div><div class="rule"></div></div>')
            frames.append(page(body, les["title"], si, len(slides)))
            segments = [s["say"]]
        elif s["type"] == "diagram":
            img = "file://" + os.path.join(DIAG, s["img"] + ".png")
            body = (f'<div class="slide diagram"><h1>{esc(s["title"])}</h1><div class="cap">{esc(s["caption"])}</div>'
                    f'<img src="{img}"></div>')
            frames.append(page(body, les["title"], si, len(slides)))
            segments = [s["say"]]
        elif s["type"] == "steps":
            for k in range(len(s["bullets"]) + 1):
                body = f'<div class="slide"><h1>{esc(s["title"])}</h1>{bullets_html(s["bullets"], k)}</div>'
                frames.append(page(body, les["title"], si, len(slides)))
            segments = list(s["say"])
            assert len(segments) == len(frames), (lid, si)
        elif s["type"] == "callout":
            code = f'<code>{esc(s["code"])}</code>' if s.get("code") else ""
            label = "Watch out" if s["kind"] == "trap" else "Tip"
            body = (f'<div class="slide"><h1>{esc(s["title"])}</h1><div class="call {s["kind"]}">'
                    f'<div class="k">{label}</div><p>{esc(s["body"])}</p>{code}</div></div>')
            frames.append(page(body, les["title"], si, len(slides)))
            segments = [s["say"]]
        names = []
        for fi, ph in enumerate(frames):
            png = os.path.join(out, f"s{si:02d}_f{fi}.png")
            render(ph, png)
            names.append(os.path.basename(png))
        text = " ".join(segments)
        with open(os.path.join(out, f"s{si:02d}.txt"), "w") as f:
            f.write(text)
        plan["slides"].append({"frames": names, "segments": segments, "text": text})
    with open(os.path.join(out, "plan.json"), "w") as f:
        json.dump(plan, f, indent=1)
    print(f"{lid}: {len(slides)} slides, {sum(len(x['frames']) for x in plan['slides'])} frames, "
          f"{sum(len(x['text']) for x in plan['slides'])} chars")


if __name__ == "__main__":
    for lid in (sys.argv[1:] or LESSONS):
        build(lid)
