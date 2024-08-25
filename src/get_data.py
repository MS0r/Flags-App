import requests
import os
import re
import io
from PIL import Image
from bs4 import BeautifulSoup as b
from datetime import datetime
from paths import flags_path


WIKIURL = 'https://en.wikipedia.org'
ISOURL = 'https://en.wikipedia.org/wiki/ISO_3166-1'
HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'}


def make_directory(path : str):
    if not os.path.exists(path):
        os.mkdir(path)

def timer(time : datetime,secondtimer : int):
    now = datetime.now()
    if now.hour > time.hour or now.minute > time.minute or now.second > time.second:
        print('\rCreating Flags and doing things ' + '.'*secondtimer + '   ', end='')
        secondtimer = secondtimer + 1 if secondtimer < 3 else 1
        time = now
    return [time,secondtimer]
    
def find_population(href : str):
    aux = WIKIURL + href
    req = requests.get(aux).content
    asop = b(req,"lxml")
    tbody = asop.find('table',{'class':'infobox'})
    pol = False
    try:
        population = tbody.find(string="Population")
        if population != None:
            pol = population.find_next("td",{"class":"infobox-data"})
            pol_number = re.search(r'(\d|,)+(\d|,)*',pol.get_text())[0]
            try:
                int(pol_number.replace(',',''))
            except:
                pol_number = 'N/A'
        else:
            pol_number =  'N/A'
    except Exception as e:
        print(e)
        raise

    return pol_number
    


def get_flags_url():
    # First we get our flags from this wikipedia's url
    isocontent = requests.get(ISOURL).content
    time = datetime.now()
    secondtimer = 1
    # Using beautifulsoup to pull out our data using lxml parser
    soup = b(isocontent,"lxml")
    soup = soup.find('caption').find_previous('table')
    flags = {}
    make_directory(flags_path)
    # Now we go through the data searching for each <tr> markup
    # Finding our image in <img> markup and getting a better image quality
    # And finallly saving our image url in a dict with its name as a key
    for country in soup.findAll("tr"):
        contry = country.find('a')
        if contry != None and 'title' in contry.attrs and 'ISO' not in contry['title'] and 'Letter' not in contry['title']:
            img = 'https:' + country.find('img')['src'].replace('23px','50px')
            try:
                img_path = os.path.join(flags_path,contry['title'] + '.png')
                flags[contry['title']] = {'href' : contry['href'],'img' : img_path,'used' : 'False'}
                flags[contry['title']]['population'] = find_population(contry['href'])

                if os.path.exists(img_path):
                    continue
                r = requests.get(img,headers=HEADERS)
                fil = io.BytesIO(r.content)
                img = Image.open(fil)
                img.save(img_path)
                time, secondtimer = timer(time,secondtimer)
                

            except Exception as e:
                print(contry.attrs)
                raise        
    return flags