
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
FIRST_LETTER = LETTERS[0]

def get_sequence(column, count, step=1):
    column = validate(column)
    count = max(abs(count), 1)

    sequence = []
    if column:
        sequence.append(column)
        count = count - 1

    for i in range(count):
        previous = sequence[-1] if sequence else column
        sequence.append(next(previous, step))

    return sequence

def next(column, step=1):
    column = validate(column)
    if not column:
        return FIRST_LETTER

    step = max(abs(step), 1)
    base = column[0:-1] if len(column) > 1 else ''
    next_char = column[-1] if len(column) > 1 else column
    for i in range(step):
        next_char = get_next_char(next_char)
        if next_char == FIRST_LETTER:
            base = rollover(base)

    return base + next_char

def rollover(column):
    if not column:
        return FIRST_LETTER

    base = column[0:-1]
    next_char = get_next_char(column[-1])
    if next_char == FIRST_LETTER:
        return rollover(base) + next_char

    return base + next_char

def get_next_char(char): 
    index = LETTERS.index(char) + 1
    return FIRST_LETTER if index >= len(LETTERS) else LETTERS[index]

def validate(column):
    if not column:
        return None

    column = column.strip().upper()
    invalid_chars = [c for c in column if c not in LETTERS]
    return None if invalid_chars else column