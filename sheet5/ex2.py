from random import choice, randrange

class Formula:
    def __add__(self, other):
        return Or(self, other)
    def __mul__(self, other):
        return And(self, other)
    def simplified(self):
        return self
    
    @staticmethod
    def tautology(formula):
        variables = []
        
        # find names of all variables occuring in the formula
        def find_variables(formula):
            if isinstance(formula, Variable):
                variables.append(str(formula))
            elif isinstance(formula, Or) or isinstance(formula, And) or isinstance(formula, Implies) or isinstance(formula, Iff):
                find_variables(formula.sub1)
                find_variables(formula.sub2)
            elif isinstance(formula, Not):
                find_variables(formula.sub)
        
        valuation = {}
        
        # check if the formula is true for every possible valuation of its variables
        def satisfied(variables):
            if len(variables) == 0:
                return formula.evaluate(valuation)
            valuation[variables[0]] = False
            if not satisfied(variables[1:]):
                return False
            valuation[variables[0]] = True
            return satisfied(variables[1:])
        
        find_variables(formula)
        return satisfied(variables)
        
class Or(Formula):
    # "sub" stands for "subformula"
    def __init__(self, sub1, sub2):
        if isinstance(sub1, Formula) and isinstance(sub2, Formula):
            self.sub1 = sub1
            self.sub2 = sub2
        else:
            raise TypeError("Subformulas have to be instances of Formula")
        
    # assumption: "variables" is a dictionary
    # the return value is True or False
    def evaluate(self, variables):
        if self.sub1.evaluate(variables):
            return True
        return self.sub2.evaluate(variables)
    
    def __str__(self):
        sub1 = str(self.sub1) if isinstance(self.sub1, Constant) or isinstance(self.sub1, Variable) or isinstance(self.sub1, Not) else "(" + str(self.sub1) + ")"
        sub2 = str(self.sub2) if isinstance(self.sub2, Constant) or isinstance(self.sub2, Variable) or isinstance(self.sub2, Not) else "(" + str(self.sub2) + ")"
        return sub1 + " ∨ " + sub2
    
    # simplify the formula
    def simplified(self):
        # P ∨ P ≡ P
        if str(self.sub1) == str(self.sub2):
            return self.sub1
        if isinstance(self.sub1, Constant):
            # ⊤ ∨ P ≡ ⊤ 
            if self.sub1.value == True:
                return Constant(True)
            # ⊥ ∨ P ≡ P
            return self.sub2.simplified()
        if isinstance(self.sub2, Constant):
            # P ∨ ⊤ ≡ ⊤ 
            if self.sub2.value == True:
                return Constant(True)
            # P ∨ ⊥ ≡ P
            return self.sub1.simplified()
        return Or(self.sub1.simplified(), self.sub2.simplified())

class And(Formula):
    def __init__(self, sub1, sub2):
        if isinstance(sub1, Formula) and isinstance(sub2, Formula):
            self.sub1 = sub1
            self.sub2 = sub2
        else:
            raise TypeError("Subformulas have to be instances of Formula")
        
    def evaluate(self, variables):
        if not self.sub1.evaluate(variables):
            return False
        return self.sub2.evaluate(variables)
    
    def __str__(self):
        sub1 = str(self.sub1) if isinstance(self.sub1, Constant) or isinstance(self.sub1, Variable) or isinstance(self.sub1, Not) else "(" + str(self.sub1) + ")"
        sub2 = str(self.sub2) if isinstance(self.sub2, Constant) or isinstance(self.sub2, Variable) or isinstance(self.sub2, Not) else "(" + str(self.sub2) + ")"
        return sub1 + " ∧ " + sub2
    
    def simplified(self):
        # P ∧ P ≡ P
        if str(self.sub1) == str(self.sub2):
            return self.sub1
        if isinstance(self.sub1, Constant):
            # ⊥ ∧ P ≡ ⊥ 
            if self.sub1.value == False:
                return Constant(False)
            # ⊤ ∧ P ≡ P
            return self.sub2.simplified()
        if isinstance(self.sub2, Constant):
            # P ∧ ⊥ ≡ ⊥ 
            if self.sub2.value == False:
                return Constant(False)
            # P ∧ ⊤ ≡ P
            return self.sub1.simplified()
        return And(self.sub1.simplified(), self.sub2.simplified())
    
class Implies(Formula):
    def __init__(self, sub1, sub2):
        if isinstance(sub1, Formula) and isinstance(sub2, Formula):
            self.sub1 = sub1
            self.sub2 = sub2
        else:
            raise TypeError("Subformulas have to be instances of Formula")
        
    # implication is true if sub1 is false or sub1 and sub2 are true
    def evaluate(self, variables):
        if not self.sub1.evaluate(variables):
            return True
        return self.sub2.evaluate(variables)
    
    def __str__(self):
        sub1 = str(self.sub1) if isinstance(self.sub1, Constant) or isinstance(self.sub1, Variable) or isinstance(self.sub1, Not) else "(" + str(self.sub1) + ")"
        sub2 = str(self.sub2) if isinstance(self.sub2, Constant) or isinstance(self.sub2, Variable) or isinstance(self.sub2, Not) else "(" + str(self.sub2) + ")"
        return sub1 + " ⟹ " + sub2
    
    def simplified(self):
        # P ⟹ P ≡ ⊤ 
        if str(self.sub1) == str(self.sub2):
            return Constant(True)
        if isinstance(self.sub1, Constant):
            # ⊥ ⟹ P ≡ ⊤
            if self.sub1.value == False:
                return Constant(True)
            # ⊤ ⟹ P ≡ P
            return self.sub2.simplified()
        if isinstance(self.sub2, Constant):
            # P ⟹ ⊥ ≡ ¬P
            if self.sub2.value == False:
                return Not(self.sub1.simplified())
            # P ⟹ ⊤ ≡ ⊤
            return Constant(True)
        return Implies(self.sub1.simplified(), self.sub2.simplified())
    
class Iff(Formula):
    def __init__(self, sub1, sub2):
        if isinstance(sub1, Formula) and isinstance(sub2, Formula):
            self.sub1 = sub1
            self.sub2 = sub2
        else:
            raise TypeError("Subformulas have to be instances of Formula")
        
    def evaluate(self, variables):
        return self.sub1.evaluate(variables) == self.sub2.evaluate(variables)
    
    def __str__(self):
        sub1 = str(self.sub1) if isinstance(self.sub1, Constant) or isinstance(self.sub1, Variable) or isinstance(self.sub1, Not) else "(" + str(self.sub1) + ")"
        sub2 = str(self.sub2) if isinstance(self.sub2, Constant) or isinstance(self.sub2, Variable) or isinstance(self.sub2, Not) else "(" + str(self.sub2) + ")"
        return sub1 + " ⇔ " + sub2
    
    def simplified(self):
        # P ⇔ P ≡ ⊤ 
        if str(self.sub1) == str(self.sub2):
            return Constant(True)
        if isinstance(self.sub1, Constant):
            # ⊥ ⇔ P ≡ ¬P
            if self.sub1.value == False:
                return Not(self.sub2.simplified())
            # ⊤ ⇔ P ≡ P
            return self.sub2.simplified()
        if isinstance(self.sub2, Constant):
            # P ⇔ ⊥  ≡ ¬P
            if self.sub2.value == False:
                return Not(self.sub1.simplified())
            # P ⇔ ⊤ ≡ P
            return self.sub1.simplified()
        return Iff(self.sub1.simplified(), self.sub2.simplified())

class Not(Formula):
    def __init__(self, sub):
        if isinstance(sub, Formula):
            self.sub = sub
        else:
            raise TypeError("Subformulas have to be instances of Formula")
        
    def evaluate(self, variables):
        return not self.sub.evaluate(variables)
    
    def __str__(self):
        sub = str(self.sub) if isinstance(self.sub, Constant) or isinstance(self.sub, Variable) else "(" + str(self.sub) + ")"
        return "¬" + sub
    
    def simplified(self):
        if isinstance(self.sub, Constant):
            # ¬⊥ ≡ ⊤
            if self.sub.value == False:
                return Constant(True)
            # ¬⊤ ≡ ⊥ 
            return Constant(False)
        # ¬(¬P) ≡ P
        if isinstance(self.sub, Not):
            return self.sub.sub.simplified()
        return Not(self.sub.simplified())
    
class Constant(Formula):
    def __init__(self, value):
        if isinstance(value, bool):
            self.value = value
        else:
            raise TypeError("The value of Constant has to be True or False")
        
    def evaluate(self, variables):
        return self.value
    
    def __str__(self):
        return "⊤" if self.value == True else "⊥"
    
class Variable(Formula):
    def __init__(self, name):
        if isinstance(name, str):
            for c in [" ", "(", ")", "∨", "∧", "⟹", "⇔", "¬", "⊥", "⊤"]:
                if c in name:
                    raise InvalidVariableName(name + " is an invalid variable name")
            self.name = name
        else:
            raise TypeError("The name of a variable has to be a string")
        
    def evaluate(self, variables):
        if self.name not in variables:
            raise UnassignedVariable("Unassigned variable: " + self.name)
        if not isinstance(variables[self.name], bool):
            raise TypeError("The value of a variable has to be True or False")
        return variables[self.name]
    
    def __str__(self):
        return self.name

class UnassignedVariable(Exception):
    pass

class InvalidVariableName(Exception):
    pass

def generate_formula(n):
    if n == 0:
        options = ["constant", "variable"]
        chosen = choice(options)
        if chosen == "constant":
            return Constant(choice([True, False]))
        else:
            return Variable(choice("pqrs"))
    options = ["constant", "variable", "or", "and", "implies", "iff", "not"]
    chosen = choice(options)
    if chosen == "constant":
        return Constant(choice([True, False]))
    elif chosen == "variable":
        return Variable(choice("pqrs"))
    elif chosen == "or":
        return Or(generate_formula(n - 1), generate_formula(n - 1))
    elif chosen == "and":
        return And(generate_formula(n - 1), generate_formula(n - 1))
    elif chosen == "implies":
        return Implies(generate_formula(n - 1), generate_formula(n - 1))
    elif chosen == "iff":
        return Iff(generate_formula(n - 1), generate_formula(n - 1))
    else:
        return Not(generate_formula(n - 1))

##############################################
# Tests
##############################################

formula1 = Or(Not(Variable("p")), And(Variable("q"), Constant(True)))
formula2 = Implies(And(Variable("p"), Constant(False)), Not(Iff(Variable("q"), Variable("p"))))
print(formula1)
print(formula1.simplified())
print()
print(formula2)
print(formula2.simplified())
print(formula2.simplified().simplified())
print()
print(formula1 + formula2)
print(formula1 * formula2)
print()
print(Formula.tautology(formula1))
print(Formula.tautology(formula2))
print()
print(formula1.evaluate({"p": False, "q": False}))
print(formula1.evaluate({"p": False, "q": True}))
print(formula1.evaluate({"p": True, "q": False}))
print(formula1.evaluate({"p": True, "q": True}))
try:
    formula = And(Constant(True), "abc")
except TypeError as e:
    print(e)
try:
    print(formula1.evaluate({"p": "hello", "q": False}))
except TypeError as e:
    print(e)
try:
    print(formula1.evaluate({"p": True}))
except UnassignedVariable as e:
    print(e)
try:
    formula = Or(Variable("⊥"), Not(Variable("q")))
except InvalidVariableName as e:
    print(e)
print()

# De Morgan's laws
de_morgan_1 = Iff(Not(And(Variable("p"), Variable("q"))), Or(Not(Variable("p")), Not(Variable("q"))))
de_morgan_2 = Iff(Not(Or(Variable("p"), Variable("q"))), And(Not(Variable("p")), Not(Variable("q"))))
print(de_morgan_1)
print(de_morgan_2)
print(de_morgan_1 + de_morgan_2)
print(de_morgan_1 * de_morgan_2)
print(Formula.tautology(de_morgan_1))
print(Formula.tautology(de_morgan_2))
print()

# generate 10 random formulas, simplify them as much as possible and check if they are tautologies
for i in range(10):
    formula = generate_formula(randrange(3, 7))
    print(formula)
    prev = str(formula)
    cur = formula.simplified()
    while str(cur) != prev:
        print(cur)
        prev, cur = str(cur), cur.simplified()
    print(Formula.tautology(formula))
    print()