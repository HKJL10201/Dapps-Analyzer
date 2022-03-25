import os
import csv

FILE = 'dapp_link.csv'
PATH = 'contracts'


def get_links(file):
    res = []
    r = csv.reader(open(file, 'r', encoding='utf-8'))
    for line in r:
        name, url = line
        if url[:5] == 'https':
            res.append(url)
    return res


def download(links, path='contracts'):
    if not os.path.exists(path):
        os.mkdir(path)
    print('start cloning...')
    idx = 1
    for link in links:
        folder = '%03d' % idx
        print(folder)
        os.system('cd ' + path+' && mkdir '+folder+' && cd '+folder +
                  ' && git clone '+link.strip())
        idx += 1
    print('>> finish cloning.')


def main():
    global FILE, PATH
    download(get_links(FILE), PATH)
