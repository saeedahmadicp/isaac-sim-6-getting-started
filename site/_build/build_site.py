"""Build the local HTML tutorial site from the learning_resource Markdown, videos, diagrams and scripts.

    uv run --with markdown --with pygments python3 learning_resource/site/_build/build_site.py

Output: learning_resource/site/*.html (+ site/static/). Serve learning_resource/ with serve.py and open
http://127.0.0.1:8765/site/
"""

import html
import json
import os
import re
import shutil

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ROOT = os.path.dirname(SITE)  # learning_resource

# ------------------------------------------------------------------ page plan (order = reading order)
NAV = [
    ("Start", [
        ("index", "README.md", "Course home"),
        ("whats-different", "00_whats_different_in_6.1.md", "What changed in 6.1"),
        ("setup-ros2", "01_setup_ros2_jazzy.md", "Set up ROS 2 Jazzy"),
    ]),
    ("Module 1 · First robot", [
        ("m1", "module1_first_robot/README.md", "Module 1 project"),
        ("m1-1", "module1_first_robot/lesson1_building_a_simple_robot.md", "1.1 Building a simple robot"),
        ("m1-2", "module1_first_robot/lesson2_controlling_the_robot.md", "1.2 Controlling the robot"),
        ("m1-3", "module1_first_robot/lesson3_adding_sensors.md", "1.3 Adding sensors"),
        ("m1-4", "module1_first_robot/lesson4_ros2_and_rviz.md", "1.4 ROS 2 and RViz"),
    ]),
    ("Module 2 · URDF & Carter", [
        ("m2", "module2_urdf_carter/README.md", "Module 2 project"),
        ("m2-1", "module2_urdf_carter/lesson1_importing_urdf.md", "2.1 Importing URDF"),
        ("m2-2", "module2_urdf_carter/lesson2_preparing_the_simulation.md", "2.2 Preparing the simulation"),
        ("m2-3", "module2_urdf_carter/lesson3_adding_sensors.md", "2.3 Adding sensors"),
        ("m2-4", "module2_urdf_carter/lesson4_nova_carter.md", "2.4 Nova Carter"),
    ]),
    ("Module 3 · Synthetic data", [
        ("m3", "module3_sdg/README.md", "Module 3 project"),
        ("m3-1", "module3_sdg/lesson1_generate_dataset.md", "3 Generate a dataset"),
    ]),
    ("Module 4 · Software-in-the-loop", [
        ("m4", "module4_sil/README.md", "Module 4 project"),
        ("m4-1", "module4_sil/lesson1_omnigraph_cmd_vel.md", "4.1 Driving from /cmd_vel"),
        ("m4-2", "module4_sil/lesson2_python_scripting.md", "4.2 Python scripting"),
        ("m4-3", "module4_sil/lesson3_isaac_ros_segmentation.md", "4.3 Camera images for Isaac ROS"),
    ]),
    ("Module 5 · Hardware-in-the-loop", [
        ("m5", "module5_hil/README.md", "5 Hardware-in-the-loop"),
    ]),
    ("Materials", [
        ("videos", None, "All videos"),
        ("diagrams", None, "All diagrams"),
        ("scripts", None, "Checkpoint scripts"),
    ]),
]
LESSON_SLUGS = {s for _, items in NAV for s, src, _ in items if src and "lesson" in src}
PAGES = [(s, src, t) for _, items in NAV for s, src, t in items]
SRC_TO_SLUG = {os.path.normpath(os.path.join(ROOT, src)): s for s, src, _ in PAGES if src}
SCRIPTS_DIR = os.path.join(ROOT, "scripts")


def rel_from_site(abs_path):
    return os.path.relpath(abs_path, SITE).replace(os.sep, "/")


def rewrite_links(body, src_dir):
    """Make every relative href/src in a converted page valid from site/."""

    def fix(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^(https?:|mailto:|#|data:)", url):
            return m.group(0)
        path, _, frag = url.partition("#")
        target = os.path.normpath(os.path.join(src_dir, path))
        if target in SRC_TO_SLUG:
            new = SRC_TO_SLUG[target] + ".html" + ("#" + frag if frag else "")
        elif target.startswith(SCRIPTS_DIR) and target.endswith(".py"):
            new = "scripts.html#" + os.path.basename(target)
        elif os.path.isdir(target) and os.path.normpath(target) == SCRIPTS_DIR:
            new = "scripts.html"
        elif os.path.isdir(target) and os.path.normpath(target) == os.path.join(ROOT, "diagrams"):
            new = "diagrams.html"
        elif os.path.isdir(target) and os.path.normpath(target) == os.path.join(ROOT, "videos"):
            new = "videos.html"
        elif os.path.exists(target):
            new = rel_from_site(target)
        else:
            return m.group(0)
        return f'{attr}="{html.escape(new)}"'

    return re.sub(r'(href|src)="([^"]+)"', fix, body)


def enhance(body):
    # 1. "🎬 Video walkthrough" paragraph → embedded player. Python-Markdown may have merged it into a
    #    preceding blockquote (blank-line separated '>' blocks join), so pull it out of any blockquote.
    def player(par):
        v = re.search(r'href="([^"]+\.mp4)"', par)
        srt = re.search(r'href="([^"]+\.srt)"', par)
        t = re.search(r"Time:</strong>\s*([^<]+)", par)
        extra = []
        if t:
            extra.append(f"lesson ⏱ {html.escape(t.group(1).strip())}")
        if srt:
            extra.append(f'<a href="{srt.group(1)}">caption text (.srt)</a>')
        extra.append(f'<a href="{v.group(1)}" download>download .mp4</a>')
        return (f'<figure class="video"><video controls preload="metadata" src="{v.group(1)}"></video>'
                f'<figcaption>🎬 Narrated walkthrough · {" · ".join(extra)}</figcaption></figure>')

    def unquote(m):
        inner = m.group(1)
        vp = re.search(r"<p>🎬.*?</p>", inner, re.S)
        if not vp:
            return m.group(0)
        rest = (inner[:vp.start()] + inner[vp.end():]).strip()
        quote = f"<blockquote>\n{rest}\n</blockquote>" if rest else ""
        return quote + player(vp.group(0))

    body = re.sub(r"<blockquote>(.*?)</blockquote>", unquote, body, flags=re.S)
    # 2. diagram image + caption (same or next paragraph) → figure with zoom link
    body = re.sub(
        r'<p><img alt="([^"]*)" src="([^"]+\.png)" ?/?>\s*(?:</p>\s*<p>)?<em>(.*?)</em></p>',
        lambda m: (f'<figure class="diagram"><a href="{m.group(2)}" target="_blank" title="open full size">'
                   f'<img alt="{m.group(1)}" src="{m.group(2)}" loading="lazy"></a>'
                   f'<figcaption>{m.group(3)}</figcaption></figure>'),
        body, flags=re.S)
    # 3. remaining standalone images
    body = re.sub(r'<p><img alt="([^"]*)" src="([^"]+)" ?/?></p>',
                  r'<figure class="diagram"><a href="\2" target="_blank"><img alt="\1" src="\2" loading="lazy"></a></figure>',
                  body)
    # 4. 🔄 / ⚠️ callouts
    body = body.replace("<blockquote>", '<blockquote class="note">')
    body = re.sub(r'<blockquote class="note">(\s*<p>(?:<strong>)?⚠️)', r'<blockquote class="warn">\1', body)
    body = re.sub(r'<blockquote class="note">(\s*<p>🔄)', r'<blockquote class="change">\1', body)
    # 5. wide tables scroll
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return body


def md_to_html(text):
    md = markdown.Markdown(
        extensions=["fenced_code", "codehilite", "tables", "toc", "sane_lists", "md_in_html", "attr_list"],
        extension_configs={"codehilite": {"guess_lang": False, "css_class": "hl"},
                           "toc": {"permalink": "#", "toc_depth": "2-3"}},
    )
    body = md.convert(text)
    return body, md.toc_tokens


def strip_markers(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # let Markdown inside multi-line <details> blocks render (md_in_html needs markdown="1")
    text = re.sub(r"^(\s*)<details>(\s*)$", r'\1<details markdown="1">\2', text, flags=re.M)
    # <details><summary>…</summary> followed by Markdown on the next lines (not one-line quiz answers)
    return re.sub(r"^(\s*)<details>(<summary>.*?</summary>)\s*$", r'\1<details markdown="1">\n\1\2\n', text, flags=re.M)


# ------------------------------------------------------------------ chrome
def sidebar(active):
    out = ['<nav class="side" id="side"><a class="brand" href="index.html"><span>Isaac Sim 6.1</span>'
           '<small>Getting Started · learning path</small></a>',
           '<div class="search"><input id="q" type="search" placeholder="Search lessons…  ( / )" autocomplete="off">'
           '<div id="results"></div></div>',
           '<div class="progress"><div class="bar"><i id="pbar"></i></div><span id="ptext"></span></div>']
    for group, items in NAV:
        out.append(f'<p class="grp">{html.escape(group)}</p><ul>')
        for slug, src, title in items:
            cls = ' class="on"' if slug == active else ""
            tick = '<b class="tick" data-slug="%s"></b>' % slug if slug in LESSON_SLUGS else ""
            out.append(f'<li><a{cls} href="{slug}.html">{tick}{html.escape(title)}</a></li>')
        out.append("</ul>")
    out.append('<p class="grp">Project</p><ul><li><a href="https://github.com/saeedahmadicp/isaac-sim-6-getting-started" '
               'target="_blank" rel="noopener">View on GitHub ↗</a></li></ul>')
    out.append("</nav>")
    return "\n".join(out)


def toc_html(tokens):
    if not tokens:
        return ""
    items = []

    def walk(ts, depth):
        for t in ts:
            if t["level"] <= 3:
                items.append(f'<li class="l{t["level"]}"><a href="#{t["id"]}">{html.escape(t["name"])}</a></li>')
            walk(t["children"], depth + 1)

    walk(tokens, 0)
    if len(items) < 3:
        return ""
    return '<aside class="toc"><p>On this page</p><ul>' + "".join(items) + "</ul></aside>"


def page(slug, title, body, toc="", lesson=False):
    idx = [s for s, _, _ in PAGES].index(slug)
    prev_ = PAGES[idx - 1] if idx > 0 else None
    next_ = PAGES[idx + 1] if idx + 1 < len(PAGES) else None
    pn = '<div class="pn">'
    pn += (f'<a class="prev" href="{prev_[0]}.html"><small>Previous</small>{html.escape(prev_[2])}</a>'
           if prev_ else "<span></span>")
    pn += (f'<a class="next" href="{next_[0]}.html"><small>Next</small>{html.escape(next_[2])}</a>'
           if next_ else "<span></span>")
    pn += "</div>"
    done = (f'<label class="done"><input type="checkbox" data-slug="{slug}"> Mark this lesson as done</label>'
            if lesson else "")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · Isaac Sim 6.1 tutorial</title>
<link rel="icon" href="static/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="static/site.css"><link rel="stylesheet" href="static/code.css">
</head><body data-slug="{slug}">
<button class="menu" onclick="document.body.classList.toggle('nav-open')" aria-label="Menu">☰</button>
{sidebar(slug)}
<main><article>{body}{done}{pn}</article>{toc}</main>
<script src="static/site.js"></script>
</body></html>"""


# ------------------------------------------------------------------ special pages
def videos_page():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "videos", "_build"))
    from content import LESSONS  # noqa

    cards = []
    for lid, les in LESSONS.items():
        cards.append(f'<div class="card"><video controls preload="metadata" src="../videos/{lid}.mp4"></video>'
                     f'<p>{html.escape(les["title"])}</p></div>')
    return ('<h1>All videos</h1><p class="lead">14 narrated walkthroughs (slides, diagrams and captions; '
            'ElevenLabs voice). Each lesson page embeds its own video at the top.</p>'
            f'<div class="grid">{"".join(cards)}</div>')


def diagrams_page():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "diagrams", "_build"))
    import build_diagrams as b  # noqa

    cards = []
    for d in b.D:
        cards.append(f'<div class="card"><a href="../diagrams/{d.slug}.html" target="_blank">'
                     f'<img src="../diagrams/{d.slug}.png" alt="{html.escape(d.title)}" loading="lazy"></a>'
                     f'<p><b>{html.escape(d.title)}</b><br><span>{html.escape(d.desc)}</span></p></div>')
    return ('<h1>All diagrams</h1><p class="lead">Click a diagram to open its interactive, zoomable HTML version.</p>'
            f'<div class="grid wide">{"".join(cards)}</div>')


def scripts_page():
    fmt = HtmlFormatter(cssclass="hl", linenos="table")
    secs = ['<h1>Checkpoint scripts</h1><p class="lead">Run from the Isaac Sim root folder. The lesson checkpoint scripts support '
            '<code>--headless --test</code> and print PASS/FAIL. Run snippets through <code>m4_run_snippet.py</code> '
            'or <b>Window &gt; Script Editor</b>. Capture helpers have their own usage instructions below.</p>',
            '<pre class="cmd"><code>cd ~/isaacsim   # your Isaac Sim installation folder\n'
            './python.sh learning_resource/scripts/&lt;script&gt;.py --headless --test</code></pre>']
    for f in sorted(os.listdir(SCRIPTS_DIR)):
        if not f.endswith(".py"):
            continue
        code = open(os.path.join(SCRIPTS_DIR, f)).read()
        doc = re.match(r'\s*"""(.*?)"""', code, re.S)
        first = doc.group(1).strip().splitlines()[0] if doc else (code.splitlines()[0].lstrip("# "))
        secs.append(f'<section class="script" id="{f}"><h2>{f}</h2><p>{html.escape(first)}</p>'
                    f'<div class="code-actions"><a href="../scripts/{f}" download>download</a></div>'
                    f'{highlight(code, PythonLexer(), fmt)}</section>')
    return "\n".join(secs)


# ------------------------------------------------------------------ build
def build():
    os.makedirs(os.path.join(SITE, "static"), exist_ok=True)
    for f in os.listdir(os.path.join(HERE, "static")):
        shutil.copy(os.path.join(HERE, "static", f), os.path.join(SITE, "static", f))
    with open(os.path.join(SITE, "static", "code.css"), "w") as f:
        f.write(HtmlFormatter(style="friendly").get_style_defs(".hl"))
        f.write("\n@media (prefers-color-scheme: dark){"
                + HtmlFormatter(style="monokai").get_style_defs(":root:not(.light) .hl").replace("\n", "") + "}")

    index = []
    for slug, src, title in PAGES:
        toc = ""
        if src:
            path = os.path.join(ROOT, src)
            text = strip_markers(open(path).read())
            body, tokens = md_to_html(text)
            body = enhance(rewrite_links(body, os.path.dirname(path)))
            toc = toc_html(tokens)
            plain = re.sub(r"<[^>]+>", " ", body)
        else:
            body = {"videos": videos_page, "diagrams": diagrams_page, "scripts": scripts_page}[slug]()
            plain = re.sub(r"<[^>]+>", " ", body)
        if slug == "index":
            body = body.replace('<h1 ', '<h1 class="big" ', 1)
        html_out = page(slug, title, body, toc, lesson=slug in LESSON_SLUGS)
        with open(os.path.join(SITE, f"{slug}.html"), "w") as f:
            f.write(html_out)
        index.append({"slug": slug, "title": title, "text": " ".join(plain.split())[:20000]})
    with open(os.path.join(SITE, "static", "search-index.json"), "w") as f:
        json.dump({"pages": index, "lessons": sorted(LESSON_SLUGS)}, f)
    print(f"built {len(PAGES)} pages into {SITE}")


if __name__ == "__main__":
    build()
