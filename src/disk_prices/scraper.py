from bs4 import BeautifulSoup
from urllib.parse import parse_qsl, urlencode
import json
import csv
import argparse
import sys
import requests

class DriveParser:
    """
    DriveParser parses the soup of the diskprices.com page
    """
    def __init__(self):
        pass

    def getTableHead(self, main_soup=None):
        """
        getTableHead searches for a table header in the specified soup

        :param main_soup: The page soup to look for the table header in
        :returns: a list of the headers in text format
        """
        if main_soup is None:
            return None

        main_table_elem = main_soup.select_one("table#diskprices")

        if main_table_elem is None:
            raise Exception("Could not find table.")

        table_head_elem = main_table_elem.select_one("tr#diskprices-head")

        if table_head_elem is None:
            raise Exception("Could not find table head.")

        table_headers_elem = table_head_elem.select("th")

        if table_headers_elem is None:
            raise Exception("Could not find table headers.")

        return [x.text for x in table_headers_elem]

    def getTableBodyElems(self, main_soup=None):
        """
        getTableBodyElems searches for the body of the table in the soup

        :param main_soup: is the soup to look for the table body in
        :return: returns the table body elements that are found and displayed
        """
        if main_soup is None:
            return None

        main_table_elem = main_soup.select_one("table#diskprices")

        if main_table_elem is None:
            raise Exception("Could not find main table element.")

        table_body_main_elem = main_table_elem.select_one("tbody#diskprices-body")

        if table_body_main_elem is None:
            raise Exception("Could not find table elements.")

        table_body_elems = table_body_main_elem.select("tr.disk")

        if table_body_elems is None:
            raise Exception("Could not find table elements.")

        # Filter out elements that aren't displayed via inline style identifiers
        filtered_elems = []
        for elem in table_body_elems:
            if 'style' not in elem.attrs or 'none' not in elem['style']:
                filtered_elems.append(elem)

        return filtered_elems

    def getDiskElemDetails(self, table_elem=None):
        """
        getDiskElemDetails finds the details of each element found in the table body

        :param table_elem: the element found in the table body
        :return: returns a list of elements that contain details of each specific table body element
        """
        details_elems = table_elem.select("td")

        if details_elems is None:
            return None

        return details_elems

    def createDiskDicts(self, table_elems=None, table_headers=None):
        """
        createDiskDicts formats the data found in the table into a collection of dictionaries

        :param table_elems: the elements found in the table body
        :param table_headers: the headers of the table
        :return: returns a list of dictionaries containing disk information scraped from the table
        """
        if table_elems is None or table_headers is None:
            return None

        disk_dicts = []
        for table_elem in table_elems:
            details_elems = self.getDiskElemDetails(table_elem)

            disk_dict = {}
            for header, detail in zip(table_headers, details_elems):
                disk_dict[header] = replaceCharsInText(detail.text).strip()

                if header.lower() == "name":
                    if "seagate" in detail.text.lower():
                        disk_dict["brand"] = "Seagate"
                    elif "toshiba" in detail.text.lower():
                        disk_dict["brand"] = "Toshiba"
                    elif "maxdigitaldata" in detail.text.lower():
                        disk_dict["brand"] = "MaxDigitalData"
                    elif "hgst" in detail.text.lower():
                        disk_dict["brand"] = "HGST"
                    elif (
                        "western digital" in detail.text.lower()
                        or "wd" in detail.text.lower()
                    ):
                        disk_dict["brand"] = "Western Digital"
                    elif "avoluxion" in detail.text.lower():
                        disk_dict["brand"] = "Avoluxion"
                    elif "avolusion" in detail.text.lower():
                        disk_dict["brand"] = "Avolusion"
                    elif "lacie" in detail.text.lower():
                        disk_dict["brand"] = "LaCie"
                    elif "owc" in detail.text.lower():
                        disk_dict["brand"] = "OWC"
                    elif "sandisk" in detail.text.lower():
                        disk_dict["brand"] = "SanDisk"
                    elif "buslink" in detail.text.lower():
                        disk_dict["brand"] = "BUSlink"
                    elif "crucial" in detail.text.lower():
                        disk_dict["brand"] = "Crucial"
                    elif "g-technology" in detail.text.lower():
                        disk_dict["brand"] = "G-Technology"
                    elif "kingston" in detail.text.lower():
                        disk_dict["brand"] = "Kingston"
                    elif "glyph" in detail.text.lower():
                        disk_dict["brand"] = "Glyph"
                    elif "micron" in detail.text.lower():
                        disk_dict["brand"] = "Micron"
                    else:
                        disk_dict["brand"] = "Unknown Brand"

                if header.lower() == "name":
                    disk_dict["url"] = detail.select_one("a").attrs["href"]

            disk_dicts.append(disk_dict.copy())

        return disk_dicts

class DiskDrivesScraper:
    """
    DiskDrivesScraper scrapes diskprices.com site data
    """
    def __init__(self):
        self.BASE_URL = "https://diskprices.com"
        self.SITE_PARSER = DriveParser()

    def getSoup(self, url=None):
        """
        getSoup uses selenium to get the page source & waits for the page javascript to format the data correctly before converting it into a bs4 object

        :param url: url to scrape from
        :return: returns the soup of the given url
        """
        if url is None:
            return None
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
        except Exception as e:
            print(e)
        else:
            return soup

    def parseUrlArgs(self, *args):
        """
        parseUrlArgs takes a list of arguments and parses and encodes them into a usable URL

        :param *args: a list of url arguments
        :return: returns an encoded url with sepcified arguments
        """
        params = {}
        for arg in args:
            temp = parse_qsl(arg)
            params[temp[0][0]] = temp[0][1]

        url_with_args = f"{self.BASE_URL}/?{urlencode(params)}"
        return url_with_args

    def getDiskDicts(self, soup=None):
        """
        getDiskDicts creates a list of dictionaries for every disk found on the website

        :param soup: the soup of the page to scrape
        :return: returns a list of dictionaries for every disk found
        """
        if soup is None:
            return None

        # get all headers
        headers = self.SITE_PARSER.getTableHead(soup)
        # get table body
        table_body_elems = self.SITE_PARSER.getTableBodyElems(soup)
        # combine headers and body elems
        disk_dicts = self.SITE_PARSER.createDiskDicts(table_body_elems, headers)

        return disk_dicts

def writeToJsonFile(dict_list=None, filename=None):
    """
    writeToJsonFile outputs the list of dictionaries into a JSON file

    :param dict_list: list of dictionaries to output
    :param filename: name to give the output file
    """
    if dict_list is None:
        return None

    if filename is None:
        filename = "test.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(dict_list, f)

    print(f"Saved data to json file: {filename}")

def writeToCSVFile(dict_list=None, filename=None):
    """
    writeToCSVFile creates a CSV file with the list of dictionaries

    :param dict_list: list of dictionaries
    :param filename: name to give the output file
    """
    if dict_list is None:
        return None

    if filename is None:
        filename = "test.csv"

    csv_file = open(filename, "w", encoding="utf-8")

    csv_writer = csv.writer(csv_file)

    count = 0

    for disk_dict in dict_list:
        if count == 0:
            header = disk_dict.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(disk_dict.values())

    csv_file.close()
    print(f"Saved data to csv file: {filename}")

def getAllDiskTypes():
    """
    getAllDiskTypes creates a list of all the possible disk types that can be used as arguments in the url

    :return: returns a list of all possible disk types
    """
    return 'external_hdd,external_hdd25,internal_hdd,internal_hdd25,internal_sshd,internal_sas,external_ssd,internal_ssd,m2_ssd,m2_nvme,u2,microsd,sd_card,cf_card,cfast_card,cfexpress,usb_flash,bdrw,bdr,dvdrw,dvdr,cdrw,cdr,lto3,lto4,lto5,lto6,lto7,lto8,lto9'.split(',')

def replaceCharsInText(text):
    """
    replaceCharsInText replaces chars in a string

    :param text: string to work on
    :return: returns string without certain chars
    """
    for ch in [",", ";"]:
        if ch in text:
            text = text.replace(ch, "")
    return text

def generateDateFilename():
    """
    generateDateFilename generates a filename based on date and time

    :return: returns a generated filename in 'diskprices-data_mm-dd-yyyy_hh·mm·ss' format
    """
    from datetime import datetime
    now = datetime.now()

    date_time = now.strftime('%m-%d-%Y_%H·%M·%S')
    return f'diskprices-data_{date_time}'

if __name__ == "__main__":
    disk_types_list = getAllDiskTypes()

    parser = argparse.ArgumentParser(
        prog="python main.py", description="Get disk drive information in JSON and CSV format", epilog='If you encounter any errors create an issue here https://github.com/badster-git/disk-prices-scraper/issues with the error. Thanks.'
    )

    # Unknown locales so can't set that option
    # parser.add_argument('-l', '--locale',action="store", type=str, help='set locale to ISO code', default='us')

    parser.add_argument('-t', '--type', action="store", type=str, choices=['tb', 'gb'], default='tb', help='set GB or TB format, uses TB by default')
    parser.add_argument('-c', '--condition',action="store", type=str, choices=['new', 'used', 'all'], help='set condition of drives to scrape, uses all by default', default='all')
    parser.add_argument('-mi', '--min',action="store",  type=int, help='set minimum drive capacity')
    parser.add_argument('-ma', '--max',action="store", type=int, help='set maximum drive capacity')
    parser.add_argument('-dt', '--disk-types',action="store", nargs='*', choices=disk_types_list, help='space separated list of disk types of disks to scrape, uses all by default. Allowed values are '+', '.join(disk_types_list), default=disk_types_list, metavar='')

    parsed_args = parser.parse_args()
    print('Scraping, please wait...')
    args_list = ['locale=us']
    capacity = ''

    for key,val in vars(parsed_args).items():
        if val is None: continue
        if key == 'disk_types':
            args_list.append(f'{key}={",".join(val)}')
        elif key == 'type': 
            if val == 'gb': args_list.append('units=gb')
            else: continue
        elif key == 'condition':
            if val == 'all': args_list.append(f'{key}=new,used')
            else: args_list.append(f'{key}={val}')
        elif key == 'max' or key == 'min':
            if key == 'max': 
                capacity += f'-{val}'
            else: 
                capacity += f'{val}-'
        else:
            args_list.append(f'{key}={val}')
    if bool(capacity): 
        if '--' in capacity: capacity = capacity.replace('--', '-')
        args_list.append(f'capacity={capacity}')

    dd_scraper = DiskDrivesScraper()
    url_with_params = dd_scraper.parseUrlArgs(*args_list)

    page_soup = dd_scraper.getSoup(url_with_params)
    disk_dict_list = dd_scraper.getDiskDicts(page_soup)
    
    if len(disk_dict_list) == 0: 
        print("Did not find any disks.")
        sys.exit()
    elif len(disk_dict_list) == 1: print(f"Found 1 disk.")
    else: print(f"Found {len(disk_dict_list)} disks.")

    filename_base = generateDateFilename()
    writeToJsonFile(disk_dict_list, f'{filename_base}.json')
    writeToCSVFile(disk_dict_list, f'{filename_base}.csv')
