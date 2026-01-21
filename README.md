**Flags_App** is a personal project for my instagram account, where i try to put a flag each day, without repeating any of them, but it will be difficult to know which of them have been used and which of them have not been used, then with this application I cant repeat any flag.

This app used the wikipedia page for the standard which define the codes for representation of names of countries and their subdivisions, [ISO3166-1](https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population), where it gets the name, flags and population from each country found in the standard.

to use it locally, we use [uv](https://github.com/astral-sh/uv) as project manager, just use the following commands.

```shell
uv venv .venv
uv sync
```

```shell
source .venv/bin/activate
python -m main
```

It will take less than 30 seconds to download all images and the information from each country found on the ISO

The database classes and the countries classes are based on the python library [pycountry](https://github.com/pycountry/pycountry).
