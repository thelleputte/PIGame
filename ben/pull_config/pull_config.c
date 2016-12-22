#include <errno.h>
#include <sys/epoll.h>  //uint16_t seems to be defined here 
#include <fcntl.h>
#include <stdio.h>
#include <time.h>

#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>

//#define BCM2708_PERI_BASE		  0x3F000000
#define BCM2708_PERI_BASE        0x20000000
#define BLOCK_SIZE (4*1024)
 
int  mem_fd;
volatile void *gpio_map;
uint32_t tempValue;
// I/O access
volatile unsigned *gpio;

//function prototypes
void setup_io_pull(uint32_t pull_cfg, uint32_t gpios, unsigned char bank);
void short_wait();


void short_wait(void)
{
    int i;

    for (i=0; i<=150; i++) {    // wait 151 cycles
        asm volatile("nop");
    }
}

void setup_io_pull(uint32_t pull_cfg, uint32_t gpios, unsigned char bank){
	/* open /dev/mem */
	if ((mem_fd = open("/dev/mem", O_RDWR|O_SYNC) ) < 0) {
		printf("can't open /dev/mem \n");
		exit(-1);
	}
	
	/* mmap GPIO */
	gpio_map = mmap(
		NULL,             		//Any adddress in our space will do
		  BLOCK_SIZE,       	//Map length
		  PROT_READ|PROT_WRITE,	// Enable reading & writting to mapped memory
		  MAP_SHARED,       	//Shared with other processes
		  mem_fd,           	//File to map
		  //BCM2708_PERI_BASE+0x100000        	//PADSOffset 
		  BCM2708_PERI_BASE+0x200000         	//GPIOOffset 
	);
   
	close(mem_fd); //No need to keep mem_fd open after mmap
	// Always use volatile pointer!
	gpio = (volatile unsigned *) gpio_map;
	
	volatile uint32_t *gppud = (uint32_t*) (gpio_map+0x94);//see pdf page 91
	*gppud = pull_cfg; //set the pull config we want to push
	fprintf(stdout, "gppud after set 0x%x\n", *gppud);
	
	volatile uint32_t *gppudClk;
	if (!bank){
		//we manage bank 0 for gpios 0 to 31
		fprintf(stdout, "bank0 at line %d\n",__LINE__);
		gppudClk = (uint32_t*) (gpio_map+0x98);	
	}
	else{
		//we manage gpio 32 to 53
		gppudClk = (uint32_t*) (gpio_map+0x9C);
	}
	*gppudClk = gpios; //set the bits passed as arguments
	short_wait();
	*gppudClk = 0;
	short_wait();	
}

void main(int argc, char **argv){
	if (argc != 4){
		fprintf(stdout, 	"usage : pull_config pull_cfg GPIOS bank\n" 
							"pull_config: 0: none 1: down 2:up\n"
							"GPIOS: put the desired bits to one and convert in hex\n"
							"bank: use 0 for gpios 0 to 31, use 1 for gpios 32  to 53\n");
	}
	else {
		uint32_t pull, gpios;
		unsigned char bank;
		
		pull = strtoul(argv[1],NULL,0);
		fprintf(stdout, "pull = %d\n",pull);
		gpios = strtoul(argv[2],NULL,0);
		fprintf(stdout, "gpios = %d\n",gpios);
		bank = (unsigned char) strtoul(argv[3],NULL,0);
		fprintf(stdout, "bank = %d\n",bank);
		setup_io_pull(pull, gpios, bank);
	}
}