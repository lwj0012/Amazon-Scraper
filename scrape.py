#!/usr/bin/python

import os, sys, math, time, Queue

import config
from app.iterfuncs import chunks
from app.scraper import WireProtocol, Scraper

def main():
    scraper = Scraper(
        db_path='./products.db',
        run_every=config.scraper['run_every']
    )
    
    products = scraper.get_products_list()
    if len(products) == 0:
        sys.exit(0)
    
    n_workers = config.scraper['workers']
    n_groups = int(math.ceil(float(len(products)) / float(n_workers)))
    
    groups = list(chunks(products, n_groups))
    workers = Queue.Queue()
    
    for i in range(n_workers):
        wp = WireProtocol(*os.pipe())
        pid = os.fork()
    
        if pid == 0:
            scraper.get_prices(wp, groups[i])
            sys.exit(0)
        
        workers.put((pid, wp))
    
    while not workers.empty():
        pid, wp = workers.get()
        scraper.save_prices(wp)

    sys.stdout.flush()
    sys.stderr.flush()
    sys.exit(0)

if __name__ == '__main__':
    # Auto-change directory
    name = sys.argv[0]
    dir_path = os.path.dirname(name)
    os.chdir(dir_path)
    
    main()
