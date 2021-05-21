import re
from enum import Enum

from sources import files
from sources import journald

class Analyzer:
    """ Request tracking module """
    def add_options(self, parser):
        subparser = parser.add_subparsers(dest='subcommand', metavar=None, required=True)
        request_parser = subparser.add_parser('request', help='Track requests'
                                              ' across SSSD components')
        request_parser.add_argument("--list", help="List recent client requests",
                                 action="store_true")
        ## FIXME: --id instead of --cid ?
        request_parser.add_argument("--cid", help="Print logs related to the provided Client ID")
        request_parser.add_argument("--pam",
                                 help="Use with --cid to track PAM related"
                                 "requests", action="store_true")
        request_parser.add_argument("--cachereq",
                                 help="Include cache request related logs",
                                 action="store_true")


    def get_cache_request_ids(self, client_id, source):
        cr_ids = []
        pattern = f"REQ_TRACE.*CID #{client_id}"
        for line in source:
            re_obj = re.compile(pattern)
            if re_obj.search(line):
                cr_re = re.compile('CR #[0-9]+')
                match = cr_re.search(line)
                if match:
                    found = match.group(0)
                    cr_ids.append(found)
        return cr_ids

    # iterate through source and search for any number of patterns in list
    def print_pattern_match(self, patterns, source):
        for line in source:
            for pattern in patterns:
                re_obj = re.compile(pattern)
                if re_obj.search(line):
                    ## fix journal newline issue
                    print(line, end='')
       
    def execute(self, source, options):
        if options['list']:
            self.list_requests(source, options['pam'])
        elif options['cid']:
            self.track_request(source, options)

    def list_requests(self, source, pam):
        component = source.Component.NSS
        resp = "nss"
        pattern = ['\[cmd']
        if pam:
            component = source.Component.PAM
            resp = "pam"

        print(f"******** Listing {resp} client requests ********")
        source.set_component(component)
        self.print_pattern_match(pattern, source)

    def track_request(self, source, options):
        client_id = options['cid']
        component = source.Component.NSS
        resp = "nss"
        pattern = [f'\[CID #{client_id}\]']

        if options['pam']:
            component = source.Component.PAM
            resp = "pam"

        print(f"******** Checking {resp} responder for Client ID {client_id} *******")
        source.set_component(component)
        if options['cachereq']:
            cr_ids = self.get_cache_request_ids(client_id, source)
            [pattern.append(id) for id in cr_ids]

        self.print_pattern_match(pattern, source)

        print(f"********* Checking Backend for Client ID {client_id} ********")
        pattern = [f'\[sssd.{resp} CID #{client_id}\]']
        source.set_component(source.Component.BE)
        self.print_pattern_match(pattern, source)
