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
