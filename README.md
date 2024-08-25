**Flags_App** is a personal project for my instagram account, where i try to put a flag each day, without repeating any of them, but it will be difficult to know which of them have been used and which of them have not been used, then with this application I cant repeat any flag.

This app used the wikipedia page for the standard which define the codes for representation of names of countries and their subdivisions, [ISO3166-1](https://en.wikipedia.org/wiki/ISO_3166-1), where it gets the name and flags from each country found in the standard, apart, it looks on each country's wikipedia page if more information is required, like the population information provided in each page.

to use it locally, just use the following commands.

```shell
pip install -r requirements.txt
```

```shell
python __main__.py
```

It will take almost 2 minutes to charge all images and the information from each country found on the ISO

The database classes and the countries classes are based on the python library [pycountry](https://github.com/pycountry/pycountry).
