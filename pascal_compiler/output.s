.text
.globl main
main:
    addi sp, sp, -1024
    li t0, 10.5
    sw t0, 12(sp)
    li t0, 5.2
    sw t0, 16(sp)
    li t0, 10.87
    sw t0, 12(sp)
    li t0, 1
    sw t0, 20(sp)
    li t0, 0
    sw t0, 8(sp)
    li t0, 1
    li t0, 10
    sw t0, 0(sp)
L1:
    lw t0, 0(sp)
    bgt t0, t0, L2
    lw t0, 8(sp)
    lw t0, 0(sp)
    sw t0, 8(sp)
    lw t0, 0(sp)
    addi t0, t0, 1
    sw t0, 0(sp)
    j L1
L2:
    li t0, 1
    sw t0, 0(sp)
L3:
    lw t0, 0(sp)
    li t0, 5
    beqz t0, L4
    lw t0, 0(sp)
    li t0, 1
    sw t0, 0(sp)
    j L3
L4:
    li t0, 1
    li t0, 10
    sw t0, 0(sp)
L5:
    lw t0, 0(sp)
    bgt t0, t0, L6
    lw t0, 0(sp)
    lw t0, 0(sp)
    lw t0, 0(sp)
    addi t0, t0, 1
    sw t0, 0(sp)
    j L5
L6:
L7: .string "Pascal"
    la t0, L7
    sw t0, 32(sp)
    addi sp, sp, 1024
    li a0, 0
    ret

.data
i: dw 0
j: dw 0
sum: dw 0
x: dw 0
y: dw 0
flag: dw 0
ch: dw 0
numbers: dw 0
word: dw 0