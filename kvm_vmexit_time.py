#!/usr/bin/env python
from __future__ import print_function
from collections import defaultdict
from time import sleep

from bcc import BPF

from exit_reason import EXIT_REASON

text = """

struct tmp{
    u64 time;
    int nested;
    unsigned int exit_reason;
};

struct value{
    u64 cumulative_time;
    u64 count;
};

BPF_HASH(start_time, u64, struct tmp);
BPF_HASH(counts, unsigned int, struct value);
BPF_HASH(counts_nested, unsigned int, struct value);

TRACEPOINT_PROBE(kvm, kvm_exit) {
    u64 id = bpf_get_current_pid_tgid();
    struct tmp zero = {.time=0, .nested=0, .exit_reason=0};
    struct tmp *val = start_time.lookup_or_init(&id, &zero);
    val->time = bpf_ktime_get_ns();
    val->exit_reason = args->exit_reason;
    val->nested = 0;
    return 0;
}

TRACEPOINT_PROBE(kvm, kvm_nested_vmexit) {
    u64 id = bpf_get_current_pid_tgid();
    struct tmp *val = start_time.lookup(&id);
    if (val != 0){
        val->nested = 1;
    }else{
        // something wrong
    }
    return 0;
}

TRACEPOINT_PROBE(kvm, kvm_entry) {
    u64 id = bpf_get_current_pid_tgid();
    struct tmp *st = start_time.lookup(&id);
    if (st != 0){
        unsigned int exit_reason = st->exit_reason;
        struct value zero = {.cumulative_time = 0, .count = 0};
        struct value* val;
        if(st->nested == 0){
            val = counts.lookup_or_init(&exit_reason, &zero);
        }else{
            val = counts_nested.lookup_or_init(&exit_reason, &zero);
        }
        val->cumulative_time += bpf_ktime_get_ns() - st->time;
        val->count += 1;
    }
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

    result = {}
    for table_name in ("counts", "counts_nested"):
        cs = b.get_table(table_name)
        result[table_name] = {}
        for k, v in cs.items():
            k, c, t = k.value, v.count, v.cumulative_time
            result[table_name][EXIT_REASON[k]] = {"count": c, "cumul_time": t}

    print("{:3s} {:18s} {:>8s} {:>10s} {:>8s} {:>10s} {:>8s} {:>10s}".format(
        "", "Exit reason", "Total", "(Avg Time)", "L1", "(Avg Time)", "L2", "(Avg Time)"))
    l1_total = 1
    l2_total = 0
    l1_time_total = 0
    l2_time_total = 0
    for i, e in enumerate(EXIT_REASON):
        cc = 0
        ct = 0
        c_avg = 0
        cnc = 0
        cnt = 0
        cn_avg = 0
        if e in result["counts"]:
            c = result["counts"][e]
            cc, ct = c["count"], c["cumul_time"]
            c_avg = ct / float(cc)
        if e in result["counts_nested"]:
            cn = result["counts_nested"][e]
            cnc, cnt = cn["count"], cn["cumul_time"]
            cn_avg = cnt / float(cnc)
        if cc > 0 or cnc > 0:
            t = cc + cnc
            t_avg = (ct + cnt) / float(cc + cnc)
            print("{:3d} {:18s} {:8d} ({:8.0f}) {:8d} ({:8.0f}) {:8d} ({:8.0f})".format(
                i, e, t, t_avg, cc, c_avg, cnc, cn_avg))
            l1_total += cc
            l2_total += cnc
            l1_time_total += ct
            l2_time_total += cnt
    print("{:3s} {:18s} {:8d} ({:8.0f}) {:8d} ({:8.0f}) {:8d} ({:8.0f})".format("", "Total (Avg Time)", l1_total + l2_total, (l1_time_total + l2_time_total) / (l1_total + l2_total),
                                                                                l1_total, l1_time_total / l1_total,
                                                                                l2_total, l2_time_total / l2_total))


if __name__ == "__main__":
    main()
