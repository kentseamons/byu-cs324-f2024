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

int main(int argc, char *argv[]) {
	char *scenario = argv[1];
	int pid = atoi(argv[2]);

	struct sigaction sigact;

	// Explicitly set flags
	sigact.sa_flags = SA_RESTART;
	sigact.sa_handler = sigint_handler;
	// Override SIGINT, so that interrupting this process sends SIGKILL to
	// this one and, more importantly, to the child.
	sigaction(SIGINT, &sigact, NULL);

	switch (scenario[0]) {
	case '0':
		// Valid Signals
		kill(pid, SIGHUP);
		kill(pid, SIGINT);
		kill(pid, SIGQUIT);
		kill(pid, SIGTERM);
		kill(pid, 30);
		kill(pid, 10);
		kill(pid, 16);
		kill(pid, 31);
		kill(pid, 12);
		kill(pid, SIGUSR1);
		kill(pid, SIGUSR2);
		break;

	case '1':
		// Invalid signals
		kill(pid, SIGABRT);
		kill(pid, SIGBUS);
		kill(pid, SIGFPE);
		kill(pid, SIGILL);
		kill(pid, SIGIOT);
		kill(pid, SIGQUIT);
		kill(pid, SIGSEGV);
		kill(pid, SIGSYS);
		kill(pid, SIGTRAP);
		// kill(pid, SIGUNUSED);
		kill(pid, SIGXCPU);
		kill(pid, SIGXFSZ);

		kill(pid, SIGALRM);
		// kill(pid, SIGEMT);
		kill(pid, SIGHUP);
		kill(pid, SIGINT);
		kill(pid, SIGIO);
		kill(pid, SIGKILL);
		// kill(pid, SIGLOST);
		kill(pid, SIGCONT);
		kill(pid, SIGPIPE);
		kill(pid, SIGPOLL);
		kill(pid, SIGPROF);
		kill(pid, SIGPWR);
		kill(pid, SIGSTKFLT);
		kill(pid, SIGTERM);
		kill(pid, SIGUSR1);
		kill(pid, SIGUSR2);
		kill(pid, SIGVTALRM);
		break;

	case '2':
		kill(pid, SIGHUP);
		sleep(2);
		kill(pid, SIGHUP);
		kill(pid, SIGHUP);
		kill(pid, SIGHUP);
		sleep(3);
		kill(pid, SIGKILL);
		break;

	case '3':
		break;
	case '4':
		break;
	case '5':
		break;
	case '6':
		break;
	case '7':
		break;
	case '8':
		break;
	case '9':
		break;

	}
	waitpid(pid, NULL, 0);
}
