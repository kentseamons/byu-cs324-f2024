#!/usr/bin/python3

import argparse
import re
import subprocess
import sys
import time
from typing import Callable, Any

NUM_TESTS = 10

KILL_RE = re.compile(r'^\s*(\d+)\.\d+\s+kill\(\d+, (SIG[A-Z0-9]+|\d+)\)')
RULE_NOSIG_RE = re.compile(r'^NOSIG:\s*(.+)')
RULE_SIGTIMING_RE = re.compile(r'^SIGTIMING:\s*(.+)')
RULE_SIGTIMING_PAIR_RE = re.compile(r'^([A-Z0-9_]+)([=<>])(.+)')
RULE_WHITELIST_RE = re.compile(r'^WHTLST:\s*(.+)')

class KillTest:
    signals = './signals'
    killer = './killer'

    scenario = None
    solution = None
    max_time = None
    rules = [
        'NOSIG: SIGKILL,9',
        'WHTLST: SIGHUP,1,SIGINT,2,SIGQUIT,3,SIGTERM,15,SIGPWR,30,SIGUSR1,10,SIGSTKFLT,16,SIGSYS,31,SIGUSR2,12,SIGCHLD,17',
        ]

    def grade(self):
        cmd = ['strace', '-r', '-e', 'trace=%signal',
                self.signals, self.killer, str(self.scenario)]

        start_time = time.time()
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        end_time = time.time()

        if self.solution is not None:
            expected = self.stringify_solution()
            actual = p.stdout.decode('utf-8').strip()
            if expected != actual:
                print(f'\nExpected:\n{expected}\n\nGot:\n{actual}\n')
                return False

        # Check timing
        if self.max_time is not None:
            time_elapsed = int(end_time - start_time)
            if time_elapsed > self.max_time:
                print(f'\nTime elapsed: {time_elapsed}s\n' + \
                        f'Maximum allowed: {self.max_time}s\n')
                return False

        # Apply rules
        output = p.stderr.decode('utf-8').strip()
        if not self.apply_rules(output.splitlines()):
            return False

        return True

    def stringify_solution(self):
        return '\n'.join([str(i) for i in self.solution])

    def apply_rules(self, strace_lines):
        for rule in self.rules:
            # Enforce whitelisted signals
            m = RULE_WHITELIST_RE.search(rule)
            if m is not None:
                if not self.apply_whtlst(m.group(1), strace_lines):
                    return False
                continue

            # Disallowed signals
            m = RULE_NOSIG_RE.search(rule)
            if m is not None:
                if not self.apply_nosig(m.group(1), strace_lines):
                    return False
                continue

            # Signals with timing requirements
            m = RULE_SIGTIMING_RE.search(rule)
            if m is not None:
                if not self.apply_sig_timing(m.group(1), strace_lines):
                    return False
                continue

        return True

    def apply_whtlst(self, sigs_str, strace_lines):
        return self._enforceSignalSetRequirements(sigs_str, strace_lines, True)


    def apply_nosig(self, sigs_str, strace_lines):
        return self._enforceSignalSetRequirements(sigs_str, strace_lines, False)

    def apply_sig_timing(self, sig_timing, strace_lines):
        sig_mapping = {}
        pairs = sig_timing.split(',')
        for pair in pairs:
            m = RULE_SIGTIMING_PAIR_RE.match(pair)
            if m is None:
                continue
            sig = m.group(1).strip()
            op = m.group(2)
            timing = m.group(3).strip()
            sig = sig.strip()
            timing = int(timing.strip())
            sig_mapping[sig] = op, timing

        for line in strace_lines:
            m = KILL_RE.search(line)
            if m is None:
                continue
            time_used = int(m.group(1))
            sig_used = m.group(2)
            if sig_used not in sig_mapping:
                continue
            op, timing = sig_mapping[sig_used]
            if op == '<':
                if time_used >= timing:
                    print(f'\n{sig_used} can only be sent before {timing} ' + \
                            'seconds have passed\n')
                    return False
            elif op == '>':
                if time_used < timing:
                    print(f'\n{sig_used} can only be sent after {timing} ' + \
                            'seconds have passed\n')
                    return False
            elif op in ('=', None):
                if time_used != timing:
                    print(f'\n{sig_used} can only be sent when exactly ' + \
                            '{timing} seconds have passed\n')
                    return False
        return True

    SignalAnalysisResult = None | tuple[bool, str]

    def _enforceSignalSetRequirements(self, sigs_str: str, strace_lines: list[str], expectUsed: bool):
        """Enforces that all system calls to kill() use signals
        which are always in or always out of the sigs_str comma separated list"""
        result = self._processSignalsSent(sigs_str, strace_lines, expectUsed)
        if result is None:
            return True
        usedDisallowedSignal, sig_used = result
        if usedDisallowedSignal:
            print(f'\n{sig_used} not allowed\n')
            return False
        return True

    def _processSignalsSent(self, sigs_str: str, strace_lines: list[str], expectUsed: bool) -> SignalAnalysisResult:
        """Reports whether all of the kill() calls conform to the constraint represented by sigs_str and expectUsed"""
        sigs_set = self._constructUniqueSet(sigs_str)
        return self._forEachSignalSent(strace_lines, self._expectSignalUsed(sigs_set, expectUsed))

    def _expectSignalUsed(self, sigs_set: set[str], expectUsed: bool) -> SignalAnalysisResult:
        """Produces a function that can be passed to _forEachSignalSent() to test if the signals are in the set"""
        def processSignal(sig_used):
            return None if (sig_used in sigs_set) == expectUsed else (True, sig_used)
        return processSignal

    def _constructUniqueSet(self, commaSeparatedList: str) -> list[str]:
        """Interprets a comma separated list into a unique set of distinct values"""
        return set([s.strip() for s in commaSeparatedList.split(',')])

    # Generics are new in python 3.12. Until that's the main version, we'll need to use looser typing
    # def _forEachSignalSent[T](self, strace_lines: list[str], eachSignal: Callable[[str], T]) -> T | None:
    def _forEachSignalSent(self, strace_lines: list[str], eachSignal: Callable[[str], Any]) -> Any | None:
        """Processes each system call to kill() be calling the eachSignal() method
        If the return value from eachSignal() is not None, it exits immediately and returns that value"""
        for line in strace_lines:
            m = KILL_RE.search(line)
            if m is None:
                continue
            sig_used = m.group(2)
            result = eachSignal(sig_used)
            if result is not None:
                return result

class KillTest0(KillTest):
    scenario = 0
    solution = [1, 2, 25]

class KillTest1(KillTest):
    scenario = 1
    solution = []

class KillTest2(KillTest):
    scenario = 2
    solution = [1, 2]

class KillTest3(KillTest):
    scenario = 3
    solution = [1, 2, 1, 2]
    rules = KillTest.rules + \
            ['SIGTIMING: ' + \
            'SIGHUP<3,SIGINT<3,1<3,2<3']

class KillTest4(KillTest):
    scenario = 4
    solution = [1, 1, 2, 2]

class KillTest5(KillTest):
    scenario = 5
    solution = [1]

class KillTest6(KillTest):
    scenario = 6
    solution = [1, 2, 7, 10]

class KillTest7(KillTest):
    scenario = 7
    solution = [1, 2, 7]

class KillTest8(KillTest):
    scenario = 8
    solution = [1, 2, 6]

class KillTest9(KillTest):
    scenario = 9
    solution = [8, 9, 1, 2]
    rules = KillTest.rules + \
            ['NOSIG: SIGHUP,SIGINT,1,2']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('scenario', action='store',
            nargs='?', type=int, choices=range(NUM_TESTS))
    args = parser.parse_args(sys.argv[1:])

    thismodule = sys.modules[__name__]
    if args.scenario is None:
        score = 0
        max_score = 0
        for scenario in range(NUM_TESTS):
            sys.stdout.write(f'Testing scenario {scenario}:')
            sys.stdout.flush()
            max_score += 1
            cls = getattr(thismodule, f'KillTest{scenario}', None)
            test = cls()
            if test.grade():
                sys.stdout.write('   PASSED\n')
                sys.stdout.flush()
                score += 1
            else:
                sys.stdout.write('   FAILED\n')
                sys.stdout.flush()
        print(f'Score: {score}/{max_score}')
    else:
        scenario = args.scenario
        sys.stdout.write(f'Testing scenario {scenario}:')
        sys.stdout.flush()
        cls = getattr(thismodule, f'KillTest{scenario}', None)
        test = cls()
        if test.grade():
            sys.stdout.write('   PASSED\n')
            sys.stdout.flush()
        else:
            sys.stdout.write('   FAILED\n')
            sys.stdout.flush()

if __name__ == '__main__':
    main()
