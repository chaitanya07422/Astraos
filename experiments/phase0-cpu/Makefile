.PHONY: run loop add test

run:
	python3 cpu_sim.py

loop:
	python3 cpu_sim.py --trace programs/loop.asm

add:
	python3 cpu_sim.py --trace programs/add.asm

test: run loop
