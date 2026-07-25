; Count from 3 down to 0, printing each value
    LI    R1, 3
loop:
    PRINT R1
    LI    R2, 0
    CMP   R1, R2
    BEQ   done
    LI    R3, 1
    SUB   R1, R1, R3
    JMP   loop
done:
    HALT
