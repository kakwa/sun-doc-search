# sun-doc-search

## Description

Client-side search + indexer for the Sun/Oracle System Handbook.

## Setup

- Install beautifulsoup:

```bash
# pick your poison of choice
sudo apt install python3-bs4
sudo dnf install python3-beautifulsoup4
sudo pacman -S python-beautifulsoup4
sudo emerge dev-python/beautifulsoup4
doas pkg_add py3-beautifulsoup4
pip install beautifulsoup4
pip3 install beautifulsoup4
```

- Go to the root of the documentation & download the assets:

```bash
SUN_DOC_PATH="/path/to/your/doc"
cd ${SUN_DOC_PATH}

wget -O Search.html https://raw.githubusercontent.com/kakwa/sun-doc-search/main/Search.html
wget -O genindex.py https://raw.githubusercontent.com/kakwa/sun-doc-search/main/genindex.py
```

- Generate the index generator script (/!\ RAM intensive):

```bash
python3 genindex.py
ls -lh search-index.json
```

Serve the documenation directory `SUN_DOC_PATH` statically.

The search page should now be available at `/Search.html`.

## License

Released under MIT.
