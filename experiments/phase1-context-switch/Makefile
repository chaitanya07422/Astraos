CC = gcc
CFLAGS = -Wall -Wextra -O0 -g

.PHONY: all run clean

all: context_switch

context_switch: main.o switch.o
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.o: %.S
	$(CC) -c -o $@ $<

run: context_switch
	./context_switch

clean:
	rm -f *.o context_switch
