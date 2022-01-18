# Scrapy bots for crawling data from [muasamcong website](http://muasamcong.mpi.gov.vn/)

## To start crawling data
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

## Start crawl in terminal
- Config your spiders in bid_scrape/bid_scrape/spiders/config.yaml file
  - Range of pages you want to crawl data
  - Collection name you want to save into database

- Run bid_scrape/main.py file to start crawl data

## Start crawl in UI
- Run bid_scrape/tkinter_app
- We have 2 modes, crawl single page and crawl multi pages continuously

# Maintenance
- New scrapy bot: Add its name to OPTION variable in tkinter_app.py to crawl in UI ![alt](/back-end/bid_scrape/assets/images/options.png)
