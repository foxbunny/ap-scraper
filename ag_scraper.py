"""
Anime-Planet.com scraper
"""

import json
from functools import partial
from itertools import chain

import requests
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
