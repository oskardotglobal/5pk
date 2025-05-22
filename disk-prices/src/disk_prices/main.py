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
    return zip(*sorted_data)  # Returns two iterators for capacities and prices


def main():
    scraper = DiskDrivesScraper()

    with open("response.html", "r") as f:
        html = f.read()
        soup = BeautifulSoup(html, "lxml")

    # Parse data - fixed price parsing and proper float conversion
    data = []
    for item in scraper.getDiskDicts(soup) or []:
        try:
            if "x" in item.get("Capacity", ''):
                continue

            price_str = item.get('Price\xa0per\xa0GB', '').replace('$', '').strip()
            
            capacity = (
                float(item.get("Capacity", '').replace(' TB', '').strip()) * 1000
                if "TB" in item.get("Capacity", '')
                else float(item.get("Capacity", '').replace(' GB', '').strip())
            )

            tech = item.get("Technology", '').strip()

            if price_str and capacity and tech:
                price_per_gb = float(price_str)

                if price_per_gb > 2:
                    continue

                data.append((price_per_gb, capacity, tech))
        except (ValueError, AttributeError):
            continue

    print(data)

    # Process data - ensure we're passing correct (capacity, price) tuples
    hdd_data = [(y, x) for (x, y, tech) in data if tech == "HDD"]  # (capacity, price)
    ssd_data = [(y, x) for (x, y, tech) in data if tech != "HDD"]  # (capacity, price)

    # Unpack the processed data properly
    x1, y1 = process_data(hdd_data) or ([], [])
    x2, y2 = process_data(ssd_data) or ([], [])

    # Convert to lists in case zip objects are exhausted
    x1, y1 = list(x1), list(y1)
    x2, y2 = list(x2), list(y2)

    # Create plot
    plt.style.use("dark_background")

    plt.figure(figsize=(10, 6))
    
    plt.plot(x1, y1, marker='o', linestyle='None', color="red", label="HDDs")
    plt.plot(x2, y2, marker='s', linestyle='None', color="blue", label="SSDs")
   
    # plt.gca().xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

    plt.title("Durchschnittspreise für neue Festplatten (amazon.com)")
    plt.xlabel("Kapazität (GB)")
    plt.ylabel("Preis pro GB (USD)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.show()

