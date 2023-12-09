#include <assert.h>
#include <poll.h>
#include <errno.h>
#include <fcntl.h>
#include <getopt.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <signal.h>
#include <stdbool.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/file.h>

#include <sys/ioctl.h>
#include <linux/serial.h>

#define BUFLEN 256

/* https://blog.mbedded.ninja/programming/operating-systems/linux/linux-serial-ports-using-c-cpp */
void configure_serial_port(int fd)
{
    struct termios tty;

        struct serial_struct serial;

        if (ioctl(fd, TIOCGSERIAL, &serial) < 0) {
            perror("error getting serial struct. Low latency mode not supported");
        } else {
            serial.flags |= ASYNC_LOW_LATENCY;
            if (ioctl(fd, TIOCSSERIAL, &serial) < 0)
                perror("error setting serial struct. Low latency mode not supported");
        }

    assert(tcgetattr(fd, &tty) >= 0);

    /* set parity */
    tty.c_cflag &= ~PARENB;

    tty.c_cflag &= ~CSTOPB;

    /* set bits */
    tty.c_cflag &= ~CSIZE;

    tty.c_cflag |= CS8; 

    /* disable RTS/CTS hardware flow control */
    tty.c_cflag &= ~CRTSCTS;

    /* turn on READ & ignore ctrl lines (CLOCAL = 1) */
    tty.c_cflag |= CREAD | CLOCAL;

    /* disable canonical mode */
    tty.c_lflag &= ~ICANON;

    /* disable echo */
    tty.c_lflag &= ~ECHO;

    /* disable erasure */
    tty.c_lflag &= ~ECHOE;

    /* disable new-line echo */
    tty.c_lflag &= ~ECHONL;

    /* disable interpretation of INTR, QUIT and SUSP */
    tty.c_lflag &= ~ISIG;

    /* turn off s/w flow ctrl */
    tty.c_iflag &= ~(IXON | IXOFF | IXANY);

    /* disable any special handling of received bytes */
    tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);

    /* prevent special interpretation of output bytes (e.g. newline chars) */
    tty.c_oflag &= ~OPOST;

    /* prevent conversion of newline to carriage return/line feed */
    tty.c_oflag &= ~ONLCR;

#ifndef __linux__
    /* prevent conversion of tabs to spaces */
    tty.c_oflag &= ~OXTABS;

    /* prevent removal of C-d chars (0x004) in output */
    tty.c_oflag &= ~ONOEOT;
#endif

    /* how much to wait for a read */
    tty.c_cc[VTIME] = 0;

    /* minimum read size: 1 byte */
    tty.c_cc[VMIN] = 0;

    /* set port speed */
    cfsetispeed(&tty, B9600);
    cfsetospeed(&tty, B9600);

    assert( tcsetattr(fd, TCSANOW, &tty) >= 0 );
}

void dump( char dir, unsigned char *buf, int len ) {
 printf("%c", dir );
 for(int i=0; i< len; i++){ 
   printf(" %02x", buf[i]);
 }
 printf("\n");
 fflush(stdout);
}


int main(int argc, char**argv) {

 int up_fd;
 int dn_fd;

 struct pollfd fds[2];

 if(argc!=3) {
   printf("%s <datalogger tty> <inverter tty>\n", argv[0] );
   printf("   modbus decoder at https://rapidscada.net/modbus/\n");
   exit(1);
 }
 
 up_fd = open(argv[1], O_RDWR);
 assert(up_fd>0);
 configure_serial_port(up_fd);

 dn_fd = open(argv[2], O_RDWR);
 assert(dn_fd>0);
 configure_serial_port(dn_fd);

 fds[0].fd     = up_fd;
 fds[0].events = POLLIN;
 fds[0].revents= 0;

 fds[1].fd     = dn_fd;
 fds[1].events = POLLIN;
 fds[1].revents= 0;
 


 while(1) {
   unsigned char b;
   unsigned char buf[BUFLEN];
   int ret;
   time_t now;
   // read a byte from up_fd, blocking until we get something
   do {
     // fprintf(stderr, ".");
   } while  ( poll(fds, 1, 10000)<=0 )  ;
   
    // get lock
   // fprintf(stderr, "[");
   flock( dn_fd, LOCK_EX );
   // fprintf(stderr, "X");
   
    // now watch up_fd and dn_fd, and pass bytes from one to the other.
   while (poll( fds, 2, 1000 )>0) {
       if (fds[0].revents|POLLIN == POLLIN) {
         ret = read(up_fd, buf, BUFLEN );
         if( ret>0 ) {
           // fprintf(stderr, ">"); // "Passing byte up -> down [%02x]\n", b);
           write(dn_fd, buf, ret );
           dump('>', buf, ret);
         }
       }
     
       if (fds[1].revents|POLLIN == POLLIN) {
         ret = read(dn_fd, buf, BUFLEN );
         if( ret>0 ) {
           // fprintf(stderr, "<");  //Passing byte down -> up\n");
           write(up_fd, buf, ret );
           dump('<', buf, ret);
         }
       }
       fds[0].revents= 0;
       fds[1].revents= 0;
    }
    // release lock
    // fprintf(stderr, "X");
    flock( dn_fd, LOCK_UN );
    // fprintf(stderr, "]");
   }
}

