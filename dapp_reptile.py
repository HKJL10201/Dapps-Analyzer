import csv
import requests
from bs4 import BeautifulSoup
import time

OUT = 'dapp_link.csv'
IEP = 10  # Items Each Page


def req(url):
    # define header
    header = {}
    header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    # create Request with header
    req = requests.get(url, headers=header)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def reptile(category, max_idx=100, page=1, idx=1, tm=10):
    global OUT
    res = []

    scale = 50

    print("START".center(scale, "-"))
    start = time.perf_counter()
    url = 'https://github.com/search?p=%d&q=dapp+%s&type=Repositories' % (
        page, category)

    while idx <= max_idx:
        i = int(idx/max_idx*scale)
        a = "*" * i
        b = "." * (scale - i)
        c = (i / scale) * 100
        dur = time.perf_counter() - start
        print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(c, a, b, dur), end="")

        soup = req(url)

        links = soup.find_all('a', class_='v-align-middle')

        # writer.writerow([page,max_page])

        if links == None:
            break

        for link in links:
            name = link['href'][1:]
            dapp_url = 'https://github.com/'+name
            res.append([name, dapp_url])
            idx += 1
            if idx > max_idx:
                break

        next_page = soup.find('a', class_='next_page')
        if next_page == None:
            break
        else:
            url = 'https://github.com/'+next_page['href']
        time.sleep(tm)
    print("\n"+"END".center(scale, "-"))
    return res


def main(category, amount=100):
    global IEP, OUT
    res = []
    n = 0
    tm = 10
    print('reptile start')
    while n < amount:
        n = len(res)
        rear = n % IEP
        if rear != 0:
            for i in range(rear):
                res.pop()
        start = n//IEP+1
        idx = (start-1)*10+1
        # print(CLA,MAXI,start,idx,tm)
        links = reptile(category, amount, start, idx, tm)
        res += links
        n = len(res)
        if n < amount:
            tm += 10
            print('%d collected, retrying...' % n)
            time.sleep(30+tm)
    writer = csv.writer(open(OUT, 'w', newline='', encoding='utf-8'))
    writer.writerows(res)
    print('>> reptile done, results are shown in '+OUT)


def test():
    MAXI = 100    # max index
    CLA = 'trading'
    main(CLA, MAXI)
# main()
