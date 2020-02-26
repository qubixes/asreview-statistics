# Copyright 2020 The ASReview Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging

from pprint import pprint

from asreview.config import LOGGER_EXTENSIONS
from asreview.entry_points import BaseEntryPoint

from asreviewcontrib.statistics import LogStatistics
from asreviewcontrib.statistics.statistics import DataStatistics


class StatEntryPoint(BaseEntryPoint):
    description = "Plotting functionality for logging files produced by "\
        "ASReview."
    extension_name = "asreview-statistics"

    def __init__(self):
        from asreviewcontrib.statistics.__init__ import __version__
        super(StatEntryPoint, self).__init__()

        self.version = __version__

    def execute(self, argv):
        logging.getLogger().setLevel(logging.ERROR)
        parser = _parse_arguments()
        args = vars(parser.parse_args(argv))

        log_paths = []
        for path in args['paths']:
            try:
                stat = DataStatistics.from_file(path)
                print("--------------------")
                print(path)
                print(stat.format_summary(), end='')
                print("++++++++++++++++++++\n")
            except ValueError:
                log_paths.append(path)

        if len(log_paths) == 0:
            return
        prefix = args["prefix"]
        if len(args["wss"]) + len(args["rrf"]) == 0:
            args["wss"] = [95, 100]
            args["rrf"] = [5, 10]

        with LogStatistics.from_paths(log_paths, prefix=prefix) as stat:
            if len(stat.analyses) == 0:
                print(f"No log files found in {log_paths}.\n"
                      f"To be detected log files have to start with '{prefix}'"
                      f" and end with one of the following: \n"
                      f"{', '.join(LOGGER_EXTENSIONS)}.")
                return
            wss_results = {f"wss_{wss}": stat.wss(wss)
                           for wss in args["wss"]}
            rrf_results = {f"rrf_{rrf}": stat.rrf(rrf)
                           for rrf in args["rrf"]}
            results = {**wss_results, **rrf_results}
            pprint(results)


def _parse_arguments():
    parser = argparse.ArgumentParser(prog='asreview stat')
    parser.add_argument(
        'paths',
        metavar='N',
        type=str,
        nargs='+',
        help='Data directories, data files or datasets.'
    )
    parser.add_argument(
        "--prefix",
        default="",
        help='Filter files in the data directory to only contain files'
             'starting with a prefix.'
    )
    parser.add_argument(
        "--abstract_only",
        default=False,
        action="store_true",
        help="Use after abstract screening as the inclusions/exclusions."
    )
    parser.add_argument(
        "--wss",
        default=[],
        action="append",
        help="Compute WSS @ some percentage."
    )
    parser.add_argument(
        "--rrf",
        default=[],
        action="append",
        help="Compute RRF @ some percentage."
    )
    return parser