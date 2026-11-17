import json
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

import update_youtube
from update_youtube import CHANNEL_ID, parse_tab, render_card


def channel_page(section, cards, channel_id=CHANNEL_ID):
    data = {
        'metadata': {'channelMetadataRenderer': {'externalId': channel_id}},
        'contents': {'tabs': [{'tabRenderer': {
            'title': section.title(), 'selected': True, 'content': cards,
        }}]},
    }
    return '<script>var ytInitialData = ' + json.dumps(data) + ';</script>'


class YouTubeFeedTests(unittest.TestCase):
    def test_refresh_never_restores_hidden_videos(self):
        keep = {'id': 'dtsOkGZV9xw', 'title': 'Keep this video',
                'thumbnail': 'https://i.ytimg.com/vi/dtsOkGZV9xw/hqdefault.jpg'}
        hidden = {**keep, 'id': 'Xtl6pZgjp-E', 'title': 'Hidden older video'}
        short = {**keep, 'id': '9RTtBa6VWRI', 'title': 'Keep this Short'}
        with TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / 'index.html'
            data = root / 'youtube.json'
            exclusions = root / 'hidden.json'
            page.write_text(update_youtube.START + update_youtube.END)
            exclusions.write_text(json.dumps({hidden['id']: hidden['title']}))
            with patch.object(update_youtube, 'PAGE_FILE', page), \
                 patch.object(update_youtube, 'DATA_FILE', data), \
                 patch.object(update_youtube, 'HIDDEN_FILE', exclusions), \
                 patch.object(update_youtube, 'fetch_tab', side_effect=lambda section: [keep, hidden] if section == 'videos' else [short]), \
                 patch('sys.argv', ['update_youtube.py', '--refresh']):
                update_youtube.main()
            rendered = page.read_text()
            self.assertNotIn(hidden['id'], rendered)
            self.assertIn(keep['id'], rendered)
            self.assertIn(short['id'], rendered)
            self.assertEqual(len(json.loads(data.read_text())['videos']), 2)

    def test_video_tab_keeps_order_and_deduplicates(self):
        card = {'lockupViewModel': {
            'contentType': 'LOCKUP_CONTENT_TYPE_VIDEO', 'contentId': 'dtsOkGZV9xw',
            'metadata': {'lockupMetadataViewModel': {'title': {'content': 'An engineering story'}}},
            'contentImage': {'thumbnailViewModel': {'image': {'sources': [
                {'url': 'https://i.ytimg.com/vi/dtsOkGZV9xw/hqdefault.jpg'},
            ]}}},
        }}
        result = parse_tab(channel_page('videos', [card, card]), 'videos')
        self.assertEqual([item['id'] for item in result], ['dtsOkGZV9xw'])
        self.assertEqual(result[0]['title'], 'An engineering story')

    def test_shorts_use_the_channel_grouping_and_portrait_thumbnail(self):
        card = {'shortsLockupViewModel': {
            'onTap': {'innertubeCommand': {'reelWatchEndpoint': {'videoId': '9RTtBa6VWRI'}}},
            'overlayMetadata': {'primaryText': {'content': 'The Modern Software Engineer'}},
            'thumbnailViewModel': {'thumbnailViewModel': {'image': {'sources': [
                {'url': 'https://i.ytimg.com/vi/9RTtBa6VWRI/oar3.jpg'},
            ]}}},
        }}
        result = parse_tab(channel_page('shorts', [card]), 'shorts')
        self.assertEqual(result[0]['id'], '9RTtBa6VWRI')
        self.assertTrue(result[0]['thumbnail'].endswith('oar3.jpg'))

    def test_unexpected_channel_and_blocked_or_empty_pages_fail(self):
        pages = [
            'Please sign in',
            channel_page('videos', [], channel_id='another-channel'),
            channel_page('shorts', []),
            channel_page('videos', []),
        ]
        for page in pages:
            with self.subTest(page=page), self.assertRaises(ValueError):
                parse_tab(page, 'videos')

    def test_titles_are_escaped_and_links_stay_on_youtube(self):
        item = {'id': 'dtsOkGZV9xw', 'title': '<script>"hello"</script>',
                'thumbnail': 'https://i.ytimg.com/vi/dtsOkGZV9xw/hqdefault.jpg'}
        rendered = render_card(item, 'videos')
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;&quot;hello&quot;', rendered)
        self.assertIn('https://www.youtube.com/watch?v=dtsOkGZV9xw', rendered)
        with self.assertRaises(ValueError):
            render_card({**item, 'id': 'bad-id'}, 'videos')
        with self.assertRaises(ValueError):
            render_card({**item, 'thumbnail': 'https://example.com/track.jpg'}, 'videos')


if __name__ == '__main__':
    unittest.main()
