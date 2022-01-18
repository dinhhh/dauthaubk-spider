import logging
import os
from datetime import datetime
import json
from bid_scrape.spiders.spider_utils import DATE_TIME_FORMAT_FOR_OUTPUT_FILE


def merge_json_file(start_time, end_time, directory_in_str, merged_file_name):
    logging.info(f"Start merge json file in {directory_in_str}, start time {start_time}, end time {end_time}")
    directory = os.fsencode(directory_in_str)

    merged_data = list()
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".json"):
            json_suffix_length = 5
            print(f"Start merge file {filename[:-5]}")
            try:
                file_name_date_time = datetime.strptime(filename[:-5], DATE_TIME_FORMAT_FOR_OUTPUT_FILE)
                if start_time < file_name_date_time < end_time:
                    with open(filename, 'r', encoding='utf8') as infile:
                        merged_data.extend(json.load(infile))
                else:
                    logging.info(f"Not merge file {filename} because of time constraint")
            except:
                logging.info(f"{filename} does not match format {DATE_TIME_FORMAT_FOR_OUTPUT_FILE}")

    with open(merged_file_name, 'w', encoding='utf8') as output_file:
        json.dump(merged_data, output_file, ensure_ascii=False)


if __name__ == '__main__':
    print(os.path.dirname(os.path.abspath(__file__)))
    merge_json_file(datetime.now().replace(hour=8, minute=0, second=0),
                    datetime.now(),
                    os.path.dirname(os.path.abspath(__file__)), "merged.json")
