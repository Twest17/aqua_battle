import time
import random
import logging


letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
# ship sizes
ships = [5, 4, 4, 4, 3]
# pc track location of last hitted ship
pc_hitted_ship = []
# player track location of last hitted ship
player_hitted_ship = []

your_table = {a + str(i): ' ' for a in letters for i in range(1, 11)}
pc_table = {a + str(i): ' ' for a in letters for i in range(1, 11)}
player_notes = {a + str(i): ' ' for a in letters for i in range(1, 11)}
pc_notes = {a + str(i): ' ' for a in letters for i in range(1, 11)}


def show_table(table):
    print('  1 2 3 4 5 6 7 8 9 10\n', end='')
    for i, key in enumerate(table, start=1):
        time.sleep(0.01)
        if i % 10 == 1:
            print(f'{key[0]:<2}', end='')
        print(f'{table[key]}', end=' ')
        if not i % 10:
            print(f'\n', end='')


def enough_space_for_ship(start_letter, start_number, orient, ship_size):
    # check that ship ends inside table
    if orient == 'h':
        if int(start_number) + ship_size - 1 > 10:
            return False
    else:
        try:
            letters[letters.index(start_letter) + ship_size - 1]
        except IndexError:
            return False
    return True


def building_ship(ship_start, orient, ship_size, table, check_mode=False):
    start_letter, start_number = ship_start[0], ship_start[1:]
    builded_ship_parts = {}

    if not enough_space_for_ship(start_letter, start_number, orient, ship_size):
        logging.info("not enough space for ship, choose another cell/orient")
        return {}

    for ship_part in range(ship_size):
        if orient == 'h':
            ship_part_loc = start_letter + str(int(start_number) + ship_part)
        else:
            ship_part_loc = letters[letters.index(start_letter) + ship_part] + start_number

        if table[ship_part_loc] != ' ':
            logging.info(f'Hit another ship at {ship_part_loc}! we need rebuild this')
            break
        builded_ship_parts[ship_part_loc] = 'S'

    # if we could not build entire ship we return empty dictionary as fail
    if len(builded_ship_parts) != ship_size:
        # we need return iterable, not bool,
        # because when pc 'check_valid_cells' for our remaining ships
        # in order to make move smart, he needs iterable
        return {}
    # check_mode == True when pc 'check_valid_cells'
    if not check_mode:
        area = get_area_around_ship(start_letter, start_number, orient, ship_size)
        table.update(area)
        table.update(builded_ship_parts)
    else:
        return builded_ship_parts
    return True


def get_area_around_ship(start_letter, start_number, orient, ship_size):
    # mark area around current ship with '.' to keep distance between ships
    area = {}
    if orient == 'h':
        down, right = 2, ship_size + 1
    else:
        right, down = 2, ship_size + 1

    # 1 cell up or start from index 0 if touch border
    start_letters = max(0, letters.index(start_letter) - 1)
    # 1 cell down + 1 b/c in range[start:end] 'end' not included
    end_letters = min(len(letters), letters.index(start_letter) + down)

    # 1 cell left or start from number 1 if touch border
    start_numbers = max(1, int(start_number) - 1)
    # 1 cell right + 1 b/c in range[start:end] 'end' not included
    end_numbers = min(11, int(start_number) + right)

    for let in letters[start_letters:end_letters]:
        for num in range(start_numbers, end_numbers):
            area[let + str(num)] = '.'
    return area


def planning(fleet, table):
    for ship in fleet:
        while True:
            print(f'\nYou are building ship of size {ship} right now...')
            try:
                ship_start = input(
                    '\nChoose up-left cell to put ship(A1-J10):')
                if table[ship_start] != ' ':
                    print('!->we already have ship here, try again')
                    continue
            except KeyError:
                print('!->incorrect cell')
                continue
            ship_orient = input(
                'Choose orientation for this ship(v-vertical, h-horizontal):')
            if ship_orient not in ('h', 'v'):
                print('!->incorrect orientation')
                continue
            if building_ship(ship_start, ship_orient, ship, table):
                show_table(table)
                print('Successful building, Captain!')
                time.sleep(1)
                break


def pc_planning(fleet, table):

    for ship in fleet:
        while True:
            ship_start = random.choice([c for c in table if table[c] == ' '])
            ship_orient = random.choice(['h', 'v'])
            if building_ship(ship_start, ship_orient, ship, table):
                break
    logging.basicConfig(level=logging.INFO)


def get_adjacent_cells(cell):
    letter, number = cell[0], cell[1:]

    up = letters[max(0, letters.index(letter) - 1)] + number
    down = letters[min(len(letters) - 1, letters.index(letter) + 1)] + number
    left = letter + str(max(1, int(number) - 1))
    right = letter + str(min(10, int(number) + 1))

    return {up, down, left, right}


def player_move():
    while True:
        move = input('\nPick a cell to hit:')
        if move == 'cheat':
            time.sleep(2)
            print('\nhaha, nice! Well, lets get look:')
            time.sleep(2)
            print('\nPC Table:')
            show_table(pc_table)
            time.sleep(1)
            continue
        if move in pc_table:
            return move
        print('Incorrect move, try again')


# calculate if ship of size m can be placed from cell i
# def func(i, m):
#     return not (i != (10 - m) * 10 and (
#             i // 10 > (9 - m)) and (i % 10 > (10 - m)
#                                     or i % 10 == 0))


def check_valid_cells():
    # here we check for too small areas for smallest remaining ship
    # and mark these areas with '-', so pc will not try them
    if min(ships) > 1:
        valid_cells = set()
        for i, cell in enumerate(pc_notes, start=1):
            if pc_notes[cell] != '-':  # and func(i, min(ships) - 1):
                for orient in ('h', 'v'):
                    # trying to place the shortest ship
                    # starting from 'cell' in both orientations
                    # add all cells that it fills, if it could be placed
                    valid_cells.update(
                        building_ship(cell, orient, min(ships), pc_notes, True))
        # cells through which no one ship could be placed
        invalid_cells = set(pc_notes) - valid_cells
        for inv in invalid_cells:
            pc_notes[inv] = '-'


def random_move():
    # before move check where remaining ships can't be
    logging.basicConfig(level=logging.ERROR)
    check_valid_cells()
    logging.basicConfig(level=logging.INFO)
    move = random.choice([c for c in pc_notes if pc_notes[c] != '-'])
    print('Machine random shot in', move)
    return move


def second_move(last_move):
    # after pc found your ship on last move he will try adjacent cells
    adjacent_moves = [cell for cell in get_adjacent_cells(last_move)
                      if pc_notes[cell] != '-']
    move = random.choice(adjacent_moves)
    print(f'\nMachine second shot in {move}')
    return move


def third_move():
    # after two successful shots pc know orientation
    # of your ship and will try on tails

    # if letters of two ship parts equal --> orientation horizontal
    orient = pc_hitted_ship[1][0] == pc_hitted_ship[0][0]
    # sort ship parts to define start and end cells of your ship
    sorted_ship = sorted(
        pc_hitted_ship, key=lambda x: int(x[1:]) if orient else x[0])
    start_letter, start_number = sorted_ship[0][0], sorted_ship[0][1:]
    last_letter, last_number = sorted_ship[-1][0], sorted_ship[-1][1:]

    cell1, cell2 = sorted_ship[0], sorted_ship[0]

    if orient:  # horizontal
        # if not touch border on left,
        # first tail will be to the left from start
        if start_number != '1':
            cell1 = start_letter + str(int(start_number) - 1)
        # if not touch border on right,
        # second tail will be to the right from end
        if last_number != '10':
            cell2 = start_letter + str(int(last_number) + 1)

    else:  # vertical
        # if not touch border up above,
        # first tail will be above to the start
        if start_letter != 'A':
            cell1 = letters[letters.index(start_letter) - 1] + start_number
        # if not touch border down below,
        # second tail will be below to the end
        if last_letter != 'J':
            cell2 = letters[letters.index(last_letter) + 1] + start_number

    move = random.choice([c for c in (cell1, cell2) if pc_notes[c] != '-'])
    print(f'\nMachine another shot in {move}')
    return move


def clean_area_around(dead_ship, table):
    # print('Cleaning cells around...')
    # horizontal if letters are the same
    orient = 'h' if (len(dead_ship) > 1) and (
            dead_ship[1][0] == dead_ship[0][0]) else 'v'
    # sort ship parts for picking left-upper corner as start point
    # then use start point to get area around dead ship and mark this area with '-'
    dead_ship.sort(key=lambda x: x[0] if orient == 'v' else int(x[1:]))
    start_letter, start_number = dead_ship[0][0], dead_ship[0][1:]
    for cell in get_area_around_ship(start_letter, start_number, orient, len(dead_ship)):
        table[cell] = '-'
    # print('Finish cleaning')


def hit(move, table, hit_counter=0):
    time.sleep(1)
    if table == your_table:  # pc move
        if your_table[move] == 'S':  # hit
            print(f'\nMachine hit you in {move}!')
            hit_counter += 1
            pc_hitted_ship.append(move)
            your_table[move] = '-'  # not needed?
            pc_notes[move] = '-'
            if check_crash(your_table):
                ships.remove(hit_counter)
                hit_counter = 0
            return True, hit_counter
        # pc miss
        print(f'\nMachine missed')
        your_table[move] = '-'  # not needed?
        pc_notes[move] = '-'
        return False, hit_counter
    if pc_table[move] == 'S':  # player hit
        print('\nOuch! What a shot! Hit!')
        pc_table[move] = 'X'
        player_notes[move] = 'X'
        player_hitted_ship.append(move)
        check_crash(pc_table)
        return True
    player_notes[move] = '-'  # player miss


def check_crash(table):
    # choose which(pc or yours) tracked ship parts to check
    ship, pc_move = (pc_hitted_ship, True) if table == your_table else (player_hitted_ship, False)

    # collect all adjacent cells for all tracked ship parts
    around_ship = set()
    for ship_part in ship:
        around_ship.update(get_adjacent_cells(ship_part))

    # if not 'alive' ship parts around, ship is crashed
    if 'S' not in [table[cell] for cell in around_ship]:
        if pc_move:  # pc crashed your ship
            print('pc crashed your ship!')
            # clean_area_around(ship, your_table)  # not needed?
            clean_area_around(ship, pc_notes)
            pc_hitted_ship.clear()
            return True
        else:  # player crashed pc ship
            print('You crashed a ship!')
            clean_area_around(ship, player_notes)
            # player_notes.update({ship_part: 'X' for ship_part in pc_hitted_ship})  # wtf? not needed???
            # fix this

            player_hitted_ship.clear()


def check_win():
    if 'S' not in your_table.values():
        print('Machine unbeatable again! Machine wins!')
        return True
    if 'S' not in pc_table.values():
        print("You've made it! You win!")
        return True


def main():
    # planning(ships, your_table)
    # use pc_planning for auto-fill player's table
    logging.basicConfig(level=logging.ERROR, format='%(message)s')
    pc_planning(ships, your_table)
    logging.basicConfig(level=logging.INFO)
    print('Players table:')
    show_table(your_table)
    time.sleep(1)
    print('\nPC Building...\n')
    pc_planning(ships, pc_table)
    # print('TABLE2')
    # show_table(pc_table)
    time.sleep(1)
    print('Ready? Fight!\n')

    # when pc hit your ship, you are shocked and pc continues
    shocked = False
    # need to track last pc move, so if pc hit you,
    # pc continues with second move, which depends on this last move
    last_move = None
    # how many times pc hit you in a row. it will change pc strategy
    hit_counter = 0
    # just statistics for fun
    moves_to_win = 0

    while not check_win():
        moves_to_win += 1
        # if pc not hit you, you are not shocked and can make a move
        if not shocked:
            you_hit = hit(player_move(), pc_table)
            print('\nYour notes:')
            show_table(player_notes)
            time.sleep(1.5)
            if you_hit:
                continue
            print('\nYou missed\n')
            time.sleep(1.5)
        # pc once hit your ship with his random move, so it now will try on adjacent cells
        if hit_counter == 1:
            shocked, hit_counter = hit(second_move(last_move), your_table, hit_counter)
            continue
        # pc hits your ship at least twice, so he knows now orientation of your ship and will try crash it
        elif hit_counter > 1:
            shocked, hit_counter = hit(third_move(), your_table, hit_counter)
            continue
        # first pc move is random. consecutive is smarter
        logging.basicConfig(level=logging.ERROR)
        last_move = random_move()
        logging.basicConfig(level=logging.INFO)
        shocked, hit_counter = hit(last_move, your_table)
        time.sleep(1.5)
        print('\nYour Table:')
        show_table(your_table)

    print('\nYour Table:')
    show_table(your_table)
    print('PC Table:')
    show_table(pc_table)
    _ = input(f'{moves_to_win} moves to win, press key:')


main()
