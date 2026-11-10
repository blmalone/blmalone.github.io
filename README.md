# blainemalone.com

A personal website made with HTML and CSS. No framework, external fonts, package dependencies, or build step. Only the booking page loads JavaScript, for the official Cal.com calendar embed.

## Preview

From this directory:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open <http://127.0.0.1:8000>.

## Edit

Edit `index.html` for the homepage and `style.css` for the shared appearance. The writing archive lives in `writing/`. The old `/books/` address remains available for existing links, but is no longer linked from the homepage. The original article keeps its `/2017/08/30/twelve-expensive-words.html` address. `/blog/` leads to the writing archive.

The writing archive contains the existing links and article content from the previous site. Theme samples and demo projects have been removed. The complete previous site remains in Git history.

The retired newsletter signup and confirmation pages have been removed. New writing links to Substack; historical newsletter issues remain in the writing archive.

Light and dark appearances follow the visitor's device preference. There is no theme switch or stored browser state.

After adding a page, add it to `sitemap.xml` and run:

```sh
python3 scripts/check_site.py
```

The check uses only Python's standard library. It validates internal links, anchors, page titles, canonical URLs, XML, and the custom domain.

## Publish on the existing domain

GitHub Pages uses **GitHub Actions** as its publishing source, with the custom domain set to `blainemalone.com`. These settings are in **Settings → Pages → Build and deployment**.

Pushes to `master` publish the checked static files with the GitHub Pages workflow. Pull requests run checks only. To retry a publication, run **Check and publish site** from the Actions tab on `master`.

The workflow packages only public site files, excluding this README and the checking script. `CNAME` retains the existing domain and `.nojekyll` disables Jekyll processing. No DNS or hosting provider change is needed.

## Podcast bookings

`/schedule/` embeds the dedicated Cal.com event at <https://cal.com/cloaked/podcast>, with a direct booking link as a fallback. The page is omitted from the homepage and sitemap and asks search engines not to index it. Anyone with the URL can still access it.

Cal.com owns availability, conflict checks, confirmations, and guest information. The event adds bookings to `blaine@clkd.xyz` and checks that calendar for conflicts. It uses the existing Working hours schedule in America/New_York, reserves 90 minutes, requires 24 hours' notice, allows one booking per day, and offers a rolling 60-day window. Its meeting location is the existing Riverside guest link, included after booking and in the invitation. The studio link is not stored in this repository.

The event title is Podcast with Blaine Malone. The shared Cal.com profile remains Cloaked so existing business booking pages are unaffected; the embedded calendar hides that profile panel and the page provides its own introduction.

Edit recording instructions in `schedule/index.html`. Manage booking hours and the Riverside link in the Cal.com event settings. `schedule/booking.js` is the official Cal.com embed bootstrap, isolated to this page. No calendar credentials or server are needed by the website.
