"""Namecheap.com marketplace parser.
Returns alist of domains within specified price limits 

Usage:
  docopt-test.py <min_price> <max_price> 
"""
from docopt import docopt
import requests
import time
from bs4 import BeautifulSoup
import sys
# a time delay between consecutive requests, in seconds
DELAY=1
if __name__ == '__main__':
    arguments = docopt(__doc__)
    price_min=arguments['<min_price>']
    price_max=arguments['<max_price>']
    try:
        price_min=int(price_min)
        price_max=int(price_max)
    except ValueError:
        print "<min_price> and <max_price> must be integer"
        sys.exit(0)   
    filename='namecheap-domains-%s-to-%s-dollars.txt' %(price_min,price_max)
    print "Parsing namecheap for domain %s to %s US dollars worth" %(price_min,price_max)
    print "Expect results in file: %s" % filename
    with open(filename,'w') as f:
        uri=r"https://www.namecheap.com/domains/marketplace/buy-domains.aspx?page=1&size=100&excludehypen=false&excludenumber=false&adultlisting=true&priceRange="+str(price_min)+"%3a"+str(price_max)+"&SortExpression=DomainName_ASC"
        r=requests.get(uri)
        soup = BeautifulSoup(r.text)
        lis=soup.find("span",{'id':"ctl00_ctl00_ctl00_ctl00_base_content_web_base_content_home_content_page_content_left_ctl05_ctl00_pagerControl_Page_PageNumberDisplayDiv"})
        last_page= int(lis.find("li","last").find("a").get_text())
        print "Total %s pages" % last_page
        total_domains=0
        for page in xrange(1,last_page+1):
            domains=0
            uri=r'https://www.namecheap.com/domains/marketplace/buy-domains.aspx?page='+str(page)+r'&size=100&excludehypen=false&excludenumber=false&adultlisting=true&priceRange='+str(price_min)+"%3a"+str(price_max)+'&SortExpression=DomainName_ASC'
            r = requests.get(uri)
            doc=r.text
            soup = BeautifulSoup(doc)
            no_items=soup.find(text='There are no items to display') is not None
            if no_items: break
            print "Parsing page %s of %s..." %(page,last_page)
            group = soup.findAll("li", "group")
            for g in group:
                domain= g.contents[1].find("a").get_text().strip()
                price=g.contents[-2].find("span").get_text().strip()
                s="%s\n"%(domain)
                f.write(s)
                domains+=1
            #print "%s domains" % domains
            total_domains+=domains
        time.sleep(DELAY)
    print "Done, %s domains total." % total_domains
