import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256

        self.reg = [0] * 8

        self.PC = self.reg[0]

        self.FL = self.reg[4]

        self.SP = self.reg[7]

        self.SP = 244

        self.commands = {
            0b00000001: self.hlt,
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b10100010: self.mul,
            0b01000110: self.pop,
            0b01000101: self.push,
            0b10100111: self.cmp,
            0b01010100: self.jmp,
            0b01010101: self.jeq,
            0b01010110: self.jne
        }

    def __repr__(self):
        return f"RAM: {self.ram} \n Register: {self.reg}"

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def hlt(self, operand_a, operand_b):
        return (0, False)

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        return (3, True)

    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])
        return (2, True)

    def mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        return (3, True)

    def pop(self, operand_a, operand_b):
        value = self.ram_read(self.SP)
        self.reg[operand_a] = value
        self.SP += 1

        return (2, True)

    def push(self, operand_a, operand_b):
        self.SP -= 1
        value = self.reg[operand_a]
        self.ram_write(value, self.SP)

        return (2, True)

    def cmp(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        return (3, True)

    def jmp(self, operand_a, operand_b):
        self.PC = self.reg[operand_a]
        return (0, True)

    def jeq(self, operand_a, operand_b):
        if self.FL == 0b00000001:
            self.PC = self.reg[operand_a]
            return(0, True)
        return (2, True)

    def jne(self, operand_a, operand_b):
        if self.FL != 0b00000001:
            self.PC = self.reg[operand_a]
            return(0, True)
        return (2, True)

    def load(self, program):
        try:
            address = 0

            with open(program) as f:
                for line in f:
                    comment_split = line.split("#")

                    number = comment_split[0].strip()

                    if number == "":
                        continue

                    value = int(number, 2)

                    self.ram_write(value, address)

                    address += 1

        except FileNotFoundError:
            print(f"{program} not found")
            sys.exit(2)

        if len(sys.argv) != 2:
            print(
                f"Please format the command like so: \n python3 ls8.py <filename>", file=sys.stderr)
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] = (self.reg[reg_a]) * (self.reg[reg_b])

        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b00000100
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
        else:
            raise Exception("ALU operation not supported")

    def trace(self):

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        running = True

        while running:
            IR = self.ram[self.PC]

            operand_a = self.ram_read(self.PC + 1)
            operand_b = self.ram_read(self.PC + 2)

            try:
                operation_output = self.commands[IR](operand_a, operand_b)

                running = operation_output[1]
                self.PC += operation_output[0]

            except:
                print(f"no such command: {IR}")
                sys.exit(1)
