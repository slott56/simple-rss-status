..  _expansions:

##############
Expansions
##############

The core user story did not include any word on transformations of the data.

The following general story framework summarizes a family of essential features:

    As a journalist, I want to parse titles and descriptions of RSS feeds to extract
    additional data encoded there so I can make better use of the available
    information.

Practically, the :func:`xml_parsing.title_transform` function is an instance of the above
general pattern. This function decomposes the title into docket and parties. There are more nuggets
of goodness buried in the description.

How do we expand the transformation steps? There are several parts to this:

-   Things we do to the code.

    1.  Write the additional **transform** functions to parse the description.

    2.  Test the function in isolation.

    3.  Expand the :class:`xml_parsing.ExpandedRSS` to include the additional attributes.

    4.  Revise the overall processing flow to

-   Things we do operationally to make it work.

    Here's the essential problem:

        The previous day's data will be incomplete with respect to the new transformation process.
