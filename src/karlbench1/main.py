from platform import system
from random import randint
from re import finditer
from typing import TypedDict
from math import ceil

from plumbum import FG, TEE, local
from plumbum.cli.terminal import ask, choose
from plumbum.cmd import dd, ls, grep, rm, cmp
from matplotlib import pyplot as plt


class Chart(TypedDict):
    title: str
    xlabel: str
    ylabel: str

    xs: list[list[float]]
    ys: list[list[float]]
    

class Benchmark:
    blocksize_mebibytes: int
    blocks: int
    seek: int = 0
    stdout: str = ""
    arch: str = ""

    def __init__(self, blocksize_mebibytes=1, blocks=1024, seek=False, arch: str = ""):
        self.blocksize_mebibytes = blocksize_mebibytes
        self.blocks = blocks

        if arch != "":
            self.arch = f" ({arch})"

        if seek:
            self.seek = randint(1, 1024 * 200)


    def dd(self, input: str, of: str, bs_m: int, sudo=False, **kwargs: str | int):
        kwargs |= { "if": input, "of": of, "bs": f"{bs_m}M" }
        args = list(map(lambda item: f"{item[0]}={item[1]}", kwargs.items()))

        if sudo:
            return local["sudo"][dd[*args]] & TEE

        return dd[*args] & TEE


    def verify(self, input: str, output: str, sudo=False):
        args = [
            "--print-bytes",
            f"--bytes={self.blocksize_mebibytes * 1024 ** 2}",
            f"--ignore-initial=0:{self.seek}",            
            input,
            output
        ]

        if sudo:
            return local["sudo"][cmp[*args]] & FG

        return cmp[*args] & FG


    def run(self, disk: str):
        input = f"/tmp/input-{randint(1111, 9999)}.bin"

        try:
            self.dd(
                bs_m=self.blocksize_mebibytes,
                count=self.blocks,
                of=input,
                input="/dev/urandom",
                status="progress",
            )

            _, _, stdout = self.dd(
                bs_m=self.blocksize_mebibytes,
                count=self.blocks,
                input=input,
                oseek=self.seek,
                of=disk,
                conv="sync,noerror",
                status="progress",
                sudo=True,
            )

            self.stdout = stdout 
            self.verify(input, disk, sudo=True)
        except Exception:
            print("Subcommand threw an error, continuing...")
        finally:
            _ = rm["-f"][input] & FG
        

    def into_plot_input(self, disk: str) -> list[Chart]:
        if self.stdout == "":
            return []

        step_regex = r"\r(?P<bytes>\d+) bytes \([0-9,]+ [kMG]B, [0-9,]+ [KMG]iB\) copied, (?P<seconds>[0-9,]+) s, (?P<speed>[0-9,]+) (?P<unit>[kMG])B/s"
        lines = list(filter(None, self.stdout.split("\n")))
        
        bytes = []
        bps = []
        seconds = []

        for result in finditer(step_regex, lines[0]):
            factor = 1000 ** {
                "G": -1,
                "M": 0,
                "k": 1
            }.get(result.group("unit"), 0)

            seconds.append(float(result.group("seconds")))
            bytes.append(float(result.group("bytes")) / 1000 ** 2)
            bps.append(float(result.group("speed").replace(",", ".")) / factor)

        return [
            { "xs": [seconds], "ys": [bytes], "xlabel": "Zeit in Sekunden", "ylabel": "Daten in Megabyte", "title": f"Bytes {'zufällig' if self.seek > 0 else 'sequenziell'} geschrieben auf {disk}{self.arch}" },
            { "xs": [seconds], "ys": [bps], "xlabel": "Zeit in Sekunden", "ylabel": "Geschwindigkeit in Megabyte pro Sekunde", "title": f"{'Zufällige' if self.seek > 0 else 'Sequenzielle'} Schreibgeschwindigkeit für {disk}{self.arch}" }
        ]

def list_disks() -> list[str]:
    re: str | None = None

    match system():
        case "Linux":
            re = "^((nvme[0-9]n[1-9])|((s|h)d[a-z]))$"
        case "Darwin":
            re = "^disk[0-9]$"
        case _:
            raise NotImplementedError("Use macOS or Linux you clown")

    return list(map(lambda dev: f"/dev/{dev}", (ls["/dev"] | grep["-E"][re])().strip().split("\n")))


def main():
    try:
        disk = choose("Which disk should we write to?", list_disks())
        arch = choose("What kind of drive is this?", ["HDD", "SSD"])
        ok = ask(f"Confirm writing to {disk}? This will permanently delete all data from the disk.", default=False)

        if not ok:
            print("Exiting!")
            return

        charts: list[Chart] = []

        for seek in {False, True}:
            benchmark = Benchmark(seek=seek, arch=arch, blocksize_mebibytes=16, blocks=64)
            runs = []

            for id in range(1, 4):
                print(f"Starting run {id}")

                benchmark.run(disk)
                runs += benchmark.into_plot_input(disk)
            
            for run in runs:
                try:
                    chart = [chart for chart in charts if chart and chart.get("title", "") == run["title"]][0]
                    
                    chart["xs"] += run["xs"]
                    chart["ys"] += run["ys"] 
                except IndexError:
                    charts.append(run)

        plt.style.use("dark_background")
        
        _, axis = plt.subplots(ceil(len(charts) / 2), min(len(charts), 2), figsize=(16, 6))
        axis = list(axis.flatten())

        for (i, chart) in enumerate(charts):
            ax = axis[i]
         
            ax.set_title(chart["title"])
            ax.set_xlabel(chart["xlabel"])
            ax.set_ylabel(chart["ylabel"])
            ax.grid(True, linestyle='--', alpha=0.7)

            for (i, x) in enumerate(chart["xs"]):
                ax.plot(x, chart["ys"][i], label=f"Run {i + 1}")

            ax.legend()
        
        plt.tight_layout()
        plt.savefig("out.png")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
