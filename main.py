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

    options = parser.add_argument_group('Analyze options')
    options.add_argument('--mode',
                         nargs='?',
                         default=False,
                         const='function',
                         choices=['program', 'contract', 'function'],
                         help='compare mode: [program, contract, function]. Default value is function')
    options.add_argument('--igfile',
                         nargs='?',
                         default=False,
                         const='Migrations.sol,node_modules',
                         help='ignore the files or diretories with specific names, \
                             saparated with commas. Default value is Migrations.sol,node_modules')
    options.add_argument('--igcon',
                         nargs='?',
                         default=False,
                         const='Migrations',
                         help='ignore the contracts with specific names, \
                             saparated with commas. Default value is Migrations')

    args = parser.parse_args()

    category = None
    # process input code

    max_idx = 100
    if args.amount:
        max_idx = args.amount

    compare_mode = 'function'
    if args.mode:
        compare_mode = args.mode

    ignore_programs = []
    ignore_contracts = []
    if args.igfile:
        ignore_programs = args.igfile.split(',')
    if args.igcon:
        ignore_programs = args.igcon.split(',')

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
        dapp_analyzer.run_compare(
            compare_mode, ignore_programs, ignore_contracts)

    if args.external:
        dapp_analyzer.run_external(ignore_programs, ignore_contracts)

    if args.all:
        if args.category:
            category = args.category
            dapp_reptile.main(category, max_idx)
            dapp_download.main()
            sol_selector.main()
            dapp_analyzer.main(compare_mode, ignore_programs, ignore_contracts)
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
