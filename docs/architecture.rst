Software Architecture
=====================

In the :ref:`approach` section, we identified three steps.
When we have multiple processing steps, we need to define multiple functions.

1.  The core RSS reader function. Pragmatically, this tends to expand into more than one function
    so we can separate the core XML parsing from add-on parsing that's unique to the data we're working with.
    For example, decomposing the title isn't about RSS in general, it's about this specific problem domain.
2.  A saved state getter. There's not much to this, but it's important to have the chalky slate where each day's updates are recorded.
3.  The change report.
4.  A saved state writer.

Let's rough out the overall plan as conceptual psuedo-code:

::

    todays_data = xml_reader("Some_RSS_URL")
    saved_data = csv_reader(yesterday_path / "save.csv")

    new_data = list(item
        for item in todays_data
            if item not in saved_data)
    all_data = set(saved_data) | set(new_data)

    csv_writer(new_data, today_path / "new.csv")
    csv_writer(todays_data, today_path / "daily.csv")
    csv_write(all_data, today_path / "save.csv")

This core processing sequence can be performed for any number of RSS feeds. The idea is
to capture as many as necessary.
