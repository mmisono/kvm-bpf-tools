#!/usr/bin/env python
from __future__ import print_function
from collections import defaultdict
from time import sleep

from bcc import BPF

from exit_reason import EXIT_REASON

text = """
BPF_HASH(counts, unsigned int, u64);
BPF_HASH(counts_nested, unsigned int, u64);

TRACEPOINT_PROBE(kvm, kvm_exit) {
    u64 zero = 0, *val;
    unsigned int key = args->exit_reason;
    val = counts.lookup_or_init(&key, &zero);
    (*val)++;
    return 0;
}

TRACEPOINT_PROBE(kvm, kvm_nested_vmexit) {
    u64 zero = 0, *val;
    unsigned int key = args->exit_code;
    val = counts_nested.lookup_or_init(&key, &zero);
    (*val)++;
    return 0;
}
"""


def main():
    # load BPF program
    b = BPF(text=text)

    print("Tracing... Hit Ctrl-C to end.")
    try:
        sleep(99999999)
    except KeyboardInterrupt:
        pass
    print()

    counts = defaultdict(int)
    result = {}
    for table_name in ("counts", "counts_nested"):
        cs = b.get_table(table_name)
        result[table_name] = defaultdict(int)
        for k, v in cs.items():
            k, v = k.value, v.value
            result[table_name][EXIT_REASON[k]] = v

    print("{:3s} {:18s} {:>8s} {:>8s} {:>8s}".format(
        "", "Exit reason", "Total", "L1", "L2"))
    total = 0
    l2_total = 0
    for i, e in enumerate(EXIT_REASON):
        c = result["counts"][e]
        cn = result["counts_nested"][e]
        if c > 0 or cn > 0:
            print("{:3d} {:18s} {:8d} {:8d} {:8d}".format(i, e, c, c - cn, cn))
            total += c
            l2_total += cn
    print("{:3s} {:18s} {:8d} {:8d} {:8d}".format("", "Total", total,
                                                  total - l2_total, l2_total))


if __name__ == "__main__":
    main()
