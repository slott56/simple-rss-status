..  _approach:

Approach
==============

We start with some previously saved history, :math:`S_t` for some time, :math:`t`. The base time, :math:`t=0` will
have an empty set of history, :math:`S_0 = \emptyset`. A blank slate.

Each day, we're going to do three things.

1.  Get the daily RSS feed, we can call it :math:`D_t` for some time, :math:`t > 0`.
    The idea is that :math:`t` is monotonically increasing.

2.  Compare the daily feed with saved history to see what's new. This is :math:`D_t - S_{t-1}`.

3.  Update the saved history. This is :math:`S_{t} = D_t \cup S_{t-1}`.

As a practical matter, the time parameter, :math:`t`, is the current day.

Implementation Details
----------------------

We'll need to save the data. We have two overall approaches to this

-   Use **one master file** and keep updating that file.

-   Use **a collection of files** on a daily basis.

The "One Master File" approach is appealing. You look in the file. You have the saved history and the recent changes.
It's awkward to debug and impossible to audit without a lot of additional information.
This is the ideal for a highly-polished end-user-friendly desktop application. It's -- perhaps -- a goal.
Sadly, it's not very simple to implement because intermediate state change information is lost.

The "Collection of Files" approach creates a lot of small files. While it's bulky, it's trivial to audit.
There are a lot of simple files written using a number of simple rules.

The idea is this.

Each day will have a folder with a name that follows the YYYYMMDD pattern: ``20180702`` for example.

Inside each day's unique folder, there will be three files:

1.  :file:`20180702/daily.csv` This is the daily download of RSS data, parsed and saved as a CSV file.
    This is :math:`D_t`

2.  :file:`20180702/new.csv` This is the items which are new. :math:`N_t = D_t - S_{t-1}`

3.  :file:`20180702/saved.csv` This is the accumulated history of items seen so far.
    It's built as :math:`S_{t} = D_t \cup S_{t-1}` each day.
    It can also be thought of as :math:`S_{t} = \bigcup_t D_t`, the union of all previous daily files.
