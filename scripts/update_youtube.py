"""Refresh the static video gallery from the channel's public Videos and Shorts tabs.

No API keys or visitor-side requests are needed. If YouTube cannot be read, the
refresh fails before writing anything, so the last successful page stays online.
"""
import argparse
import html
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
CHANNEL_ID = 'UCzHl1XlhwIwvYIlV_J5tD1Q'
CHANNEL_URL = 'https://www.youtube.com/@blaine.malone'
DATA_FILE = ROOT / 'videos' / 'youtube.json'
PAGE_FILE = ROOT / 'videos' / 'index.html'
HIDDEN_FILE = ROOT / 'scripts' / 'youtube_hidden.json'
START = '<!-- youtube-gallery:start -->'
END = '<!-- youtube-gallery:end -->'
VIDEO_ID = re.compile(r'[A-Za-z0-9_-]{11}')


def walk(value, key):
    if isinstance(value, dict):
        if key in value:
            yield value[key]
        for child in value.values():
            yield from walk(child, key)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child, key)


def text(value):
    return value.get('content') or value.get('simpleText') or ''.join(
        run.get('text', '') for run in value.get('runs', [])
    )


def thumbnail(sources):
    usable = [source for source in sources if (
        urlsplit(source.get('url', '')).scheme == 'https'
        and urlsplit(source['url']).hostname == 'i.ytimg.com'
    )]
    if not usable:
        raise ValueError('Missing YouTube thumbnail')
    return max(usable, key=lambda source: source.get('width', 0) * source.get('height', 0))['url']


def parse_tab(page, section):
    match = re.search(r'(?:var\s+)?ytInitialData\s*=\s*', page)
    if not match:
        raise ValueError('YouTube did not return channel data')
    data, _ = json.JSONDecoder().raw_decode(page[match.end():])
    metadata = next(walk(data, 'channelMetadataRenderer'), {})
    if metadata.get('externalId') != CHANNEL_ID:
        raise ValueError('Unexpected YouTube channel')
    selected = next((tab for tab in walk(data.get('contents', {}), 'tabRenderer')
                     if tab.get('selected') and tab.get('title', '').lower() == section), None)
    if selected is None:
        raise ValueError(f'Missing selected {section} tab')
    content = selected.get('content', {})
    items = []
    if section == 'videos':
        for video in walk(content, 'lockupViewModel'):
            if video.get('contentType') != 'LOCKUP_CONTENT_TYPE_VIDEO':
                continue
            title = text(video.get('metadata', {}).get('lockupMetadataViewModel', {}).get('title', {}))
            image = video.get('contentImage', {}).get('thumbnailViewModel', {})
            items.append({'id': video.get('contentId'), 'title': title,
                          'thumbnail': thumbnail(image.get('image', {}).get('sources', []))})
        for video in walk(content, 'videoRenderer'):
            items.append({'id': video.get('videoId'), 'title': text(video.get('title', {})),
                          'thumbnail': thumbnail(video.get('thumbnail', {}).get('thumbnails', []))})
    else:
        for video in walk(content, 'shortsLockupViewModel'):
            endpoint = video.get('onTap', {}).get('innertubeCommand', {}).get('reelWatchEndpoint', {})
            image = video.get('thumbnailViewModel', {})
            image = image.get('thumbnailViewModel', image).get('image', {})
            items.append({'id': endpoint.get('videoId'),
                          'title': text(video.get('overlayMetadata', {}).get('primaryText', {})),
                          'thumbnail': thumbnail(image.get('sources', []))})
        for video in walk(content, 'reelItemRenderer'):
            items.append({'id': video.get('videoId'), 'title': text(video.get('headline', {})),
                          'thumbnail': thumbnail(video.get('thumbnail', {}).get('thumbnails', []))})
    unique = {}
    for item in items:
        if not VIDEO_ID.fullmatch(item.get('id') or '') or not item['title'].strip():
            raise ValueError(f'Invalid {section} entry')
        unique.setdefault(item['id'], item)
    if not unique:
        raise ValueError(f'No {section} found; keeping the existing gallery')
    return list(unique.values())[:30]


def fetch_tab(section):
    request = Request(f'{CHANNEL_URL}/{section}?hl=en', headers={
        'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US,en;q=0.9',
    })
    with urlopen(request, timeout=30) as response:
        return parse_tab(response.read().decode('utf-8'), section)


def render_card(item, section):
    video_id = item['id']
    if not VIDEO_ID.fullmatch(video_id):
        raise ValueError('Invalid video ID in gallery data')
    title = html.escape(item['title'], quote=True)
    image = html.escape(thumbnail([{'url': item['thumbnail']}]), quote=True)
    url = f'https://www.youtube.com/{"shorts/" if section == "shorts" else "watch?v="}{video_id}'
    height = 854 if section == 'shorts' else 270
    return f'''        <li class="video-card">
          <a class="video-preview video-media" href="{url}" data-video-id="{video_id}" aria-label="Play {title}">
            <img src="{image}" alt="" width="480" height="{height}" loading="lazy" decoding="async">
            <span class="video-play" aria-hidden="true">▶</span>
          </a>
          <p class="video-title"><a href="{url}">{title}</a></p>
        </li>'''


def filter_hidden(data, hidden_ids):
    return {**data, **{
        section: [item for item in data[section] if item['id'] not in hidden_ids]
        for section in ['videos', 'shorts']
    }}


def render_gallery(data):
    sections = []
    for section in ['videos', 'shorts']:
        heading_tag = 'h1' if section == 'videos' else 'h2'
        label = section.title()
        cards = '\n'.join(render_card(item, section) for item in data[section])
        sections.append(f'''    <section class="video-section" data-video-section="{section}" aria-labelledby="{section}-heading">
      <div class="videos-heading">
        <{heading_tag} id="{section}-heading">{label}</{heading_tag}>
        <div class="view-switch" role="group" aria-label="{label} layout" hidden>
          <button type="button" data-video-view="grid" aria-label="Grid view" aria-pressed="true" aria-controls="{section}-grid" title="Grid view">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true" focusable="false">
              <rect x="3" y="3" width="7" height="7" rx="1.3"/><rect x="14" y="3" width="7" height="7" rx="1.3"/><rect x="3" y="14" width="7" height="7" rx="1.3"/><rect x="14" y="14" width="7" height="7" rx="1.3"/>
            </svg>
          </button>
          <button type="button" data-video-view="list" aria-label="List view" aria-pressed="false" aria-controls="{section}-grid" title="List view">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true" focusable="false">
              <path d="M9 5h12M9 12h12M9 19h12"/><circle cx="3.5" cy="5" r="1" fill="currentColor" stroke="none"/><circle cx="3.5" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="3.5" cy="19" r="1" fill="currentColor" stroke="none"/>
            </svg>
          </button>
        </div>
      </div>
      <ul id="{section}-grid" class="video-grid {section}-grid" aria-label="{label}">
{cards}
      </ul>
    </section>''')
    return '\n'.join(sections)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Fetch the latest public channel tabs')
    args = parser.parse_args()
    if args.refresh:
        with ThreadPoolExecutor(max_workers=2) as pool:
            videos, shorts = pool.map(fetch_tab, ['videos', 'shorts'])
        data = {'channel_id': CHANNEL_ID, 'videos': videos, 'shorts': shorts}
    else:
        data = json.loads(DATA_FILE.read_text())
    hidden_ids = json.loads(HIDDEN_FILE.read_text())
    if not all(VIDEO_ID.fullmatch(video_id) for video_id in hidden_ids):
        raise ValueError('Invalid ID in the hidden-video list')
    visible = filter_hidden(data, hidden_ids)
    gallery = render_gallery(visible)
    page = PAGE_FILE.read_text()
    if page.count(START) != 1 or page.count(END) != 1:
        raise ValueError('Gallery markers are missing or duplicated')
    before, rest = page.split(START)
    _, after = rest.split(END)
    updated = before + START + '\n' + gallery + '\n    ' + END + after
    if args.refresh:
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    PAGE_FILE.write_text(updated)
    print(f'Gallery: {len(visible["videos"])} videos and {len(visible["shorts"])} Shorts')


if __name__ == '__main__':
    main()
