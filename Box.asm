// Box.asm - K=83

// Box starts at screen row 83.
// Height = 20 rows.
// Width = 64 pixels (4 words).

// SCREEN + 32*83 = 19040.

(LOOP)

    // Read keyboard
    @KBD
    D=M

    @SETBLACK
    D;JNE

    @WHITE
    0;JMP


(SETBLACK)

    @VALUE
    M=-1

    @DRAW
    0;JMP


(WHITE)

    @VALUE
    M=0


(DRAW)

    // Starting screen address
    @19040
    D=A

    @PTR
    M=D


    // Number of rows
    @20
    D=A

    @ROWS
    M=D


(ROWLOOP)

    // Four words per row
    @4
    D=A

    @COLS
    M=D


(COLLOOP)

    // Write black or white
    @VALUE
    D=M

    @PTR
    A=M

    M=D


    // Move to next screen word
    @PTR
    M=M+1


    // Decrease column count
    @COLS
    M=M-1

    D=M

    @COLLOOP
    D;JGT


    // Move to next screen row
    @PTR
    D=M

    @28
    D=D+A

    @PTR
    M=D


    // Decrease row count
    @ROWS
    M=M-1

    D=M

    @ROWLOOP
    D;JGT


    // Repeat forever
    @LOOP
    0;JMP