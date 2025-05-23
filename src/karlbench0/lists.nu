export def sum []: list<int> -> list<int> {
    reduce -f [] { |value, acc|
        if ($acc | length) == 0 {
            [$value]
        } else {
            $acc | append (($acc | last) + $value)
        }
    }
}

export def flat-map [do: closure]: list<any> -> list<any> {
    each $do | flatten
}

export def map [list: list<any>, do: closure] {
    $list | each $do
}
