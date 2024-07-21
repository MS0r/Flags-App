import requests
import os
import re
import io
from PIL import Image
from bs4 import BeautifulSoup as b
from datetime import datetime
from paths import flags_path

def make_directory(path : str):
    if not os.path.exists(path):
        os.mkdir(path)

def print_wait(second : int):
    print('\rCreating Flags and doing things ' + '.'*second + '   ', end='')

def get_flags_url():
    # First we get our flags from this wikipedia's url
    cwd = os.getcwd()
    wikiurl = 'https://en.wikipedia.org/wiki/ISO_3166-1'
    toget = 'https://en.wikipedia.org'
    flagswiki = requests.get(wikiurl).content
    time = datetime.now()
    tim = 1
    # Using beautifulsoup to pull out our data using lxml parser
    soup = b(flagswiki,"lxml")
    soup = soup.find('caption').find_previous('table')
    flags = {}
    make_directory(flags_path)

    # Now we go through the data searching for each <tr> markup
    # Finding our image in <img> markup and getting a better image quality
    # And finallly saving our image url in a dict with its name as a key
    for country in soup.findAll("tr"):
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'}
        contry = country.find('a')
        if contry != None and 'title' in contry.attrs and 'ISO' not in contry['title'] and 'Letter' not in contry['title']:
            img = 'https:' + country.find('img')['src'].replace('23px','50px')
            try:
                # print('Add Flag for ' + contry['title'])
                img_path = os.path.join(flags_path,contry['title'] + '.png')
                flags[contry['title']] = {'href' : contry['href'],'img' : img_path,'used' : 'False'}
                if os.path.exists(img_path):
                    continue
                r = requests.get(img,headers=headers)
                fil = io.BytesIO(r.content)
                img = Image.open(fil)
                img.save(img_path)
                now = datetime.now()
                if now.hour > time.hour or now.minute > time.minute or now.second > time.second:
                    print_wait(tim)
                    tim = tim + 1 if tim < 3 else 1
                    time = now
            except Exception as e:
                print(contry.attrs)
                raise        

    for contry in flags:

        aux = toget + flags[contry]['href']
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
                flags[contry]['population'] = pol_number
                now = datetime.now()
                if now.hour > time.hour or now.minute > time.minute or now.second > time.second:
                    print_wait(tim)
                    tim = tim + 1 if tim < 3 else 1
                    time = now
            else:
                flags[contry]['population'] = 'N/A'
        except Exception as e:
            print(e, contry)
            raise

    return flags