# Tutorial website

A browsable HTML version of the whole course: every lesson with its narrated video embedded, diagrams,
concepts, steps, checks, exercises and quizzes; galleries of all videos and diagrams; syntax-highlighted
checkpoint scripts; search (press `/`); lesson progress saved in your browser.

The site is plain static HTML. Pages live in `site/` and load media from the sibling `videos/`,
`diagrams/`, `screenshots/` and `scripts/` folders, so always serve the **whole course folder**,
not just `site/`.

## Open it locally

From the course folder (`learning_resource/`, or the repository root if you cloned it on its own):

```bash
python3 site/serve.py            # then open http://127.0.0.1:8765/site/
```

`serve.py` supports HTTP range requests, so you can seek in the videos. Options: `--port 9000`,
`--host 0.0.0.0` (reachable from other machines on your network).

Keep it running in the background:

```bash
setsid nohup python3 site/serve.py > site/serve.log 2>&1 &
pkill -f site/serve.py           # stop it
```

## Publish on GitHub Pages

Publishing is automated by [`.github/workflows/deploy-pages.yml`](../.github/workflows/deploy-pages.yml):
every push to `main` rebuilds the HTML from the Markdown, fails if any link or anchor is broken
(`tools/check_site.py`), and deploys the site, videos, diagrams, screenshots and scripts.

One-time setup for [github.com/saeedahmadicp/isaac-sim-6-getting-started](https://github.com/saeedahmadicp/isaac-sim-6-getting-started):

1. Push this folder as the repository root.
2. On GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Open the **Actions** tab and wait for *Deploy site to GitHub Pages* to finish (re-run it from
   there with **Run workflow** if it ran before step 2).

The course is then live at <https://saeedahmadicp.github.io/isaac-sim-6-getting-started/>.
All links are relative, so the site works under any sub-path; each video is 4–12 MB, well within
GitHub's 100 MB file limit.

## Rebuild after editing a lesson

The Markdown lessons are the source of truth; regenerate the HTML after any edit:

```bash
uv run --no-project --with markdown --with pygments python3 site/_build/build_site.py
# or: pip install -r site/requirements.txt && python3 site/_build/build_site.py
python3 tools/check_site.py     # same link check the deploy workflow runs
```

The builder lives in `_build/build_site.py` (navigation order is the `NAV` list at the top); styles and
scripts are in `_build/static/`.
