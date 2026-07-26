AS = as
LD = ld

.PHONY: all run clean hello arithmetic

all: hello arithmetic

hello: hello.o
	$(LD) -o $@ $^

arithmetic: arithmetic.o
	$(LD) -o $@ $^

%.o: %.S
	$(AS) -o $@ $<

run: all
	./hello
	./arithmetic

clean:
	rm -f *.o hello arithmetic
