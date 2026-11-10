"""Check static pages with Python's standard library; no packages to install."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = 'https://blainemalone.com'
errors = []


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.links = []
        self.scripts = []
        self.ids = set()
        self.canonical = None
        self.has_title = False
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if tag == 'title':
            self.in_title = True
        if tag == 'script':
            self.scripts.append(attrs.get('src'))
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                errors.append(f'Duplicate id: {attrs["id"]}')
            self.ids.add(attrs['id'])
        for attr in ('href', 'src'):
            if attr in attrs:
                self.links.append(attrs[attr])
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs.get('href')

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and data.strip():
            self.has_title = True


def local_file(url, source):
    path = unquote(urlsplit(url).path)
    target = ROOT / path.lstrip('/') if path.startswith('/') else source.parent / path
    if not path:
        target = source
    elif target.is_dir():
        target /= 'index.html'
    return target.resolve()


pages = {}
for path in sorted(ROOT.rglob('*.html')):
    if '.git' in path.parts or '_site' in path.parts:
        continue
    page = Page()
    page.feed(path.read_text())
    pages[path.resolve()] = page
    if not page.has_title or 'main' not in page.tags:
        errors.append(f'{path.relative_to(ROOT)}: missing title or main content')
    expected_scripts = ['/schedule/booking.js'] if path.relative_to(ROOT).as_posix() == 'schedule/index.html' else []
    if page.scripts != expected_scripts:
        errors.append(f'{path.relative_to(ROOT)}: unexpected JavaScript')
    if not page.canonical or not page.canonical.startswith(ORIGIN + '/'):
        errors.append(f'{path.relative_to(ROOT)}: missing or incorrect canonical URL')

for source, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = local_file(link, source)
        if not target.is_relative_to(ROOT) or not target.is_file():
            errors.append(f'{source.relative_to(ROOT)}: broken link {link}')
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f'{source.relative_to(ROOT)}: missing anchor {link}')

for xml_file in ('sitemap.xml', 'feed.xml', 'favicon.svg'):
    ET.parse(ROOT / xml_file)

sitemap = ET.parse(ROOT / 'sitemap.xml')
for location in sitemap.findall('.//{*}loc'):
    if not location.text.startswith(ORIGIN + '/') or not local_file(location.text, ROOT / 'index.html').is_file():
        errors.append(f'Invalid sitemap location: {location.text}')

for item in ET.parse(ROOT / 'feed.xml').findall('.//item/link'):
    if not local_file(item.text, ROOT / 'index.html').is_file():
        errors.append(f'Broken feed item: {item.text}')

if (ROOT / 'CNAME').read_text().strip() != 'blainemalone.com':
    errors.append('Custom domain changed')
if not (ROOT / '.nojekyll').is_file():
    errors.append('Missing .nojekyll')
if not pages:
    errors.append('No HTML pages found')

if errors:
    raise SystemExit('\n'.join(errors))
print(f'Checked {len(pages)} pages: internal links, anchors, metadata, XML, and custom domain are valid.')
