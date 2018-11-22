# Tashbeek

The matching algorithm for the IRC's Project Match

![](https://media.giphy.com/media/dh2XvZthDl7ag/giphy.gif)

## Python Notebook Setup

To setup, create and activate a virualenv and then run

`pip install -r requirements.txt`

### Run

`jupyter notebook`

## API Setup & Run

To run the API, you should have [docker](https://www.docker.com/) and
[docker-compose](https://docs.docker.com/compose/) installed. Once installed...

`docker-compose up`

For the API docs/contract, we use [API blueprint](https://apiblueprint.org/)
and personally, I prefer [agilo](https://github.com/danielgtaylor/aglio) for
reading the contract. 

Simply `cd api` and `agilo -i contract.apib -s` and view it in your web
browser.
