# blainemalone.com

A personal website made with HTML and CSS. No framework, external fonts, or package dependencies. The booking page uses the official Cal.com embed; the Videos page supports muted hover previews and click-to-play YouTube videos.

## Preview

From this directory:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open <http://127.0.0.1:8000>.

## Edit

Edit `index.html` for the homepage and `style.css` for the shared appearance. The writing archive lives in `writing/`, and the YouTube gallery lives in `videos/`. The shared text navigation links to Writing and Videos. The old `/podcasts/` address leads to `/videos/`. The homepage introduces Blaine’s focus on engineers in the age of AI with social icons in the footer, including X and YouTube. The old `/books/` address remains available for existing links, but is no longer linked from the homepage. The original article keeps its `/2017/08/30/twelve-expensive-words.html` address. `/blog/` leads to the writing archive.

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

## Videos and Shorts

`/videos/` has two sections matching the channel's public Videos and Shorts tabs, with the latest 30 entries from each. `scripts/youtube_hidden.json` lists individual videos excluded from the gallery; those exclusions apply on every refresh. The checked-in `videos/youtube.json` and generated HTML provide a working local snapshot. Titles also link directly to YouTube, including when JavaScript is unavailable. On desktop, hovering over a thumbnail immediately requests a muted preview with no intentional delay. The official YouTube IFrame API is prepared on desktop page load to reduce the first-hover wait; playback still depends on YouTube loading the video. Previews stop when the pointer leaves, the page is hidden, or the section switches to list view. Touch devices and reduced-motion preferences keep click-to-play. Clicking a thumbnail loads a privacy-enhanced YouTube embed with sound; an explicitly opened player takes priority over hover previews, and starting another restores the previous thumbnail. Each section has its own compact grid/list switch and remembers its choice independently in local browser storage. List view shows title links without thumbnails. Switching a section to list view stops its active player.

To refresh the snapshot from the public channel pages:

```sh
python3 scripts/update_youtube.py --refresh
```

To render existing data without fetching:

```sh
python3 scripts/update_youtube.py
```

GitHub Actions refreshes the public channel data before publishing, and runs every six hours after deployment. Scheduled runs update the published gallery without committing generated data to Git. This needs no API key or channel login. It reads YouTube's public page data, whose format can change; if either channel tab cannot be read, publication stops and the last successful site remains online. Check the failed workflow before updating the parser or rerunning it.

## Podcast bookings

`/schedule/` embeds the dedicated Cal.com event at <https://cal.com/cloaked/podcast>. A direct booking link appears if the calendar has not loaded after 12 seconds, and is also available when JavaScript is disabled. The Videos page links to the booking page. The page is omitted from the sitemap and asks search engines not to index it. Anyone with the URL can still access it.

Cal.com owns availability, conflict checks, confirmations, and guest information. The event adds bookings to `blaine@clkd.xyz` and checks that calendar for conflicts. It uses the existing Working hours schedule in America/New_York, reserves 90 minutes, requires 24 hours' notice, allows one booking per day, and offers a rolling 60-day window. Its meeting location is the existing Riverside guest link, included after booking and in the invitation. The studio link is not stored in this repository.

The event title is Podcast with Blaine Malone. The shared Cal.com profile remains Cloaked so existing business booking pages are unaffected; the embedded calendar hides that profile panel and the page provides its own introduction.

Edit the page introduction in `schedule/index.html`. Manage recording instructions, booking hours, and the Riverside link in the Cal.com event settings. `schedule/booking.js` is the official Cal.com embed bootstrap, isolated to this page. No calendar credentials or server are needed by the website.
