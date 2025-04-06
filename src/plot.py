import sys
import json
import matplotlib.pyplot as plt


def main():
    runs = json.load(sys.stdin)
    fig, ax = plt.subplots()

    for x, y, label in runs:
        ax.plot( x, y, label=label)

    ax.set_xlabel("Zeit in Sekunden")
    ax.set_ylabel("Geschriebene Daten in Bytes")
    plt.legend()

    try:
        plt.show()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
