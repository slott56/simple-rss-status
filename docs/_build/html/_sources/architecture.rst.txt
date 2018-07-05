#####################
Software Architecture
#####################

In the :ref:`approach` section, we identified three steps.
When we have multiple processing steps, we need to define multiple functions to implement
those steps. The mapping isn't exact because we're refining abstractions into concrete
expressions.

1.  The core RSS reader function. Pragmatically, this tends to expand into more than one function
    so we can separate the core XML parsing from add-on parsing that's unique to the data we're working with.
    For example, decomposing the title isn't about RSS in general, it's about this specific problem domain.

2.  A saved state getter.
    There's not much to this, but it's important to recover the information
    from the chalky slate where each day's updates are recorded.

4.  A saved state writer. This can be pressed into service to write all of the files,
    since they're structurally identical.

Let's rough out the overall plan as conceptual pseudo-code shoing the original approach
steps and how they've become functions that map arguments to results.

::

    yesterdays_path, todays_path = path_maker("Some_RSS_URL")

    # 1. Get Daily RSS Feed
    todays_data = xml_reader("Some_RSS_URL")
    saved_data = csv_load(yesterday_path / "save.csv")

    # 2. Compare with saved history
    new_data = set(todays_data) - set(saved_data)

    # 3. Update saved history
    all_data = set(todays_data) | set(saved_data)

    csv_dump(new_data, today_path / "new.csv")
    csv_dump(todays_data, today_path / "daily.csv")
    csv_dump(all_data, today_path / "save.csv")

The above is purely conceptual. The idea is to outline a possible approach. As we delve into
details, we'll uncover places where this might be less than perfect. The final code will
differ based on the things we learn along the way.

This core processing sequence can be performed for any number of RSS channels. The idea is
to capture as many as necessary.

Some Design Patterns
--------------------

One overall idea that is helpful is the **Extract-Transform-Load** (ETL) pipeline.
This application involves ETL in miniature:

-   Extract raw data from it's XML representation to build Python objects.

-   Transform the raw data from one class of Python objects to another class of objects.

-   Load the transformed data into a "database". In this case, a bunch of directories
    and files. The conceptual "database load" is implemented as function to "dump" the data
    in CSV notation.

    The terminology change is awkward, but Python uses "dump" and "load"
    as the verbs of choice for dumping python objects into an external file and loading
    Python objects from an external file.

Additionally, we're working with several examples of **Serialization**. The concept
is to create a series of bytes that represent a Python object. The source data
was serialized in XML notation; we parse that to recover Python objects. The working
data is serialized in CSV notation; we load and dump those files.

.. py:module:: xml_parsing

Core Data Structures
--------------------

We have to address some technical nuance before going forward.

..  important::

    Python sets work with immutable objects.

    The ``csv`` module works with mutable List or Dict objects for each row.

This will be aggravating.

..  sidebar:: Mutability

    There's a firm and abiding distinction between mutable and immutable data
    structures in Python.

    -   Immutable: strings, numbers, tuples. These are objects with an unchanging
        internal state. We can't change the value of the integer 13.

    -   Mutable: Lists, Dicts, instances of classes we define. These are objects
        with an internal state we can adjust.

        ::

            >>> some_list = [1, 2, 3]
            >>> some_list.append(42)
            >>> some_list
            [1, 2, 3, 42]

        The list object, ``some_list`` was mutated by the :meth:`append` method.

    "But wait," you cry out. "What about this?"

    ::

        >>> some_number = 13
        >>> some_number = some_number + 1
        >>> some_number
        14

    "We mutated ``some_number``!"

    Well, actually...

    The object, ``13`` did not mutate. The expression ``some_number + 1`` is working with two
    immutable objects. A new immutable object, ``14``, was created by the expression.
    This new immutable object was then assigned the name ``some_number``. The old immutable ``13``
    object is no longer being used.

We have two choices for working with the mutable results of reading CSV files.

-   Implement our own versions of set subtraction and set union that work
    with mutable objects. This has the advantage of enabling the huge flexibility
    inherent in working with the :class:`csv.DictReader`: each row becomes
    a dictionary with an indefinition collection of keys.

-   Transmogrify the mutable objects into immutable data structures.
    (The technical term is "coerce", but I like transmogrification.)
    While this tends to limit our flexibility somewhat, it saves us from
    implementing set operations.

The transmogrification approach leads us to building a named tuple object
for each CSV row.

..  autoclass:: xml_parsing.SourceRSS
    :members:

..  autoclass:: xml_parsing.ExpandedRSS
    :members:


XML Parsing
-----------

XML parsing is handled gracefully by Python's :mod:`xml` package. There are several
parses, the :mod:`xml.etree` is particularly nice, and provides a wealth of features.

..  autofunction::   xml_parsing.xml_reader


Creating Working Paths
----------------------

We have two dimensions to the paths. The :func:`path_maker` function will
honor this by using a name from the URL and today's date.

..  autofunction:: xml_parsing.path_maker

What about yesterday's files?  We can't simply subtract one day from today's date.
For that to work, we'd have to religiously run this **every single day**. That's unreasonable.
What's easier is locating the most recent date which contains files for a given channel.

..  autofunction:: xml_parsing.find_yesterday

Saving and Recovering CSV State
-------------------------------

These two functions will save and restore collections of :class:`ExpandedRSS` objects.
We use the names "dump" and "load" to be consistent with other serialization packages.
We could use ``json.dump()`` or ``yaml.dump()`` instead of writing in CSV notation.

..  autofunction:: xml_parsing.csv_dump

..  autofunction:: xml_parsing.csv_load

Transformations
---------------

Currently, we only have one transformation, from :class:`SourceRSS` to
:class:`ExpandedRSS`.

..  autofunction:: xml_parsing.title_transform

In the long run, there will be additional transformations.

Adding transormations means this single function does too many things.
The current design has two elements combined together.

1.  Building a new list from individually transformed rows.

2.  Applying a single transformation process to create :class:`ExpandedRSS` objects.

In the longer run (see :ref:`expansions`) this needs to be refactored to allow
multiple transformation processes to be combined by an over-arching transformation pipeline.
