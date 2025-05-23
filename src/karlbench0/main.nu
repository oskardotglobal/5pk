#!/usr/bin/env nu

use lists.nu *

def sudo [command: string] {
    ^sudo nu --stdin --commands $command
}

def benchmark [file: string] {
    rm -f ./benchmark.json

    let args = [
        "--size" "1GB"
        "--cycles" 10
        "--blocksize" "16MB"
        "--mode" "all"
        # Report as json
        "--no-chart"
        "--export-json" "./benchmark.json"
        # Don't fuck with block devices
        "--no-create"
        "--no-delete"
    ]

    [$args, [...$args, "--random-seek"]]
    | each { |args|
        ^sudo simple-disk-benchmark ..$args $file
    }

    open ./benchmark.json
}

def main [] {
    [
        {
            label: "Externe HDD",
            mountpoint: "/dev/disk5",
        }
        # {
        #     label: "Externe SSD",
        #     mountpoint: "/Volumes/SSD/",
        # }
    ]
    | each { |disk|
        let runs = benchmark $disk.mountpoint
            | select options runs
            | flat-map { |benchmark|
                map $benchmark.runs { |$run| {run: $run, options: $benchmark.options} }
            }
            | each { |benchmark|
                let mode = match [$benchmark.run.mode, $benchmark.options.random_seek] {
                    ["Read", false] => "Bytes gelesen",
                    ["Write", false] => "Bytes geschrieben",
                    ["Read", true] => "Bytes gelesen (Zufälliges Suchen)",
                    ["Write", true] => "Bytes geschrieben (Zufälliges Suchen)"
                }

                let time = $benchmark.run.cycle_results
                    | get elapsed
                    | sum

                let bytes_over_time = [
                    $time
                    (
                        $benchmark.run.cycle_results
                        | get bytes
                        | sum
                    )
                    $mode
                ]

                let bytes_per_second_over_time = [
                    $time
                    (
                        $benchmark.run.cycle_results
                        | each { |cycle| $cycle.bytes / $cycle.elapsed }
                    )
                    ($mode | str replace "Bytes" "Bytes pro Sekunde")
                ]

                [$bytes_over_time, $bytes_per_second_over_time]
            }

        [$disk, $runs]
    }
    | to json
    | ^uv run ($env.FILE_PWD | path join "plot.py")

    rm -f ./benchmark.json
}
