import program_analyzer as PA
from dapp_analyzer import dic_to_string


def get_program_from_file(filepath):
    return PA.main(filepath)


def get_contract_from_file(filepath, name):
    p = get_program_from_file(filepath)
    for c in p.contracts:
        if c.sign['name'] == name:
            return c


def get_functions_from_file(filepath, name):
    p = get_program_from_file(filepath)
    res = []
    for c in p.contracts:
        for f in c.functions:
            if ' '.join(f.sign['name']) == name:
                res.append(f)
    return res


def compare_program(a, b, mode='function', ignore_contracts=[]):
    idx, content = a.compare_with(b, mode, ignore_contracts)
    if idx == 0:
        return 'No similarity'
    elif idx == 1:
        return content
    elif idx == 2:
        return dic_to_string(0, content)


def test():
    file = '658.sol'
    fb = '6580.sol'
    a = get_program_from_file(file)
    b = get_program_from_file(fb)
    print(compare_program(a, b))


test()
