from bs4 import BeautifulSoup


def parse_html(html_string):
    """ Create a BeautifulSoup context from a string

    Example:

        >>> parse_html('<p>Hello</p>')
        <p>Hello</p>
    """
    return BeautifulSoup(html_string, "html.parser")


def find_by(tag_name, attributes, ctx):
    """ Find an element by arbitrary attributes

    Example:

        >>> ctx = BeautifulSoup('''
        ... <div>
        ...   <div data-name="foo">foo</div>
        ... </div>
        ... ''', 'html.parser')
        >>> find_by('div', {'data-name': 'foo'}, ctx)
        <div data-name="foo">foo</div>
    """
    return ctx.find(tag_name, attributes)


def find_by_class(tag_name, classes, ctx):
    """ Find an element with a given tag name and classes

    Example:

        >>> ctx = BeautifulSoup('''
        ... <div>
        ...   <p class="foo">foobar</p>
        ... </div>
        ... ''', 'html.parser')
        >>> find_by_class('p', 'foo', ctx)
        <p class="foo">foobar</p>
    """
    return find_by(tag_name, {"class": classes}, ctx)


def find_next_by(tag_name, attribs, ctx):
    """ Find the next element by tag name and arbitrary attributes

    Example:

        >>> ctx = BeautifulSoup('''
        ... <div>
        ...   <li class="foo" data-type="bar">1</li>
        ...   <li class="foo" data-type="baz">2</li>
        ...   <li class="bar" data-type="bar">3</li>
        ...   <li class="bar" data-type="baz">4</li>
        ... </div>
        ... ''', 'html.parser')
        >>> first_li = find_by_class('li', 'foo', ctx)
        >>> find_next_by('li', {'class': 'bar'}, first_li)
        <li class="bar" data-type="bar">3</li>
    """
    return ctx.find_next(tag_name, attribs)


def find_all_by(tag_name, attribs, ctx):
    """ Find all elements by tag name and arbitrary attributes

    Example:

        >>> ctx = BeautifulSoup('''
        ... <p>
        ...   <a class="foo">1</a>
        ...   <a class="bar">2</a>
        ...   <a class="foo">3</a>
        ...   <a class="bar">4</a>
        ...   <a class="foo">5</a>
        ... </p>
        ... ''', 'html.parser')
        >>> find_all_by('a', {'class': 'foo'}, ctx)
        [<a class="foo">1</a>, <a class="foo">3</a>, <a class="foo">5</a>]
    """
    return ctx.find_all(tag_name, attribs)


def find_links(ctx):
    """ Return all links in a given BeautifulSoup context

    Example:

        >>> ctx = BeautifulSoup('''
        ... <p>
        ...   <a>Foo</a>
        ...   <a>Bar</a>
        ...   <a>Baz</a>
        ... </p>
        ... ''', 'html.parser')
        >>> find_links(ctx)
        [<a>Foo</a>, <a>Bar</a>, <a>Baz</a>]
    """
    return find_all_by("a", None, ctx)


def has_text_content(element):
    """ Return True if element has text content

    Example:

        >>> ctx = BeautifulSoup('<a>Foo</a>', 'html.parser')
        >>> has_text_content(ctx)
        True
        >>> ctx = BeautifulSoup('<a></a>', 'html.parser')
        >>> has_text_content(ctx)
        False
    """
    return element.string is not None
