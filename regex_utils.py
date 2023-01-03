def locate_union_symb(rex, pos=0):
    bracket_counter = 0
    while pos < len(rex) and bracket_counter >= 0:
        cursymb = rex[pos]
        if cursymb == '(':
            bracket_counter += 1
        elif cursymb == ')':
            bracket_counter -= 1
        elif cursymb == '|' and bracket_counter == 0:
            return pos
        pos += 1
    return None


def _expand_plus(rex, pos=0):
    new_rex = ''
    while pos < len(rex):
        cursymb = rex[pos]
        if cursymb == '(':
            currex, pos = _expand_plus(rex, pos+1)
            if pos == len(rex) or rex[pos] != ')':
                raise ValueError('missing closing bracket')
            currex = '(' + currex + ')'
        elif cursymb == ')':
            return new_rex, pos
        else:
            currex = cursymb
        pos += 1
        rex_modifier = rex[pos] if pos < len(rex) else ''
        if rex_modifier == '+':
            currex = currex + currex + '*'
            pos += 1
        elif rex_modifier in ('?', '*'):
            currex += rex_modifier
            pos += 1
        new_rex += currex
    return new_rex, pos


def expand_plus(rex):
    newrex, _ = _expand_plus(rex)
    return newrex
