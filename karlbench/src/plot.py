import json
import sys
import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, List

Disk = { "label": str, "mountpoint": str }
Series = Tuple[List[float], List[float], str]
Benchmark = List[Tuple[Disk, List[Tuple[Series, Series]]]]

def main():
    benchmark_data: Benchmark = json.load(sys.stdin)

    num_charts = len(benchmark_data) * 2
    rows = int(np.ceil(np.sqrt(num_charts)))
    cols = int(np.ceil(num_charts / rows))

    fig, axes = plt.subplots(rows, cols)
    axes = [axes] if num_charts == 1 else axes.flatten()

    for i, (chart_info, ax) in enumerate(zip(benchmark_data, axes)):
        metadata = chart_info[0]
        data = chart_info[1]

        for series in np.array(data).flatten():
            x_values = series[0]
            y_values = series[1]
            series_label = series[2]
            ax.plot(x_values, y_values, label=series_label)

        ax.set_xlabel("Zeit in Sekunden")
        ax.set_ylabel("Geschriebene Daten in Bytes")
        ax.legend()

        ax.set_title(metadata["label"])

    # Hide any unused subplots
    for j in range(num_charts, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()

    try:
        plt.show()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
