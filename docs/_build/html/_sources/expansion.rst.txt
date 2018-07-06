..  _expansions:

##############
Expansions
##############

The core user story did not include any word on transformations of the data.

The following general story framework summarizes a family of essential features:

    As a journalist, I want to parse titles and descriptions of RSS feeds to extract
    additional data encoded there so I can make better use of the available
    information.

This suffers from a vagueness problem. See https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/
for help on decomposing this generic, meta-story into specific stories.
Also see https://agileforall.com/patterns-for-splitting-user-stories/ for more guidance
on decomposition of complexity.

Practically, the :func:`rss_status.title_transform` function is a single concrete instance of the above
general story pattern. This function decomposes the title into docket and parties. There are more nuggets
of goodness buried in the description property of the RSS item.

There's a tiny problem with this function. We'll look at two versions of adding transformations.
The first way to add transformations is simple and applies to the case were a few, very simple things need to be
done. Emphasis on "few".

Then we'll look at a more sophisticated rewrite that might be in order.

Simple Expansion
----------------

How do we expand the transformation steps? There are several parts to making a few, simple changes:

1.  Write the additional **transform** steps inside the :func:`rss_status.title_transform` function.

    Right now, the code looks like this::

        docket, _, parties_title = row.title.partition(' ')
        _, _, real_docket = docket.partition(":")

    Which partitions the title on a space, and the partitions the docket on a ```":"``.

2.  Test the function in isolation. This is best done with examples, as shown in
    the :func:`rss_status.title_transform` function. The Python doctest tool
    can confirm the example is correct.

    Here's the OS-level command that runs doctest.

    ::

        slott$ python3 -m doctest -v rss_status.py

    Here's the bottom two lines of the output.

    ::

        7 passed and 0 failed.
        Test passed.

    All of the examples worked as predicted.

3.  Expand the :class:`rss_status.ExpandedRSS` class to include the additional attributes
    built by the new **transform** function(s).

Because the structure of the :class:`rss_status.ExpandedRSS` class has changed, the next daily
feed will appear to be entirely new. And -- clearly -- the new data items make it appear all new.
There are ways to limit the scope of comparison to check for newness, but the problem of
"it appears all new after I made a change" doesn't appear to be large enough to yield significant
benefit from additional complexity.


More Sophistication
--------------------

The :func:`rss_status.title_transform` function does two things.

1.  It builds a list of :class:`rss_status.ExpandedRSS` items.

2.  It applies a series of transformational steps to each :class:`rss_status.SourceRSS` item to
    create the resulting :class:`rss_status.ExpandedRSS` items.

We can refactor the function to break it into poeces and make it quite a bit easier to expand.

First. The list-building is really this.

::

    todays_data = list(transform(xml_reader(url)))

This depends on a new :func:`transform` function.

::

    def transform(source: Iterable[SourceRSS]) -> Iterator[ExpandedRSS]:
        for item in source:
            parties_title, real_docket = title_parse(row.title)
            # other extraction goes here
            yield ExpandedRSS(
                title=row.title,
                link=row.link,
                description=row.description,
                pubDate=row.pubDate,
                docket=real_docket,
                parties_title=parties_title,
                # Other field values go here
            )

The :func:`title_parse` function looks like this.

::

    def title_parse(title: str) -> Tuple[str, str]:
        docket, _, parties_title = title.partition(' ')
        _, _, real_docket = docket.partition(":")
        return parties_title, real_docket

We can now easily add more things that are like :func:`title_parse`.

Since this is so small, it's easy to test in isolation. We can write many
functions like this, and bundle them into the overall :func:`transform` function
to add additional, derived attributes of each item.
