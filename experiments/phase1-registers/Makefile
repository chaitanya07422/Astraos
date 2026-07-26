CC = gcc
CFLAGS = -Wall -Wextra -O0 -g
ASFLAGS =

.PHONY: all run clean gdb-demo

all: register_inspect

register_inspect: main.o registers.o
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.o: %.S
	$(CC) $(ASFLAGS) -c -o $@ $<

run: register_inspect
	./register_inspect

# Non-interactive GDB dump at fill_regs_ready (before callee-saved restore)
gdb-demo: register_inspect
	gdb -batch -ex 'set pagination off' \
	    -ex 'break fill_regs_ready' -ex 'run' \
	    -ex 'info registers x0 x1 x19 x20 x29 x30 sp' \
	    -ex 'quit' ./register_inspect

clean:
	rm -f *.o register_inspect
