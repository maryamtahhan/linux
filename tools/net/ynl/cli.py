#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause

import argparse
import json
import pprint
import time
import os

from lib import YnlFamily

class ynlConfig():
    def __init__(self):
        self.no_schema = True
        self.schema = None
        self.spec = None
        self.json_text = None
        self.ntf = None
        self.sleep = None
        self.do = None
        self.dump = None
    def run(self):
        ynl_cfg(self.no_schema, self.spec, self.schema, self.json_text, self.ntf, self.sleep, self.do, self.dump)

def ynl_cfg(no_schema, spec, schema, json_text, ntf, sleep, do, dump):

        if no_schema:
            schema = ''

        attrs = {}
        if json_text:
            attrs = json.loads(json_text)

        ynl = YnlFamily(spec, schema)

        if ntf:
            ynl.ntf_subscribe(ntf)

        if sleep:
            time.sleep(sleep)

        if do:
            reply = ynl.do(do, attrs)
            pprint.PrettyPrinter().pprint(reply)
        if dump:
            reply = ynl.dump(dump, attrs)
            pprint.PrettyPrinter().pprint(reply)

        if ntf:
            ynl.check_ntf()
            pprint.PrettyPrinter().pprint(ynl.async_msg_queue)

def main():
    parser = argparse.ArgumentParser(description='YNL CLI sample')
    parser.add_argument('--spec', dest='spec', type=str)
    parser.add_argument('--schema', dest='schema', type=str)
    parser.add_argument('--no-schema', action='store_true')
    parser.add_argument('--json', dest='json_text', type=str)
    parser.add_argument('--do', dest='do', type=str)
    parser.add_argument('--dump', dest='dump', type=str)
    parser.add_argument('--sleep', dest='sleep', type=int)
    parser.add_argument('--subscribe', dest='ntf', type=str)
    parser.add_argument('--config', dest='config', type=str)
    args = parser.parse_args()

    if args.config:
        directory = ""
        yamls = {}

        if not os.path.exists(args.config):
             print("Error: ", args.config, " doesn't exist")
             exit(-1)

        f = open(args.config)
        data = json.load(f)

        for k in data:
            if k == 'yaml-specs-path':
                directory = data[k]

                # Scan the dir and get all the yaml files.
                for filename in os.scandir(directory):
                    if filename.is_file():
                        if filename.name.endswith('.yaml'):
                            yamls[filename.name] = filename.path

            elif k == 'spec-args':
               for v in data[k]:
                    print("############### ",v," ###############\n")
                    cfg = ynlConfig()
                    # Check for yaml from the specs we found earlier
                    if v in yamls:
                        # FOUND
                        cfg.spec = yamls[v]
                        if 'no-schema' in data[k][v]:
                            cfg.no_schema = data[k][v]['no-schema']
                        if 'schema' in data[k][v]:
                            cfg.schema = data[k][v]['schema']
                            cfg.no_schema = False
                        if 'do' in data[k][v]:
                            cfg.do = data[k][v]['do']
                        if 'dump' in data[k][v]:
                            cfg.dump = data[k][v]['dump']
                        if 'subscribe' in data[k][v]:
                            cfg.ntf = data[k][v]['subscribe']
                        if 'sleep' in data[k][v]:
                            cfg.sleep = data[k][v]['sleep']
                        if 'json-params' in data[k][v]:
                            cfg.json_text = json.dumps(data[k][v]['json-params'])

                        cfg.run()
                    else:
                        print("Error: ", v, " doesn't have a valid yaml file in ", directory, "\n")
    else:
        ynl_cfg(args.no_schema, args.spec, args.schema, args.json_text, args.ntf, args.sleep, args.do, args.dump)

if __name__ == "__main__":
    main()
