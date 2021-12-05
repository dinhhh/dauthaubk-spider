# Steps to run crawl data from muasamcong website
- Clone this project

`$ git clone https://github.com/dinhhh/DauThau-BK.git`

- Init virtual python environment

`$ cd back-end`

`$ python -m venv venv`

- Activate virtual environment

`$ source venv/bin/activate`
 
- Install requirements

`$ pip install -r requirements.txt`

- Change MONGO_URI and MONGO_DATABASE in settings.py to your mongo URI and your mongo database name

- Config your spiders in bid_scrape/bid_scrape/spiders/config.yaml file
  - Range of pages you want to crawl data
  - Collection name you want to save into database

- Run bid_scrape/main.py file to start crawl data