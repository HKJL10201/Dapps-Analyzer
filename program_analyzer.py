

class Program():
    def __init__(self, name, code) -> None:
        self.name = name
        self.code = code
        self.contracts = []
        self.interfaces = []
        self.libraries = []

    def set_contracts(self, contracts):
        self.contracts = contracts

    def print(self):
        print(self.name)
        for contract in self.contracts+self.interfaces+self.libraries:
            contract.print()


class Contract():
    def __init__(self, name, code) -> None:
        self.name = name
        self.code = code
        self.functions = []
        self.defined_names = []
        self.sign = {'name': '', 'inherit': []}
        self.instances = []

    def set_functions(self, functions):
        self.functions = functions

    def get_function_names(self):
        names = []
        for f in self.functions:
            if len(f.sign['name']) > 0:
                names.append(' '.join(f.sign['name']))
        return names

    def set_defined_names(self):
        self.defined_names += self.get_function_names()

    def set_sign(self, name, inherit):
        self.sign['name'] = name
        self.sign['inherit'] = inherit

    def print(self):
        print(' '.join(self.name))
        print('inherits: '+str(self.sign['inherit']))
        print('defined_names: '+str(self.defined_names))
        for function in self.functions:
            function.print()


class Function():
    def __init__(self) -> None:
        self.name = []
        self.code = []
        self.sign = {}

    def __init__(self, name, code) -> None:
        self.name = name
        self.code = code
        self.sign = {}

    def set_sign(self, name, para, scope, returns):
        self.sign['name'] = name
        self.sign['para'] = para
        self.sign['scope'] = scope
        self.sign['returns'] = returns

    def set_sign_raw(self, sign):
        self.sign['raw'] = sign

    def print(self):
        print(self.sign)


def init(filename):
    with open(filename, 'r') as f:
        code = []
        for line in f:
            words = line.strip().split()
            code.append(words)
    return code


def get_next(code, i, j):
    if j+1 < len(code[i]):
        return code[i][j+1], i, j+1
    else:
        i += 1
        while i < len(code):
            if len(code[i]) == 0:
                i += 1
                continue
            return code[i][0], i, 0
        return None, i, len(code[i-1])


def preprocess(code):   # comments filter
    res = []
    i = 0
    while i < len(code):
        line = code[i]
        j = 0
        while j < len(line):
            word = line[j]
            if '//' in word:
                t_idx = word.index('//')
                if t_idx != 0:
                    res.append(word[:t_idx])
                break
            elif '/*' in word:
                t_idx = word.index('/*')
                if t_idx != 0:
                    res.append(word[:t_idx])
                while True:
                    word, i, j = get_next(code, i, j)
                    if word == None:
                        break
                    if '*/' in word:
                        t_idx = word.index('*/')
                        if t_idx != len(word)-2:
                            res.append(word[t_idx+2])
                        break
                if word == None:
                    break
            else:
                res.append(word)
            j += 1
        i += 1
    return res


def program_analyzer(program):
    def get_content(i, code):
        word = code[i]
        c_name = []
        c_code = []
        while word != '{':
            c_name.append(word)
            i += 1
            if i >= len(code):
                return i, c_name, c_code
            word = code[i]

        c_flag = 1
        while c_flag != 0:
            i += 1
            if i >= len(code):
                return i, c_name, c_code
            word = code[i]
            c_code.append(word)
            if word == '{':
                c_flag += 1
            elif word == '}':
                c_flag -= 1
        return i, c_name, c_code

    code = program.code
    code = ' '.join(code).replace('{', ' { ').replace('}', ' } ').split()
    contracts = []
    interfaces = []
    libraries = []
    i = 0
    while i < len(code):
        word = code[i]
        if word == 'contract':
            i, c_name, c_code = get_content(i, code)
            contracts.append(Contract(c_name, c_code))
        elif word == 'interface':
            i, c_name, c_code = get_content(i, code)
            interfaces.append(Contract(c_name, c_code))
        elif word == 'library':
            i, c_name, c_code = get_content(i, code)
            libraries.append(Contract(c_name, c_code))
        i += 1
    program.set_contracts(contracts)
    program.interfaces = interfaces
    program.libraries = libraries


def contract_name_formatter(contract):
    name = contract.name
    name = ' '.join(name).replace(',', ' , ').split()
    n = len(name)
    i = 0
    is_flag = 0
    c_name = ''
    c_inherit = []
    while i < n:
        if name[i] == 'contract' or name[i] == 'interface' or name[i] == 'library':
            i += 1
            if i < n:
                c_name = name[i]
        elif name[i] == 'is':
            is_flag = 1
        elif name[i] == ',':
            i += 1
            continue
        elif is_flag == 1:
            c_inherit.append(name[i])
        i += 1
    contract.set_sign(c_name, c_inherit)


def contract_analyzer(contract):
    contract_name_formatter(contract)
    code = contract.code
    code = ' '.join(code).replace(
        '(', ' ( ').replace(')', ' ) ').replace(';', ' ; ').split()
    defined = ['struct', 'event']
    functions = []
    i = 0
    while i < len(code):
        word = code[i]
        if word == 'using':
            i += 1
            if i < len(code):
                word = code[i]
                contract.sign['inherit'].append(word)
        elif word in defined:
            i += 1
            if i < len(code):
                word = code[i]
                contract.defined_names.append(word)
        elif word == 'function':
            f_name = []
            f_code = []
            while word != '{':
                if word == ';':   # for interface
                    functions.append(Function(f_name, f_code))
                    break
                f_name.append(word)
                i += 1
                if i >= len(code):
                    break
                word = code[i]
            if i >= len(code):
                break
            if word == ';':   # for interface
                i += 1
                continue
            '''if len(f_name)>=2:
                if ''.join(f_name[:2])=='function(':
                    i+=1
                    continue'''

            f_flag = 1
            while f_flag != 0:
                i += 1
                if i >= len(code):
                    break
                word = code[i]
                f_code.append(word)
                if word == '{':
                    f_flag += 1
                elif word == '}':
                    f_flag -= 1
            functions.append(Function(f_name, f_code))
        i += 1
    contract.set_functions(functions)


def function_analyzer(func):
    name = func.name
    raw_name = ' '.join(name).replace(
        '(', ' ( ').replace(')', ' ) ').replace(',', ' , ')
    name = raw_name.split()
    i = 0
    f_name = []
    while i < len(name) and name[i] != '(':
        if name[i] != 'function':
            f_name.append(name[i])
        i += 1

    f_para = []
    t_para = []
    while i < len(name) and name[i] != ')':
        if name[i] == ',':
            f_para.append(' '.join(t_para))
            t_para = []
        else:
            if name[i] != '(':
                t_para.append(name[i])
        i += 1
    f_para.append(' '.join(t_para))

    f_scope = []
    while i < len(name) and name[i] != 'returns':
        if name[i] != ')':
            f_scope.append(name[i])
        i += 1

    f_returns = []
    t_returns = []
    while i < len(name):
        if name[i] == ',':
            f_returns.append(' '.join(t_returns))
            t_returns = []
        else:
            if name[i] != 'returns' and name[i] != '(' and name[i] != ')':
                t_returns.append(name[i])
        i += 1
    if len(t_returns) > 0:
        f_returns.append(' '.join(t_returns))

    func.set_sign(f_name, f_para, f_scope, f_returns)


def analyze(promgram):
    program_analyzer(promgram)
    for c in promgram.contracts+promgram.interfaces+promgram.libraries:
        contract_analyzer(c)
        for f in c.functions:
            function_analyzer(f)
        c.set_defined_names()


def main(file):
    code = preprocess(init(file))
    p = Program(file, code)
    analyze(p)
    return p


def test():
    FILE = 'tkf.sol'
    p = main(FILE)
    p.print()


# test()
