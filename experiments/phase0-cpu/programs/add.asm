; R3 = 7 + 5, store at 0x20
    LI    R1, 7
    LI    R2, 5
    ADD   R3, R1, R2
    STORE R3, 0x20
    PRINT R3
    HALT
