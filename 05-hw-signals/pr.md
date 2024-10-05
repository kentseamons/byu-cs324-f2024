## Overview
The current [signal homework instruction](/05-hw-signals/README.md#instructions) makes the asserts the following requirement on the assignment (emphasis added):
> You are not allowed to send signals other than those for which handlers are installed in `signals.c`. \
> **In particular, you cannot use `SIGKILL`.**

The grading driver asserts that students do not send `SIGKILL` commands, but it does not actually restrict the _other_ signals. This allows a student (like me) to use any of the other signals that have the exact same effect as SIGKILL without being flagged by the grading system. Examples include: `SIGPIPE`, `SIGALRM`, or `SIGXFSZ`.

This PR explicitly blacklists **all** signals which result in a term or core dump result. Another option would be to whitelist the signals specifically allowed in the process.

## All Blacklisted Signals
`Core` action signals:
- SIGABRT
- SIGBUS
- SIGFPE
- SIGILL
- SIGIOT
- SIGQUIT
- SIGSEGV
- SIGSYS
- SIGTRAP
- SIGUNUSED
- SIGXCPU
- SIGXFSZ

`Term` action signals:
- SIGALRM
- SIGEMT
- SIGHUP
- SIGINT
- SIGIO
- SIGKILL
- SIGLOST
- SIGPIPE
- SIGPOLL
- SIGPROF
- SIGPWR
- SIGSTKFLT
- SIGTERM
- SIGUSR1
- SIGUSR2
- SIGVTALRM

## Relevant Source Material
Extracted from `man signal.7`:
```txt
   Signal dispositions
       Each signal has a current disposition, which determines how the process behaves when it is delivered the signal.

       The entries in the "Action" column of the table below specify the default disposition for each signal, as follows:

       Term   Default action is to terminate the process.

       Ign    Default action is to ignore the signal.

       Core   Default action is to terminate the process and dump core (see core(5)).

       Stop   Default action is to stop the process.

       Cont   Default action is to continue the process if it is currently stopped.

   ...

   Standard signals
       Linux supports the standard signals listed below.  The second column of the table indicates which standard (if any) specified the signal: "P1990" indicates that
       the signal is described in the original POSIX.1-1990 standard; "P2001" indicates that the signal was added in SUSv2 and POSIX.1-2001.

       Signal      Standard   Action   Comment
       ────────────────────────────────────────────────────────────────────────
       SIGABRT      P1990      Core    Abort signal from abort(3)
       SIGALRM      P1990      Term    Timer signal from alarm(2)
       SIGBUS       P2001      Core    Bus error (bad memory access)
       SIGCHLD      P1990      Ign     Child stopped or terminated
       SIGCLD         -        Ign     A synonym for SIGCHLD
       SIGCONT      P1990      Cont    Continue if stopped
       SIGEMT         -        Term    Emulator trap
       SIGFPE       P1990      Core    Floating-point exception
       SIGHUP       P1990      Term    Hangup detected on controlling terminal
                                       or death of controlling process
       SIGILL       P1990      Core    Illegal Instruction
       SIGINFO        -                A synonym for SIGPWR
       SIGINT       P1990      Term    Interrupt from keyboard
       SIGIO          -        Term    I/O now possible (4.2BSD)
       SIGIOT         -        Core    IOT trap. A synonym for SIGABRT
       SIGKILL      P1990      Term    Kill signal
       SIGLOST        -        Term    File lock lost (unused)
       SIGPIPE      P1990      Term    Broken pipe: write to pipe with no
                                       readers; see pipe(7)
       SIGPOLL      P2001      Term    Pollable event (Sys V);
                                       synonym for SIGIO
       SIGPROF      P2001      Term    Profiling timer expired
       SIGPWR         -        Term    Power failure (System V)
       SIGQUIT      P1990      Core    Quit from keyboard
       SIGSEGV      P1990      Core    Invalid memory reference
       SIGSTKFLT      -        Term    Stack fault on coprocessor (unused)
       SIGSTOP      P1990      Stop    Stop process
       SIGTSTP      P1990      Stop    Stop typed at terminal
       SIGSYS       P2001      Core    Bad system call (SVr4);
                                       see also seccomp(2)
       SIGTERM      P1990      Term    Termination signal
       SIGTRAP      P2001      Core    Trace/breakpoint trap
       SIGTTIN      P1990      Stop    Terminal input for background process
       SIGTTOU      P1990      Stop    Terminal output for background process
       SIGUNUSED      -        Core    Synonymous with SIGSYS
       SIGURG       P2001      Ign     Urgent condition on socket (4.2BSD)
       SIGUSR1      P1990      Term    User-defined signal 1
       SIGUSR2      P1990      Term    User-defined signal 2
       SIGVTALRM    P2001      Term    Virtual alarm clock (4.2BSD)
       SIGXCPU      P2001      Core    CPU time limit exceeded (4.2BSD);

                                       see setrlimit(2)
       SIGXFSZ      P2001      Core    File size limit exceeded (4.2BSD);
                                       see setrlimit(2)
       SIGWINCH       -        Ign     Window resize signal (4.3BSD, Sun)
```
