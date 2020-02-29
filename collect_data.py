try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

import csv 
import json
import time 
import uuid
import os
import datetime


class Scraper:
    
    def __init__(self,orig_filename,skustart):
        self.visited = set()
        self.session = requests.Session()
        self.session.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36"}
        self.level = 1
        self.skustart = skustart
        requests.packages.urllib3.disable_warnings()  # turn off SSL warnings
        self.orig_filename = orig_filename
        self.domain = ''
        self.category = ''

    def visit_url(self, url, level,category):
        #print(url)
        if url in self.visited:
            return

        self.visited.add(url)
        self.level = level
        self.category = category
       
        parsed_uri = urlparse( url )
        tempdomain = parsed_uri.netloc
        #print(tempdomain)
        #return
        tempdomain = tempdomain.replace("www.", "").replace(".com", "").replace("www2.", "").replace(".ae", "").replace("eu.", "").replace("en-ae.", "").replace("shop.", "").replace("uk.", "")
        self.domain = tempdomain
        
        rows = []
        
       
        rows = self.zara(url)
        
            
           #return
        #return
        #with open(filename, 'a', encoding='utf-8') as toWrite:
        print(self.domain)
        filename = 'new_'+self.orig_filename
        
        if not rows:
            print("List is empty  "+str(level))
            return
        #return
        print("Done  "+str(level))
        #skutemp = self.skustart+level
        
        #sku = self.orig_filename.replace(".csv", "")+'-'+str(skutemp)
        #rows[0].append(sku)
        rows[0].append(self.domain)
        rows[0].append(self.orig_filename)
        #print(sku)
        print(rows)
        with open(filename, 'a', newline='', encoding='utf-8') as toWrite:
        #with open(filename, 'a', encoding='utf-8') as toWrite:
        #with open(filename, 'a', newline='') as toWrite:
            writer = csv.writer(toWrite)
            writer.writerows(rows)
            
                

                
    
    
    def zara(self,url):
		
		
		#content = requests.get(url).text
        driver = webdriver.Firefox()
        driver.get(url)

        content = driver.page_source
        
        soup = BeautifulSoup(content, "lxml")
        
        
        #stock = soup.find_all("div", class_="outOfStockMessages stockAvailability")
        #print(len(stock))
        #if len(stock) > 0 :
        #    return
        
        name_html = soup.find('h1', attrs={'class': 'product-name'})
        if(name_html):
            name_html.find('span', {'class': 'offleft'}).replace_with('')
            #name_html = name_html.find('span').replace_with('')
            #print(name_html)
            name = name_html.text
            #name = name.strip('Details')
            name = name.strip()
        #print(name)
        
        prname = name.lower().replace(" ", "_")
        #prname = str(self.level)+'_'+prname
        prname = str(self.level)
        basedir = self.orig_filename.replace(".csv", "")
        imagedirectory = basedir+ "/"+self.domain+'/'+prname+'/'
        
        pimages = soup.find_all("a",{"class":"_seoImg"})
        imagelists = []
        color_value = []
        size_value = []
        productcode = ''
        
        #print(pimages)
        #return
		
		
        for img in pimages:
            #images = img.find("img")
            image_src = img["href"]
            image_url = image_src
            
            #image_url = image_url.strip('xs:')
            
        
            #image_url = image_url.split("?")[0]
            if not image_url.startswith(("data:image", "javascript")):

                imgurltopass = urljoin(url, image_url)
                imagepath = imgurltopass.split('/')[-1].split("?")[0]
            
                imagefullpath = imagedirectory + imagepath
                imagename = self.download_image(imgurltopass,imagefullpath)
                
                #imagename = self.download_image(urljoin(url, image_url))
                imagelists.append(imagename)
        imageliststring =  ','.join(imagelists)
        #print(imageliststring)
        
              
        
        
        
        brand = 'zara'
            
        price_html = soup.find('div', attrs={'class': '_product-price'})
        #print(price_html)
        #return
        if(price_html):
            
            #brand = brand_html.find('span').replace_with('')
            price = price_html.text
            price = price.strip()
            #print(price)
        
        #print(bar.text)
       
        #return
        productcode_html = soup.find('span', attrs={'data-qa-qualifier': 'product-reference'})
        if productcode_html :
            productcode = productcode_html.text
        now = datetime.datetime.now()
        uidwithtime = now.strftime("%Y%m%d%H%M%S")
        sku = 'zara-'+uidwithtime+'-'+productcode
        
        colorcontainer = soup.find('p', attrs={'class': 'product-color'})
        if(colorcontainer):
            desc = colorcontainer.prettify()
        desc_html = soup.find('div', attrs={'id': 'description'})
        #print(desc.prettify())
        if(desc_html):
            #desc_html = desc_html.find('<a').replace_with('')
            desc += desc_html.prettify()
        #print(desc)
        color = soup.find('span', attrs={'class': '_colorName'})
        if color :
            color_value = color.text
        #print(color_value)
        
        
        sizecontainer = soup.find('div', attrs={'class': 'size-select'})
        if sizecontainer:
            size = sizecontainer.find_all('label', attrs={'class': 'product-size'})
            if size :
                
                for label in size:
                    if 'disabled' not in label['class'] and 'back-soon' not in label['class']:
                        token = label.find('span',attrs={'class': 'size-name'}).text
                        size_value.append(token.strip())
                    #print(token.strip())
        #if level > 0:
            #for link in soup.select("a[href]"):
                #self.visit_url(urljoin(url, link["href"]), level - 1)
        #return 
        #print(size_value)
        #return
        rows = []
        if not color_value:
            colorsting = ''
        else:
            colorsting = color_value
        if not size_value:
            sizesting = ''
        else:
            sizesting = ', '.join(size_value)
        rows.append([name, price, desc, brand, self.category, colorsting, sizesting, imageliststring, url, productcode, sku])
        #print(rows)
        return rows
        
        
        
    
        

    def download_image(self, image_url,imagefullpath):
        #print(image_url)
        #self.i = self.i + 1
        #print(self.i)
        #image_url = '//images.selfridges.com/is/image//selfridges/167-2001606-518215TAV37_BLACK_ALT02'
        #local_filename = image_url.split('/')[-1].split("?")[0]
        #local_filename =   'hm_{}.jpg'.format(int(time.time()))  
        #local_filename = 'sm/hm'+str(uuid.uuid4())+'.jpg'
        #return local_filename
        #return imagefullpath
        r = self.session.get(image_url, stream=True, verify=False)
        os.makedirs(os.path.dirname(imagefullpath), exist_ok=True)
        with open(imagefullpath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
        return imagefullpath



if __name__ == '__main__':
    csvfile = 'ZARA-18-12-18.csv'
    skustart = 3650
    scraper = Scraper(csvfile,skustart)
    with open(csvfile, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            lineNum = spamreader.line_num
            #scrapurl = ', '.join(row)
            scrapurl = row[3]
            #print(row[2])
           
            
            category = row[0]
            if(row[1]):
                category = category +','+ row[1]
            if(row[2]):
                category = category +','+row[2]
            print(scrapurl)
            #scraper.visit_url('http://www.selfridges.com/GB/en/cat/balenciaga-logo-print-cotton-jersey-hoody_167-2001606-518215TAV37', 1)
            #rowarray = [6,18,19,23,33,34]
            if(lineNum > 0 ):
                scraper.visit_url(scrapurl, lineNum, category)
                time.sleep(5)
                
