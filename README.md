# KVM BPF Tools
Some codes to trace KVM events using BPF.

## Requirements
- [bcc](https://github.com/iovisor/bcc)
- [fire](https://github.com/google/python-fire)

## VMEXIT Counts
Counts number of KVM VMEXIT.
L2 shows the number of VMEXIT from nested guests.

```sh
% sudo ./kvm_vmexit_count.py
Tracing... Hit Ctrl-C to end.
^C
    Exit reason           Total       L1       L2
  0 EXCEPTION_OR_NMI         52        0       52
  1 EXTERNAL_INT             68       49       19
  7 INTERRUPT_WINDOW         91       84        7
 12 HLT                    2965     2787      178
 15 RDPMC                  8106     8106        0
 19 VMCLEAR                 118      118        0
 20 VMLAUNCH                104      104        0
 21 VMPTRLD                 117      117        0
 23 VMREAD                 2887     2887        0
 24 VMRESUME               2418     2418        0
 28 MOV_CR                  428      428        0
 29 MOV_DR                  579      579        0
 30 IO_INSTRUCTION          134       46       88
 31 RDMSR                  1771     1761       10
 32 WRMSR                  1987     1294      693
 44 APIC_ACCESS            7657     7657        0
 48 EPT_VIOLATION          1528        5     152
 49 EPT_MISCONFIG            76       76        0
 50 INVEPT                   25       25        0
 52 VMX_PREEMPT_TIMER        51       32       19
 53 INVVPID                  17       17        0
    Total                 31179    28590     2589
```

## VMEXIT Counts and Handling time
Counts number of KVM VMEXIT and measure average handling time.
Reported time is in nano seconds.

```sh
$ sudo ./kvm_vmexit_time.py
Tracing... Hit Ctrl-C to end.
^C
    Exit reason           Total (Avg Time)       L1 (Avg Time)       L2 (Avg Time)
  0 EXCEPTION_OR_NMI         27 (   24760)        1 (    4979)       26 (   25520)
  1 EXTERNAL_INT             25 (    3304)       21 (    2797)        4 (    5967)
  7 INTERRUPT_WINDOW         38 (    4009)       37 (    3363)        1 (   27890)
 12 HLT                    1245 ( 3437190)     1164 ( 3674603)       81 (   25469)
 15 RDPMC                  3760 (    3785)     3760 (    3785)        0 (       0)
 19 VMCLEAR                  82 (   12110)       82 (   12110)        0 (       0)
 20 VMLAUNCH                 69 (   32072)       69 (   32072)        0 (       0)
 21 VMPTRLD                  82 (    8692)       82 (    8692)        0 (       0)
 23 VMREAD                 1282 (    3403)     1282 (    3403)        0 (       0)
 24 VMRESUME               1031 (   28250)     1031 (   28250)        0 (       0)
 28 MOV_CR                  324 (    6583)      324 (    6583)        0 (       0)
 29 MOV_DR                  308 (    2597)      308 (    2597)        0 (       0)
 30 IO_INSTRUCTION           68 (   21263)       19 (   14930)       49 (   23719)
 31 RDMSR                   897 (    2858)      892 (    2744)        5 (   23206)
 32 WRMSR                  1060 (    9160)      777 (    3059)      283 (   25912)
 44 APIC_ACCESS            3414 (    8813)     3414 (    8813)        0 (       0)
 48 EPT_VIOLATION           666 (   27375)        1 (   15456)      665 (   27393)
 49 EPT_MISCONFIG            22 (   21835)       22 (   21835)        0 (       0)
 50 INVEPT                    6 (    6420)        6 (    6420)        0 (       0)
 52 VMX_PREEMPT_TIMER        21 (   12105)       14 (    4543)        7 (   27228)
 53 INVVPID                   2 (    6608)        2 (    6608)        0 (       0)
    Total (Avg Time)      14430 (  304754)    13309 (  328184)     1121 (   26580)
```

## VMEXIT Handling time histogram
Show VMEXIT handling time histogram.
Reported time is in nano seconds.

```sh
% sudo ./kvm_vmexit_time_hist.py
Tracing... Hit Ctrl-C to end.
^C
     value               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 55       |                                        |
       512 -> 1023       : 772      |***                                     |
      1024 -> 2047       : 2497     |**********                              |
      2048 -> 4095       : 9349     |****************************************|
      4096 -> 8191       : 3823     |****************                        |
      8192 -> 16383      : 2762     |***********                             |
     16384 -> 32767      : 2912     |************                            |
     32768 -> 65535      : 129      |                                        |
     65536 -> 131071     : 16       |                                        |
    131072 -> 262143     : 47       |                                        |
    262144 -> 524287     : 56       |                                        |
    524288 -> 1048575    : 228      |                                        |
   1048576 -> 2097151    : 183      |                                        |
   2097152 -> 4194303    : 1115     |****                                    |
   4194304 -> 8388607    : 290      |*                                       |
   8388608 -> 16777215   : 201      |                                        |
```

Only trace the specified VMEXIT by the specifying VMEXIT number.

```sh
% sudo ./kvm_vmexit_time_hist.py 12
Tracing... Hit Ctrl-C to end.
^C
     value               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 5        |                                        |
       512 -> 1023       : 498      |****************************************|
      1024 -> 2047       : 489      |*************************************** |
      2048 -> 4095       : 457      |************************************    |
      4096 -> 8191       : 318      |*************************               |
      8192 -> 16383      : 301      |************************                |
     16384 -> 32767      : 137      |***********                             |
     32768 -> 65535      : 9        |                                        |
     65536 -> 131071     : 2        |                                        |
    131072 -> 262143     : 1        |                                        |
    262144 -> 524287     : 2        |                                        |
    524288 -> 1048575    : 18       |*                                       |
   1048576 -> 2097151    : 25       |**                                      |
   2097152 -> 4194303    : 99       |*******                                 |
   4194304 -> 8388607    : 29       |**                                      |
   8388608 -> 16777215   : 13       |*                                       |
```

## VMEXIT Handling time slower
Report VMEXIT events whose handling time is longer than the predefined value.
Reported time is in nano seconds.

```sh
# Threshold is 1ms (default: 10ms) and excludes exit 12 (HLT)
% sudo ./kvm_vmexit_slower.py 1 --excludes 12,
Excludes: HLT
Tracing... Hit Ctrl-C to end.
 44 APIC_ACCESS         2631024 (L1)
 44 APIC_ACCESS         1442657 (L1)
  1 EXTERNAL_INT        1635030 (L1)
...
```

## License
Apache-2.0
