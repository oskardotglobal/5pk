from collections.abc import Callable
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt, ticker
from collections import defaultdict

from .scraper import DiskDrivesScraper


def process_data(data: list[tuple[float, float]]) -> tuple[list[float], list[float]]:
    capacity_dict = defaultdict(list)
    for cap, price in data:
        capacity_dict[cap].append(price)

    sorted_data = sorted([(cap, sum(prices)/len(prices)) for cap, prices in capacity_dict.items()])
    if not sorted_data:
        return [], []
    return zip(*sorted_data) 


def parse_data(input: list[dict], y_key: str, process_y: Callable[[str], float | None]) -> tuple[list[float], list[float], list[float], list[float]]:
    data = []
    for item in input or []:
        try:
            if "x" in item.get("Capacity", ''):
                continue

            y = process_y(item.get(y_key, ''))
            
            capacity = (
                float(item.get("Capacity", '').replace(' TB', '').strip()) * 1000
                if "TB" in item.get("Capacity", '')
                else float(item.get("Capacity", '').replace(' GB', '').strip())
            )

            tech = item.get("Technology", '').strip()

            if y and capacity and tech:
                data.append((capacity, y, tech))
        except (ValueError, AttributeError):
            continue

    x1, y1 = process_data([(x, y) for (x, y, tech) in data if tech == "HDD"]) or ([], [])
    x2, y2 = process_data([(x, y) for (x, y, tech) in data if tech != "HDD"]) or ([], [])

    return x1, y1, x2, y2

def main():
    scraper = DiskDrivesScraper()

    with open("response.html", "r") as f:
        html = f.read()
        soup = BeautifulSoup(html, "lxml")

    data = scraper.getDiskDicts(soup)[:-5] 


    plt.style.use("dark_background")
    
    # Create figure with 2 subplots (1 row, 2 columns)
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    ax1.set_title("Durchschnittspreise für neue Festplatten (amazon.com)")
    ax1.set_xlabel("Kapazität (GB)")
    ax1.set_ylabel("Preis pro GB (USD)")
    ax1.grid(True, linestyle='--', alpha=0.7)

    x1, y1, x2, y2 = parse_data(
        data,
        'Price\xa0per\xa0GB',
        lambda ppg: float(ppg.replace('$', '').strip())
    )

    ax1.plot(x1, y1, marker='o', linestyle='None', color="red", label="HDDs")
    ax1.plot(x2, y2, marker='s', linestyle='None', color="blue", label="SSDs")
    ax1.legend()

    ax2.set_title("Durchschnittspreise für neue Festplatten (amazon.com)")
    ax2.set_xlabel("Kapazität (GB)")
    ax2.set_ylabel("Preis (USD)")
    ax2.grid(True, linestyle='--', alpha=0.7)

    x1, y1, x2, y2 = parse_data(
        data,
        'Price',
        lambda price: float(price.replace('$', '').strip())
    )

    ax2.plot(x1, y1, marker='o', linestyle='None', color="red", label="HDDs")
    ax2.plot(x2, y2, marker='s', linestyle='None', color="blue", label="SSDs")
    # ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax2.legend()

    plt.tight_layout()
    
    try:
        plt.show()
    except KeyboardInterrupt:
        pass

