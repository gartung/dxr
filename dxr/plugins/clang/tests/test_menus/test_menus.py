"""Tests for contextual menu building

These integration tests guarantee that the compiler plugin is emitting the
right stuff and that that stuff makes it through the DXR clang plugin
unscathed.

"""
import cgi
import json
import re

from nose.tools import ok_

from dxr.testing import DxrInstanceTestCase


def menu_on(haystack, text, *menu_items):
    """Assert that there is a context menu on certain text that contains
    certain menu items.

    :arg text: The text contained by the menu's anchor tag. The first
        menu-having anchor tag containing the text is the one compared against.
    :arg menu_items: Dicts whose pairs must be contained in some item of the
        menu. If an item is found to match, it is discarded can cannot be
        reused to match another element of ``menu_items``.

    """
    def removed_match(expected, found_items):
        """Remove the first menu item from ``found_items`` where the keys in
        ``expected`` match it. If none is found, return False; else, True.

        :arg expected: Dict whose pairs are expected to be found in an item of
            ``found_items``
        :arg found_items: A list of dicts representing menu items actually on
            the page

        """
        def matches(expected, found):
            """Return whether all the pairs in ``expected`` are found in
            ``found``.

            """
            for k, v in expected.iteritems():
                if found.get(k) != v:
                    return False
            return True

        for i, found in enumerate(found_items):
            if matches(expected, found):
                del found_items[i]
                return True
        return False

    # We just use cheap-and-cheesy regexes for now, to avoid pulling in and
    # compiling the entirety of lxml to run pyquery.
    match = re.search(
            '<a data-menu="([^"]+)">' + re.escape(cgi.escape(text)) + '</a>',
            haystack)
    if match:
        found_items = json.loads(match.group(1).replace('&quot;', '"')
                                               .replace('&lt;', '<')
                                               .replace('&gt;', '>')
                                               .replace('&amp;', '&'))
        for expected in menu_items:
            removed = removed_match(expected, found_items)
            if not removed:
                ok_(False, "No menu item with the keys %r was found in the menu around '%s'." % (expected, text))
    else:
        ok_(False, "No menu around '%s' was found." % text)


class MenuTests(DxrInstanceTestCase):
    def main_page(self):
        return self.client().get('/code/source/main.cpp').data

    def test_includes(self):
        """Make sure #include cross references are linked."""
        menu_on(self.main_page(),
                '"extern.c"',
                {'href': '/code/source/extern.c'})

    def test_functions(self):
        """Make sure definitions are found and a representative qualname-using
        search is properly constructed."""
        menu_on(self.main_page(),
                'another_file',
                {'html': 'Jump to definition',
                 'href': '/code/source/extern.c#1'},
                {'html': 'Find callers',
                 'href': '/code/search?q=%2Bcallers%3Aanother_file%28%29'})

    def test_variables(self):
        """Make sure definitions are found and a representative qualname-using
        search is properly constructed."""
        menu_on(self.main_page(),
                'var',
                {'html': 'Jump to definition',
                 'href': '/code/source/extern.c#5'},
                {'html': 'Find declarations',
                 'href': '/code/search?q=%2Bvar-decl%3Avar'})