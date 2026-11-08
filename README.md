# blainemalone.com

A personal website made with HTML and CSS. No framework, JavaScript, external fonts, dependencies, or build step.

## Preview

From this directory:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open <http://127.0.0.1:8000>.

## Edit

Edit `index.html` for the homepage and `style.css` for the shared appearance. The other pages live in `writing/`, `books/`, `newsletter/`, and `thankyou/`. The original article keeps its `/2017/08/30/twelve-expensive-words.html` address. `/blog/` leads to the writing archive.

The writing archive contains the existing links and article content from the previous site. Theme samples and demo projects have been removed. The complete previous site remains in Git history.

Newsletter signup links to the existing hosted Kit form, so the site doesn't load a third-party subscription script. New writing links to Substack.

Light and dark appearances follow the visitor's device preference. There is no theme switch or stored browser state.

After adding a page, add it to `sitemap.xml` and run:

```sh
python3 scripts/check_site.py
```

The check uses only Python's standard library. It validates internal links, anchors, page titles, canonical URLs, XML, and the custom domain.

## Publish on the existing domain

**One-time migration:** in the repository's **Settings → Pages → Build and deployment → Source**, select **GitHub Actions** instead of the old `gh-pages` branch. Keep the custom domain set to `blainemalone.com`. Make this change when the redesign is ready to go live; it isn't needed for local preview or pull request checks.

After that, pushes to `master` publish the checked static files with the GitHub Pages workflow. Pull requests run checks only. To retry a publication, run **Check and publish site** from the Actions tab on `master`.

The workflow packages only public site files, excluding this README and the checking script. `CNAME` retains the existing domain and `.nojekyll` disables Jekyll processing. No DNS or hosting provider change is needed.
