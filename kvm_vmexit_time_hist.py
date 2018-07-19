#!/usr/bin/env python
from __future__ import print_function
from collections import defaultdict
from time import sleep

from bcc import BPF

from exit_reason import EXIT_REASON

# Measure the time between vmexit and vmentry

text = """
BPF_HISTOGRAM(dist);
BPF_HASH(time, int, u64);

// I found that kvm_exit tracepoint event does not have vcpu_id :(
//TRACEPOINT_PROBE(kvm, kvm_exit) {
//    u64 zero = 0, *start;
//    int vcpu_id = args->vcpu->vpu_id;
//    val = time.lookup_or_init(&vcpu_id, &zero);
//    *val = bpf_ktime_get_ns();
//    return 0;
//}

#include <linux/kvm_host.h>
#include <linux/kvm.h>

int kprobe__vmx_handle_exit(struct pt_regs *ctx, struct kvm_vcpu *vcpu){
    u64 zero = 0, *start;
    int vcpu_id = vcpu->vcpu_id;
    start = time.lookup_or_init(&vcpu_id, &zero);
    *start = bpf_ktime_get_ns();
    return 0;
}

TRACEPOINT_PROBE(kvm, kvm_entry) {
    int vcpu_id = args->vcpu_id;
    u64 *start = time.lookup(&vcpu_id);
    if (start != 0){
        u64 end = bpf_ktime_get_ns();
        dist.increment(bpf_log2l(end-*start));
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

    dist = b["dist"]
    dist.print_log2_hist()

if __name__ == "__main__":
    main()
