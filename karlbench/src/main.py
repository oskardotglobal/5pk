from platform import system
from random import randint
from tempfile import mktemp

from plumbum import FG, local
from plumbum.cli.terminal import ask, choose
from plumbum.cmd import dd, ls, grep, rm, sudo


class Benchmark:
    blocksize_mb: int
    blocks: int
    seek: int = 0

    def __init__(self, blocksize_mb=1, blocks=1024, random=False):
        self.blocksize_mb = blocksize_mb
        self.blocks = blocks

        if random:
            self.seek = round(randint(1, 1024 ** 4 * 100) / (self.blocksize_mb * 1024 ** 3))

    def dd(self, input: str, of: str, bs_mb: int, sudo=False, **kwargs: str | int):
        kwargs |= { "if": input, "of": of, "bs": f"{bs_mb}M" }
        args = list(map(lambda item: f"{item[0]}={item[1]}", kwargs.items()))

        if sudo:
            return local["sudo"][dd[*args]] & FG

        return dd[*args] & FG

    def run(self, disk: str):
        input = mktemp("input.bin")
        output = mktemp("output.bin")

        try:
            self.dd(
                bs_mb=self.blocksize_mb,
                count=self.blocks,
                of=input,
                input="/dev/urandom",
                status="progress",
            )

            self.dd(
                bs_mb=self.blocksize_mb,
                count=self.blocks,
                input=input,
                oseek=self.seek,
                of=disk,
                conv="sync,noerror",
                status="progress",
                sudo=True,
            )

            self.dd(
                bs_mb=self.blocksize_mb,
                count=self.blocks,
                input=disk,
                iseek=self.seek,
                of=output,
                conv="sync,noerror",
                status="progress",
                sudo=True,
            )
        finally:
            _ = rm["-f"][input] & FG
            _ = sudo[rm["-f"][output]] & FG



def list_disks() -> list[str]:
    re: str | None = None

    match system():
        case "Linux":
            raise NotImplementedError("TODO")
        case "Darwin":
            re = "^disk[0-9]$"
        case _:
            raise NotImplementedError("Use macOS or Linux you clown")

    return list(map(lambda dev: f"/dev/{dev}", (ls["/dev"] | grep["-E"][re])().strip().split("\n")))

def main():
    path = choose("Which disk should we write to?", list_disks())
    ok = ask(f"Confirm writing to {path}? This will permanently delete all data from the disk.", default=False)

    if not ok:
        print("Exiting!")
        return

    benchmark = Benchmark(random=True)
    benchmark.run(path)


if __name__ == "__main__":
    main()
