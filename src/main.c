#include <zmq.h>
#include <unistd.h>

void publisher(void) {
	printf("zmq_ctx_new - publisher\n");
	void* context = zmq_ctx_new();

	printf("zmq_socket - PUB\n");
	void* publisher = zmq_socket(context, ZMQ_PUB);

	printf("zmq_bind\n");
	zmq_bind(publisher, "tcp://*:5555");

	char send_msg[] = "hello zmq!";

	while(1) {
		printf("zmq_send\n");
		zmq_send(publisher, send_msg, sizeof(send_msg), 0);
		sleep(1);
	}
}

void subscriber(void) {
	printf("zmq_ctx_new - subscriber\n");
	void* context = zmq_ctx_new();

	printf("zmq_socket - SUB\n");
	void* subscriber = zmq_socket(context, ZMQ_SUB);

	printf("zmq_connect\n");
	zmq_connect(subscriber, "tcp://localhost:5555");

	printf("zmq_setsockopt\n");
	zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "", 0);

	char recv_msg[] = "          ";

	while(1) {
		printf("zmq_recv\n");
		zmq_recv(subscriber, recv_msg, sizeof(recv_msg), 0);

		printf("%s\n", recv_msg);
		sleep(1);
	}
}

int main(void) {
	if (fork() == 0) {
		subscriber();
	} else {
		publisher();
	}

	return 0;
}