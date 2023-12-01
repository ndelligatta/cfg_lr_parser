from enum import Enum

class SymbolType(Enum):
    NONTERMINAL = 0
    TERMINAL = 1
    DOT = 2

    def __str__(self):
        return self.name

class GrammarSymbol():
    symbol_type = None
    def __init__(self, symbol):
        self.symbol = symbol   

    def __str__(self):
        return f"{self.symbol}" 

    def get_symbol(self):
        return self.symbol
    
    def get_symbol_type(self):
        return self.symbol_type

class Terminal(GrammarSymbol):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.symbol_type = SymbolType.TERMINAL

class Nonterminal(GrammarSymbol):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.symbol_type = SymbolType.NONTERMINAL

class Production():
    def __init__(self, LHS, RHS):
        self.LHS = LHS
        self.RHS = RHS
    
    def get_LHS(self):
        return self.LHS

    def get_RHS(self):
        return self.RHS

    def __str__(self):
        return f"{self.LHS}->{self.RHS}"

class CFG():
    nonterminals = {"E", "T", "F"}
    terminals = {"+", "*", "(", ")", "id", "$"}
    rules = '''E->E+T
E->T
T->T*F
T->F
F->(E)
F->i'''
    productions = { }
    for rule in rules.split():
        LHS, RHS = rule.split("->")[:2]
        if LHS not in productions.keys():
            productions[LHS] = []
        productions[LHS].append(RHS)
    def get_productions(self, nonterminal):
        return self.productions[nonterminal]
    starting_state = "E"
    first_set = { 
        "E": {"(", "id"},
        "T": {"(", "id"},
        "F": {"(", "id"}
    }
    follow_set = {
        "E": {"+", ")", "$"},
        "T": {"+", "*", ")", "$"},
        "F": {"+", "*", ")", "$"}
    }

class ActionType(Enum):
    REDUCE = 0
    SHIFT = 1

class Action():
    def __init__(self, action, number):
        self.action = action
        self.number = number
    
    def __str__(self):
        if self.action == ActionType.REDUCE:
            return f"R{self.number}"
        else:
            return f"S{self.number}"

class ParseTable():
    def __init__(self):
        self.G = CFG()
        self.productions = self.G.productions
        self.starting_state = self.G.starting_state
        self.grammar = {}

    def itemize(self, RHS):
        return "." + RHS
    
    def get_symbol_after_dot(self, RHS):
        print(f"Length is {len(RHS)}")
        for i, symbol in enumerate(RHS):
            if symbol == "." and i + 1 != len(RHS):
                return RHS[i+1]

    def closure(self, symbol):
        rules = []
        for RHS in self.productions[symbol]:
            rules.append(self.itemize(RHS))
        return rules

    def augument_grammar(self):
        #self.grammar["Z"] = [self.itemize(self.starting_state)]
        self.productions["Z"] = [self.starting_state]
        x = 0
        for LHS in self.productions:
            for RHS in self.productions[LHS]:
                x += 1
                self.grammar[x] = (LHS, RHS)

    table = {
        0: {
            "i": "S5",
            "(": "S4",
            "E": "1",
            "T": "2",
            "F": "3"
        },
        1: {
            "+": "S6",
            "$": "acc"
        },
        2: {
            "+": "R2",
            "*": "S7",
            ")": "R2",
            "$": "R2"
        },
        3: {
            "+": "R4",
            "*": "R4",
            ")": "R4",
            "$": "R4"
        },
        4: {
            "i": "S5",
            "(": "S4",
            "E": "8",
            "T": "2",
            "F": "3"
        },
        5: {
            "+": "R6",
            "*": "R6",
            ")": "R6",
            "$": "R6"
        },
        6: {
            "i": "S5",
            "(": "S4",
            "T": "9",
            "F": "3"
        },
        7: {
            "i": "S5",
            "(": "S4",
            "F": "10"
        },
        8: {
            "+": "S6",
            ")": "S11"
        },
        9: {
            "+": "R1",
            "*": "S7",
            ")": "R1",
            "$": "R1"
        },
        10: {
            "+": "R3",
            "*": "R3",
            ")": "R3",
            "$": "R3"
        },
        11: {
            "+": "R5",
            "*": "R5",
            ")": "R5",
            "$": "R5"
        }
    }

class Parser():
    def __init__(self, input):
        self.input = input
        self.table = ParseTable().table
        self.grammar = ParseTable()
        self.grammar.augument_grammar()
        self.grammar = self.grammar.grammar
        self.stack = [0]
        self.step = 0
    def start(self):
        self.input = self.input.replace("id", "i")
        print(f"{'Step':<4} | {'Stack':<50}{'| Input':<11} {'| Next Step':<20}")
    def parse(self):
        self.step += 1
        next_entry = (self.table.get(int(self.stack[-1]), None))
        next_entry = next_entry.get(self.input[0], None)
        if next_entry is None:
            print("error, aborting")
            return -1
        print(f"{self.step:<4} | {str(self.stack):<50}{ f'| {self.input:<9}'} {f'| {next_entry:<3}'}")
        if next_entry[:1] == "S":
            self.stack.append(self.input[0])
            self.input = self.input[1:]
            self.stack.append(next_entry[1:])
        elif next_entry[:1] == "R":
            rule_number = int(next_entry[1:])
            selected_production = self.grammar[rule_number][1]
            for _ in range(len(selected_production) * 2):
                self.stack.pop()
            self.stack.append(self.grammar[rule_number][0])
            self.stack.append(self.table[int(self.stack[-2])][self.stack[-1]])
        elif next_entry == "acc":
            print("Done!")
            return 1
    def parse_string(self):
        output = 0
        while output != -1 and output != 1:
            output = self.parse()
        if output == 1:
            print("String is accepted")
        elif output == -1:
            print("String is not accepted")
        else:
            print("Well this is strange")
    
def main():
    input_string = ("(id+id)*id$")
    parser = Parser(input_string)
    parser.start()
    parser.parse_string()
    
if __name__ == "__main__":
    main()