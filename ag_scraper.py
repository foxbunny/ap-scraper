"""
Anime-Planet.com scraper

Doctests:

    >>> ctx = BeautifulSoup('''
    ... <main>
    ...   <h1>Title</h1>
    ...   <div class="pagination aligncenter">
    ...     <a>1</a>
    ...     <a>2</a>
    ...     <a>3</a>
    ...   </div>
    ... </main>
    ... ''', 'html.parser')
    >>> find_pager(ctx)
    <div class="pagination aligncenter">
    <a>1</a>
    <a>2</a>
    <a>3</a>
    </div>


    >>> ctx = BeautifulSoup('''
    ... <div class="pagination aligncenter">
    ...   <a>1</a> <a>2</a> <a>3</a>
    ... </div>
    ... ''', 'html.parser')
    >>> list(get_pager_range(ctx))
    [1, 2, 3]


    >>> ctx = BeautifulSoup('''
    ... <div>
    ...   <ul class="cardDeck" data-type="anime">
    ...     <li class="card">
    ...       <a title="anime metadata 1">First</a>
    ...     </li>
    ...     <li class="card">
    ...       <a title="anime metadata 2">Second</a>
    ...     </li>
    ...   </ul>
    ... </div>
    ... ''', 'html.parser')
    >>> list(get_anime_metadata(ctx))
    [anime metadata 1, anime metadata 2]


    >>> ctx = BeautifulSoup('''
    ... <div>
    ...   <h5>Title</h5>
    ... </div>
    ... ''', 'html.parser')
    >>> anime_get_title(ctx)
    'Title'


    >>> ctx = BeautifulSoup('''
    ... <div>
    ...   <h6 class="aka">Alternative title</h6>
    ... </div>
    ... ''', 'html.parser')
    >>> anime_get_title_alt(ctx)
    'Alternative title'
    >>> ctx = BeautifulSoup('<div></div>', 'html.parser')
    >>> anime_get_title_alt(ctx)
    ''


    >>> ctx = BeautifulSoup('''
    ... <div>
    ...   <li class="type">TV (12ep)</li>
    ... </div>
    ... ''', 'html.parser')
    >>> anime_get_type(ctx)
    'TV (12ep)'


    >>> ctx = BeautifulSoup('''
    ... <ul>
    ...   <li class="type">TV (12ep)</li>
    ...   <li>Production I.G.</li>
    ...   <li>Bogus</li>
    ... </ul>
    ... ''', 'html.parser')
    >>> anime_get_studio(ctx)
    'Production I.G.'
    >>> ctx = BeautifulSoup('''
    ...   <li class="type">TV (12ep)</li>
    ...   <li></li>
    ...   <li>Bogus</li>
    ... </ul>
    ... ''', 'html.parser')
    >>> anime_get_studio(ctx)
    ''


    >>> ctx = BeautifulSoup('''
    ... <ul>
    ...   <li class="iconYear">2010 - 2011</li>
    ... </ul>
    ... ''', 'html.parser')
    >>> anime_get_year(ctx)
    '2010 - 2011'
    >>> ctx = BeautifulSoup('''
    ... <ul>
    ...   <li class="iconYear"></li>
    ... </ul>
    ... ''', 'html.parser')
    >>> anime_get_year(ctx)
    ''


    >>> ctx = BeautifulSoup('''
    ... <ul>
    ...   <li><div class="ttRating">3.4</div></li>
    ... </ul>
    ... ''', 'html.parser')
    >>> anime_get_rating(ctx)
    '3.4'
    >>> ctx = BeautifulSoup('''
    ... <ul>
    ...   <li></li>
    ... </ul>
    ... ''', 'html.parser')
    >>> anime_get_rating(ctx)
    ''


    >>> ctx = BeautifulSoup('''
    ... <div>
    ...   <p>Awesome description</p>
    ... </div>
    ... ''', 'html.parser')
    >>> anime_get_description(ctx)
    'Awesome description'


    >>> ctx = BeautifulSoup('''
    ... <div>
    ...   <div class="tags">
    ...     <h4>Tags</h4>
    ...     <ul>
    ...       <li>food</li>
    ...       <li>drinks</li>
    ...       <li>fun</li>
    ...     </ul>
    ...   </div>
    ... </div>
    ... ''', 'html.parser')
    >>> anime_get_tags(ctx)
    ['food', 'drinks', 'fun']
    >>> ctx = BeautifulSoup('<div></div>', 'html.parser')
    >>> anime_get_tags(ctx)
    []


    >>> ctx = BeautifulSoup('''
    ... <div>
    ...   <h5>Awesome anime</h5>
    ...   <h6 class="aka">Alt title: Osomu anime</h6>
    ...   <ul class="entryBar">
    ...     <li class="type">TV (12ep)</li>
    ...     <li>Production I.G.</li>
    ...     <li class="iconYear">2010 - 2011</li>
    ...     <li><div class="ttRating">3.4</div></li>
    ...   </ul>
    ...   <p>Wonderful story about anime.</p>
    ...   <div class="tags">
    ...     <h4>Tags</h4>
    ...     <ul>
    ...       <li>food</li>
    ...       <li>drinks</li>
    ...       <li>fun</li>
    ...     </ul>
    ...   </div>
    ... </div>
    ... ''', 'html.parser')
    >>> meta = anime_get_metadata(ctx)
    >>> meta['title']
    'Awesome anime'
    >>> meta['altTitle']
    'Alt title: Osomu anime'
    >>> meta['type']
    'TV (12ep)'
    >>> meta['studio']
    'Production I.G.'
    >>> meta['year']
    '2010 - 2011'
    >>> meta['rating']
    '3.4'
    >>> meta['description']
    'Wonderful story about anime.'
    >>> meta['tags']
    ['food', 'drinks', 'fun']
"""

import json
from functools import partial
from itertools import chain

import requests
from bs4 import BeautifulSoup
from it import it

from bsutil import (parse_html, find_by, find_by_class, find_links, find_all_by,
                    has_text_content)
from funcutil import (pipe, filter_by, map_with, unless, default, is_none,
                      from_spec, apply_to)


BASE_URL = 'https://www.anime-planet.com/anime/all'
PAGE_PARAMETERS = '?sort=title&order=asc&page='


def get_range(last_number):
    """ Return a range object for a given number

    The range starts with 1 and ends with the specified number.

    Example:

        >>> get_range(6)
        range(1, 7)
    """
    return range(1, last_number + 1)


get_string_if_any = pipe(
    unless(is_none, it.string),
    default(""),
)

""" Find a pager container element in the given context 

Expects a BeautifulSoup context object.
"""
find_pager = partial(find_by_class, "div", "pagination aligncenter")

""" Find anime card deck 

Expects a BeautifulSoup context object.
"""
find_anime_card_deck = partial(find_by, "ul",
                               {"class": "cardDeck",
                                "data-type": "anime"})

""" Retrieve a page range from the pager on a page

Expects a BeautifulSoup context object.
"""
get_pager_range = pipe(
    find_pager,
    find_links,
    filter_by(has_text_content),
    map_with(it.string),
    map_with(int),
    max,
    get_range
)

""" Retrieve and parse the contents of a HTML page 

Expects the pager URL as a string.
"""
get_page_content = pipe(
    requests.get,
    it.text,
    parse_html,
)

""" Get a count of pages in a remote page 

Expects the pager URL as a string.
"""
get_page_count = pipe(
    get_page_content,
    get_pager_range,
)

""" Get anime info in anime card deck anchors

Expects a BeautifulSoup context object.
"""
get_anime_metadata = pipe(
    find_anime_card_deck,
    find_links,
    map_with(it["title"]),
    map_with(parse_html)
)

""" Get anime metadata on a page

Expects a page URL as a string.
"""
download_anime_list_by_url = pipe(
    get_page_content,
    get_anime_metadata
)

""" Get the title in the anime metadata 

Expects a BeautifulSoup context object.
"""
anime_get_title = pipe(
    partial(find_by, 'h5', None),
    it.string,
)

""" Get the alternative title in the anime metadata 

Expects a BeautifulSoup context object.
"""
anime_get_title_alt = pipe(
    partial(find_by_class, 'h6', 'aka'),
    get_string_if_any
)

""" Get the anime type in the metadata 

Expects a BeautifulSoup context object.
"""
anime_get_type = pipe(
    partial(find_by_class, "li", "type"),
    it.string,
)

""" Get the studio name from anime metadata 

Expects a BeautifulSoup context object.
"""
anime_get_studio = pipe(
    partial(find_by_class, "li", ""),
    get_string_if_any
)


""" Get years from anime metadata 

Expects a BeautifulSoup context object.
"""
anime_get_year = pipe(
    partial(find_by_class, 'li', 'iconYear'),
    get_string_if_any
)


""" Get anime rating from anime metadata 

Expects a BeautifulSoup context object.
"""
anime_get_rating = pipe(
    partial(find_by_class, 'div', 'ttRating'),
    get_string_if_any,
)

""" Get the description from anime metadata 

Expects a BeautifulSoup context object.
"""
anime_get_description = pipe(
    partial(find_by, 'p', None),
    it.string
)

""" Get tags from anime metadata

Expects a BeautifulSoup context object.
"""
anime_get_tags = pipe(
    partial(find_by_class, 'div', 'tags'),
    unless(is_none, pipe(
        partial(find_all_by, 'li', None),
        map_with(it.string),
        list
    )),
    default([])
)


""" Return a dict containing individual anime metadata

Expects a BeautifulSoup context object representing the HTML of the anime 
metadata.
"""
anime_get_metadata = from_spec({
    "title": anime_get_title,
    "altTitle": anime_get_title_alt,
    "type": anime_get_type,
    "studio": anime_get_studio,
    "year": anime_get_year,
    "rating": anime_get_rating,
    "description": anime_get_description,
    "tags": anime_get_tags,
})


def to_page_url(page_number):
    return BASE_URL + PAGE_PARAMETERS + str(page_number)


def run_baby_run():
    return apply_to(BASE_URL, pipe(
        get_page_count,
        map_with(pipe(
            to_page_url,
            download_anime_list_by_url,
            map_with(anime_get_metadata)
        )),
        chain.from_iterable
    ))


if __name__ == "__main__":
    with open('anime.json', 'w', encoding="utf-8") as fout:
        for metadata in run_baby_run():
            print(metadata['title'])
            fout.write(json.dumps(metadata, ensure_ascii=False) + "\n")
