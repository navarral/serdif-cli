#!/venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2023/05/09 09:00:00
# @Author  : navarral
# @Site    : https://w3id.org/serdif
# @File    : __main__


import sys
import argparse
from serdif import linkage
import time
import textwrap


# Construct the argument parser and parse the arguments
arg_desc = '''\
    Welcome to SERDIF command line interface (CLI)!
    -----------------------------------------------------------------------
        This program loads a event data and metadata from two separate
        files and links them with environmental datasets. The output is
        a zip file with the linked data and metadata as data tables (.csv),
        graphs (.ttl, .trig) and an interactive report (.html).
    
    author: Albert Navarro-Gallinad
    version: 20230509
    -----------------------------------------------------------------------
    \
    '''

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=arg_desc)

required = parser.add_argument_group('required arguments')

# event data argument
required.add_argument('-e', '--events', metavar='', required=True,
                      help=textwrap.dedent('''Path to your input events data .csv file. 
The file must contain the following columns: id, group, longitude, lattitude, date, length, lag and spatial.

| id | group | longitude | latitude |    date    | length | lag | spatial |
|----|-------|-----------|----------|------------|--------|-----|---------|
| 11 |   A   |  -6.2530  |  53.3436 | 2010-02-05 |   30   |  0  |   30    |
| 12 |   A   |  -6.2530  |  53.3436 | 2010-02-05 |   30   |  0  |  NUTS-2 |

* id: event identifier [only letters, numbers and dashed without spaces]
* longitude: Longitude coordinate of the event's location [numeric]
* latitude: Latitude coordinate of the event's location [numeric]
* date: Date of the event in the format YYYY-MM-DD [YYYY-MM-DD]
* length: Time interval to gather data in days [integer]
* lag: Time between the data and the event in days [integer]
* spatial: spatial linkage method between events and datasets. 
    The allowed values are standard NUTS regions [https://ec.europa.eu/eurostat/web/nuts/nuts-maps] "NUTS-0", "NUTS-1", "NUTS-2", "NUTS-3";
    or any positive number which refers to the radius from the event location in km.
The file must be a .csv file with comma-separated values and no missing values are allowed.\n
'''))

# event metadata argument
required.add_argument('-i', '--info', metavar='', required=True,
                      help=textwrap.dedent('''Path to your input events metadata .csv file. 
The file must contain the following columns: key, value.

|     key        |                      value                          |
|----------------|-----------------------------------------------------|
|    context     |                 ANCA vasculitis                     |
|    publisher   |          https://www.adaptcentre.ie/                |
|     license    |   https://creativecommons.org/licenses/by-sa/4.0/   |
| dataController |               https://www.tcd.ie/                   |
|  dataProcessor |         https://orcid.org/0000-0002-2336-753X       |
|   datasetsURLs |   https://doi.org/10.24381/cds.adbb2d47, http://... |

The key column must contain the following values:
* context: context of what the events refer to (e.g. a particular disease) [string]
* publisher: publisher entity associated with the resulting linked dataset [valid URL]
* license: license assigned to the resulting linked dataset [valid URL]
* dataController: data controller entity assigned to the resulting linked dataset [valid URL]
* dataProcessor: agent that performed the linkage process [valid URL]
* datasetsURLs: space separated list of the URLs associated with your input environmental datasets [valid URL]
The file must be a .csv file with comma-separated values and no missing values are allowed.
'''))

# dataset folder argument
# aggregation method argument
required.add_argument('-d', '--datasets', metavar='', required=True,
                      help='Path to your environmental dataset folder (e.g. /data ). ')

# temporal linkage argument
required.add_argument('-t', '--timeunit', metavar='', required=True, default='day',
                      choices=['raw', 'hour', 'day', 'month', 'year'],
                      help=textwrap.dedent('''The observations of your datasets can be integrated to a broader temporal unit or kept as input (raw).
Allowed values are: raw, hour, day, month, year.
'''))

# aggregation method argument
required.add_argument('-agg', '--aggregation', metavar='', required=True, default='day',
                      choices=['avg', 'sum', 'min', 'max', 'median'],
                      help='Given that more than one dataset can be linked to an event, select an aggregation method '
                           'to integrate the observations for the same variable. Allowed values are: avg, sum, min, max, median.')

args = vars(parser.parse_args())

steps_progress = ['load events', 'load metadata', 'link events', 'link metadata',
                  'link events and metadata',
                  'link events and metadata with environmental datasets',
                  'generate report']


def main():
    print(arg_desc)
    queryTimeStr = time.strftime('%Y%m%dT%H%M%S')
    linkage.load_events(
        event_data=args['events'],
        event_metadata=args['info']
    )
    linkage.uplift_metadata(
        raw_folder='.' + args['datasets'],
        queryTimeStr=queryTimeStr,
    )
    linkage.serdif_geosparql()
    linkage.link_data(
        raw_folder='.' + args['datasets'],
        df_input_path=args['events'],
        df_info_path=args['info'],
        queryTimeStr=queryTimeStr,
        agg_method=args['aggregation'],
        time_Unit=args['timeunit'],
    )


if __name__ == '__main__':
    main()
