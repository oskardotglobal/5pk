#!/usr/bin/env nu

def benchmark [] {
    rm -f ./benchmark.json

    let args = [
        "--size" "1GB"
        "--cycles" 10
        "--blocksize" "16MB"
        "--no-chart"
        "--export-json" "./benchmark.json"
    ]

    ["--random-seek", ""]
    | each { |x|
        ["write" "read"]
        | each { |y| if $x != "" { [$x "--mode" $y] } else ["--mode" $y] }
    }
    | flatten
    | each { |mode| simple-disk-benchmark ...$args ...$mode }

    open ./benchmark.json
}

def sum [] {
    reduce -f [] { |value, acc|
        if ($acc | length) == 0 {
            [$value]
        } else {
            $acc | append (($acc | last) + $value)
        }
    }
}

def main [] {
    benchmark
    | select options runs
    | each { |benchmark|
        let run = $benchmark.runs | first
        let mode = if $run.mode == "Write" { "geschrieben" } else "gelesen"
        let random = if $benchmark.options.random_seek { " (Zufälliges Suchen)" } else ""

        [
            ($run.cycle_results | get elapsed | sum)
            ($run.cycle_results | get bytes | sum)
            $"Bytes ($mode)($random)"
        ]
    }
    | to json
    | uv run ($env.FILE_PWD | path join plot.py)

    rm -f testdata.dat ./benchmark.json
}
