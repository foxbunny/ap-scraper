"""
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

from ag_scraper import *
from bs4 import BeautifulSoup
