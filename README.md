# Tashbeek

The matching algorithm for the IRC's [Project Match](https://airbel.rescue.org/projects/employment-hub/)

![](https://media.giphy.com/media/HnnKLPMqsO12g/giphy.gif)

## Python Notebook Setup

To setup, create and activate a virualenv and then run

`pip install -r requirements.txt`

### Run

`jupyter notebook`

All of the notebooks are contained in the `notebook/` directory of this
repository

## API Setup & Run

To run the API, you should have [docker](https://www.docker.com/) and
[docker-compose](https://docs.docker.com/compose/) installed. Once installed...

`docker-compose up`


### Docs

For the API docs/contract, we use [API blueprint](https://apiblueprint.org/)
and personally, I prefer [agilo](https://github.com/danielgtaylor/aglio) for
reading the contract. 

Simply `cd api` and `agilo -i contract.apib -s` and view it in your web
browser.

You can find the latest stable docs at https://github.com/nolski/tashbeek
