#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dapp_reptile
import dapp_download
import sol_selector
import dapp_analyzer
import clear


import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Dapp Analysis tool for Solidity Blockchain Smart Contracts (ETH)')

    inputs = parser.add_argument_group('Input arguments')
    inputs.add_argument('-c', '--category',
                        help='target category')
    inputs.add_argument('-a', '--amount',
                        default=100,
                        help='amount of dapps')

    features = parser.add_argument_group('Features')
    features.add_argument('-A', '--all',
                          action='store_true',
                          help='run the whole process automatically')
    features.add_argument('-r', '--reptile',
                          action='store_true',
                          help='run dapp_reptile to get dapp links from GitHub')
    features.add_argument('-d', '--download',
                          action='store_true',
                          help='run dapp_download to download dapps from GitHub')
    features.add_argument('-s', '--sol',
                          action='store_true',
                          help='run sol_selector to generate sol file list')
    features.add_argument('-m', '--compare',
                          action='store_true',
                          help='run dapp similarity comparison')
    features.add_argument('-e', '--external',
                          action='store_true',
                          help='run dapp external function analysis')
    features.add_argument('-C', '--clear',
                          action='store_true',
                          help='clear all generated files')

    args = parser.parse_args()

    category = None
    # process input code

    max_idx = 100
    if args.amount:
        max_idx = args.amount

    if args.reptile:
        if args.category:
            category = args.category
            dapp_reptile.main(category, max_idx)
        else:
            print('Error: Please specify your category!')
            parser.print_help()
            return

    if args.download:
        dapp_download.main()

    if args.sol:
        sol_selector.main()

    if args.compare:
        dapp_analyzer.run_compare(max_idx)

    if args.external:
        dapp_analyzer.run_external()

    if args.all:
        if args.category:
            category = args.category
            dapp_reptile.main(category, max_idx)
            dapp_download.main()
            sol_selector.main()
            dapp_analyzer.main(max_idx)
        else:
            print('Error: Please specify your category!')
            parser.print_help()
            return

    if args.clear:
        clear.main()

    if not args.reptile and not args.download\
        and not args.sol and not args.compare\
            and not args.external and not args.all\
    and not args.clear:
        parser.print_help()


if __name__ == '__main__':
    main()
