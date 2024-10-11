#include <sys/types.h>
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>

#include <sys/types.h>
#include <sys/wait.h>

void sigint_handler(int signum) {
	// send SIGKILL to all processes in group, so this process and children
	// will terminate.  Use SIGKILL because SIGTERM and SIGINT (among
	// others) are overridden in the child.
	kill(-getpgid(0), SIGKILL);
}

int pid; // Convenience to store this as global rather than passing as argument

void exit_early();
void speedup(int times);

int main(int argc, char *argv[]) {
	char *scenario = argv[1];
	pid = atoi(argv[2]);

	struct sigaction sigact;

	// Explicitly set flags
	sigact.sa_flags = SA_RESTART;
	sigact.sa_handler = sigint_handler;
	// Override SIGINT, so that interrupting this process sends SIGKILL to
	// this one and, more importantly, to the child.
	sigaction(SIGINT, &sigact, NULL);

	switch (scenario[0]) {
	case '0':
		kill(pid, SIGHUP);
		sleep(1);
		speedup(10);
		break;
	case '1':
		exit_early();
		break;
	case '2':
		kill(pid, SIGHUP);
		sleep(5);
		exit_early();
		break;
	case '3':
		kill(pid, SIGHUP);
		sleep(1);
		speedup(1);
		kill(pid, SIGHUP);
		sleep(1);
		speedup(1);
		exit_early();
		break;
	case '4':
		kill(pid, SIGHUP);
		sleep(1);
		kill(pid, SIGINT);
		sleep(1);
		speedup(1);
		exit_early();
		break;
	case '5':
		kill(pid, 12);
		kill(pid, SIGINT);
		sleep(1);
		kill(pid, SIGTERM);
		break;
	case '6':
		kill(pid, SIGINT);		// Print 1, 2
		sleep(1);
		speedup(1);
		kill(pid, 10);				// Fork child with exit status 7
		sleep(1);
		kill(pid, 16);				// Print 10
		sleep(1);
		exit_early();
		break;
	case '7':
		kill(pid, SIGINT);		// Print 1, 2
		sleep(1);
		speedup(1);
		kill(pid, 10);				// Fork child with exit status 7
		sleep(1);
		exit_early();
		break;
	case '8':
		kill(pid, SIGINT);		// Print 1, 2
		sleep(1);
		kill(pid, 31);				// Speed up SIGINT and block SIGCHLD
		sleep(1);
		kill(pid, 10);				// Set foo to a positive value
		sleep(1);
		kill(pid, 30);				// Set foo to 6
		sleep(1);
		kill(pid, SIGTERM);		// Print foo (6)
		sleep(1);
		exit_early();
		break;
	case '9':
		kill(pid, 31);				// Block SIGINT
		sleep(1);
		kill(pid, SIGQUIT);		// Start 8, 9, send SIGINT
		sleep(1);
		speedup(1);
		kill(pid, 31);				// Unblock SIGINT (prints 1,2)
		sleep(1);
		speedup(1);
		exit_early();
		break;

	}
	waitpid(pid, NULL, 0);
}

void exit_early() {
	kill(pid, 12);
	sleep(1);
	kill(pid, SIGTERM);
}

void speedup(int times) {
	for (int i = 0; i < times; ++i) {
		kill(pid, 30); // Noop speedup
		sleep(1);
	}
}
