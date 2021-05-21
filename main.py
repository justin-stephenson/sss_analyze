#!/bin/python3

import sys
import argparse
import re

from sources import journald
from sources import files
from modules import request


def add_options():
    parser = argparse.ArgumentParser('sss_analyze')
    parser.add_argument(
            '--source', action='store', type=str, default='files',
            choices=['files', 'journald']
    )
    return parser

def load_module(module, parser):
    if module == 'request':
        analyzer = request.Analyzer()
    else:
        return
    analyzer.add_options(parser)
    return analyzer

def main():
    parser = add_options()

    module = load_module('request', parser)

    ns = parser.parse_args()
    args = vars(ns)

    if args['source'] == "journald":
        reader = journald.Reader()
    else:
        reader = files.Reader()

    module.execute(reader, args)

if __name__ == '__main__':
    main()
