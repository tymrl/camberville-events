# camberville-events

A script that scrapes the websites of different venues in the Cambridge/Somerville area and aggregates events.

## Usage

To use the script, simply run `python events.py` in an python3 environment where [arrow](https://arrow.readthedocs.io/en/latest/), [requests](https://docs.python-requests.org/en/latest/), and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) are installed. Exact versions are listed in requirements.txt. For best results, use a virtual environment.

This script uses [argparse](https://docs.python.org/3/library/argparse.html) to create a command line interface. For help using the CLI, run `python events.py -h`.
