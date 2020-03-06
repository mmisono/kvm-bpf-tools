#!/usr/bin/env python
from __future__ import print_function
import ctypes as ct
import sys

from bcc import BPF

if not hasattr(BPF, "perf_buffer_poll"):
    BPF.perf_buffer_poll = BPF.kprobe_poll

from exit_reason import EXIT_REASON

text = """
struct data{
    u64 time;
    int nested;
    unsigned int exit_reason;
};

BPF_HASH(start_time, u64, struct data);
BPF_PERF_OUTPUT(events);

TRACEPOINT_PROBE(kvm, kvm_exit) {
    u64 id = bpf_get_current_pid_tgid();
    struct data zero = {.time=0, .nested=0, .exit_reason=0};
    struct data *val = start_time.lookup_or_init(&id, &zero);
    val->time = bpf_ktime_get_ns();
    val->exit_reason = args->exit_reason;
    val->nested = 0;
    return 0;
}

TRACEPOINT_PROBE(kvm, kvm_nested_vmexit) {
    u64 id = bpf_get_current_pid_tgid();
    struct data *val = start_time.lookup(&id);
    if (val != 0){
        val->nested = 1;
    }else{
        // something wrong
    }
    return 0;
}

TRACEPOINT_PROBE(kvm, kvm_entry) {
    u64 id = bpf_get_current_pid_tgid();
    struct data *st = start_time.lookup(&id);
    if (st != 0){
        st->time = bpf_ktime_get_ns() - st->time;
        if(st->time >= THRESH){
            events.perf_submit(args, st, sizeof(struct data));
        }
    }
    return 0;
}
"""

class Data(ct.Structure):
    _fields_ = [("time", ct.c_uint64), ("nested", ct.c_int), ("exit_reason", ct.c_uint)]


def main(thresh=10, excludes=[]):
    global text

    if (type(excludes) == int):
      excludes = [excludes]

    if len(excludes) > 0:
        print("Excludes: {}".format(",".join([EXIT_REASON[i] for i in excludes])))

    # XXX: unit of thresh is milliseconds
    # mill to ns
    thresh = "{}ULL".format(int(thresh * 1000000));
    text = text.replace("THRESH", thresh)

    def print_event(cpu, data, size):
        event = ct.cast(data, ct.POINTER(Data)).contents
        if event.exit_reason not in excludes:
            print("{:3d} {:18s} {:8.0f} ({})".format(event.exit_reason, EXIT_REASON[event.exit_reason], event.time, "L1" if event.nested == 0 else "L2"))

    # load BPF program
    b = BPF(text=text)
    b["events"].open_perf_buffer(print_event, page_cnt=64)

    print("Tracing... Hit Ctrl-C to end.")
    try:
        while True:
            b.perf_buffer_poll()
    except KeyboardInterrupt:
        pass
    print()

if __name__ == "__main__":
    import fire
    fire.Fire(main)
