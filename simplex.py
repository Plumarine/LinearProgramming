__author__ = 'Ma7aseem'
# Simplex algorithm pivoting tool by Abdulla Almansoori
# Use this as a test input: simplex('x + y', 'x y', '2x + y <= 4', 'x + 2y <= 4')
# or this simplex("x + y - z", "x y z xyz", "2x + y - xyz <= 4", "x + 2y +10*z <= 4", "5>= .7 y - xyz")
# or this simplex("3xcococo+5x22", "xcococo x22", "xcococo<=4", "2x22<=12", "3*xcococo+2x22<=18")

import time
import re


def simplex(objective, variables, *constraints):
    # --- INITIALIZATION ---
    start_time = time.time()
    # Initialize functions
    # A function to check if string s is a number
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    # A function to show results (tableau format)
    def show_tab(tab, allvars, bas, step, prec):
        m = 0
        cell = 0  # Cell size

        cell_sizes = [[]]
        for x in allvars:
            size = len(x)
            cell_sizes[0].append(size)
            if size > cell:
                cell = size
        m += 1
        for row in tab:
            cell_sizes.append([])
            for x in row:
                x = float(x)
                if x.is_integer():
                    x = int(x)
                else:
                    x = round(x, prec)
                size = len(str(x))
                cell_sizes[m].append(size)
                if size > cell:
                    cell = size
            m += 1

        cell += 2  # Cell space (with spaces at the edges)

        firstrow = "_" * (cell - 2) + " "
        nsize, msize = len(allvars), len(bas) + 1
        n = 0
        while n < nsize:
            cellspace = cell - cell_sizes[0][n]
            ls = int(cellspace / 2)
            rs = cellspace - ls
            firstrow += "|" + ls * " " + str(allvars[n]) + rs * " "
            n += 1

        print("Tableau Step %d" % step)
        print(firstrow)
        m = 0
        while m < msize:
            if m < msize - 1:
                basind = allvars.index(bas[m])
                row = bas[m] + (cell - 1 - cell_sizes[0][basind]) * " "
            else:
                row = "P" + " " * (cell - 2)
            n = 0
            while n < nsize:
                cellspace = cell - cell_sizes[m + 1][n]
                rs = cellspace - 1
                val = float(tab[m][n])
                if val.is_integer():
                    val = int(val)
                else:
                    val = round(val, prec)
                row += "|" + " " + str(val) + rs * " "
                n += 1
            print(row)
            m += 1
        print("\n")

    # A function to make expressions look nicer
    def make_pretty(expr):

        expr = expr.replace("*","")

        i = 0
        skip = False  # skip the remaining of variable letters
        while i < len(expr):  # Make space before every variable
            if skip:
                if expr[i] == "+" or expr[i] == "-" or expr[i] == "=":
                    skip = False
            elif expr[i].isalpha():
                expr = expr[0:i] + " " + expr[i:]  # or "*" in case the user wants a "*" between numbers and variables
                skip = True
            i += 1

        if expr[0] == " ":
            expr = expr[1:]

        expr = expr.replace("<=", " <= ")
        expr = expr.replace(">=", " >= ")
        expr = expr.replace("+"," + ")
        expr = expr.replace("-"," - ")
        #expr = expr.replace("**"," *")  # In case the user wants the "*" format
        #expr = expr.replace("*"," * ")  # In case the user wants the "*" format

        return expr

    # Initialize variables and lists
    errors = []
    constraints = list(constraints)
    variables = variables.split()
    varset = set(variables)
    numconst = len(constraints)
    numvar = len(variables)
    exprlist = list(constraints)
    exprlist.append(objective)
    precision = 3  # Notice this should be an option
    basic = []
    i = 1
    while i < numconst + 1:
        basic.append("s" + str(i))
        i += 1
    vartab = variables + basic
    vartab.append("P")
    vartab.append("C")

    # Initialize dictionary matrix
    sim = [[0 for x in range(2+numvar+numconst)] for x in range(1+numconst)]

    # Rid expressions of all spaces
    objective = objective.replace(' ', '')
    i = 0
    for const in constraints:
        constraints[i] = const.replace(' ', '')
        i += 1
    # --- CHECKING INPUT ---

    # Check decision variables input
    varcheck = re.compile("^[A-Za-z][A-Za-z0-9_]*$")
    for var in variables:
        if len(var) > 15:
            errors.append("Decision variables => %s is too long!")
        elif not re.match(varcheck, var):
            errors.append("Decision variables => syntax error")

    # Check if there are duplicate declared variables
    if len(varset) < len(variables):
        errors.append("Decision variables => duplicate variables!")

    # --- SETTING THE MATRIX---

    # Assiging values of 1 to slacks in constraint
    i = 0
    for row in exprlist:
        sim[i][numvar+i] = 1
        i += 1

    # Go through expressions
    objcheck = re.compile("^[+-.0-9/*a-zA-Z_]+$")
    constcheck = re.compile("^[+-.0-9/*a-zA-Z_]+[<>]=[+-.0-9/*a-zA-Z_]+$")
    badsym = ['++', '--', '**', '+$', '-$', '*$', '+*', '-*', '+<', '-<', '*<', '+>' '->', '*>']
    varmode = False
    i = 0
    if not errors:
        for row in exprlist:
            # Reinitialize some variables
            lhs, rhs = 1, -1
            var, coeff = '', ''
            switchside = False
            err = False
            objc = 1
            if i == numconst:  # To make objective function values the opposite for the tableau
                objc = -1

            # Check symbols in input
            if i == numconst:
                if not re.match(objcheck, row):
                    errors.append("Objective function => unknown symbols used")
                    continue
            else:
                if not re.match(constcheck, row):
                    errors.append("Constraint #%d => unknown symbols used" % (i + 1))
                    continue

            row += '$'  # Mark end of expression

            # Add + at before unsigned variables and check < or >
            if row[0] != '+' and row[0] != '-':
                row = '+' + row
            if i < numconst:
                x = row.index('=')
                if row[x+1] != '+' and row[x+1] != '-':
                    row = row.replace('=', '=+')
                if '>' in row:
                    lhs, rhs = -1, 1  # Just change sign convention if >= was used instead

            side = lhs
            cnum = 0
            for sym in badsym:
                if sym in row:
                    err = True
                    break
            if not err:
                for c in row:
                    if c == '=':
                        continue
                    elif c == '*':  # Check if coefficient is number and next character is a letter (variable)
                        if not row[cnum+1].isalpha() or not is_number(coeff):
                            err = True
                            break

                    elif c == '>' or c == '<':
                        switchside = True

                    elif c == '+' or c == '-' or c == '$':
                        if coeff == '+' or coeff == '-':
                            coeff += '1'
                        if is_number(coeff):
                            if not var:  # Variable is empty, meaning it's a number
                                sim[i][-1] = -1 * side * objc * float(coeff)
                            elif var in variables:  # Check if variable declared
                                x = variables.index(var)
                                sim[i][x] = side * objc * float(coeff)
                            else:
                                if i == numconst:
                                    errors.append("Objective function => undeclared variable %s" % var)
                                else:
                                    errors.append("Constraint #%d => undeclared variable %s" % (i + 1, var))
                        elif cnum > 0:  # Coefficient can't be recognized as a number
                            err = True
                            break
                        # Switched sides if needed (Only after last variable on LHS is recorded)
                        if switchside:
                            side = rhs
                            switchside = False
                        var, coeff = '', ''
                        varmode = False
                        # Record for the ext variable (if $, c will be reset anyway)
                        coeff += c

                    elif c.isalpha() or varmode:  # Variable recording mode (start with alpha, ends with +, -, or $)
                        if not varmode:
                            varmode = True
                        var += c

                    elif not varmode:  # Not alpha (or _ ), and not +, -, <, >, $, or = (so c is # or .)
                        coeff += c
                    cnum += 1

            if err:
                if i == numconst:
                    errors.append("Objective function => syntax error")
                else:
                    errors.append("Constraint #%d => syntax error" % (i + 1))
            i += 1

    # --- START SIMPLEX ---
    start_algorithm = time.time()
    optimum = False
    unbounded = False
    step = 1
    if not errors:
        while not optimum and not unbounded:
            # Check if optimum
            if any((True for x in sim[-1] if x < 0)):  # If there is any negative values on P row
                # Show tableau before doing simplex
                show_tab(sim, vartab, basic, step, precision)
                step += 1

                # Simplex
                enter = sim[-1].index(min(sim[-1]))
                m = 0
                maxratio = 0

                # Assume unbounded until a positive value in the entering column is found
                unbounded = True
                # Check ratios (and if unbounded)
                while m < numconst:
                    if sim[m][enter] > 0:
                        ratio = sim[m][enter] / sim[m][-1]
                        unbounded = False
                    else:
                        ratio = 0
                    if maxratio < ratio:
                        maxratio = ratio
                        leave = m
                    m += 1

                if not unbounded:

                    # leaving row: divide pivot row by pivot
                    pivot = sim[leave][enter]
                    sim[leave] = [val / pivot for val in sim[leave]]

                    # Do row operations (except for leaving row)
                    m = 0
                    for row in sim:
                        if m != leave:
                            row_coeff = sim[m][enter]
                            n = 0
                            while n < len(row):
                                sim[m][n] -= row_coeff * sim[leave][n]
                                n += 1
                        m += 1

                print("Entering variable: %s" % vartab[enter])
                print("Leaving variable: %s\n" % basic[leave])
                basic[leave] = vartab[enter]  # Update basic variables
            else:
                if not unbounded:
                    optimum = True
    if optimum:
        print("---- Optimum Solution ----")
        show_tab(sim, vartab, basic, step, precision)

    end_algorithm = time.time()

    # --- PRINT REPORT ---
    if not errors:
        print("--- Final Results ---")
        print("Number of decision variables: %s" % numvar)
        print("Number of constraints: %s" % numconst)
        print("Maximize:")
        print(make_pretty(objective))
        print("Subject to:")
        i = 1
        for const in constraints:
            print("#%d: %s" % (i, make_pretty(const)))
            i += 1
        print("Objective value = %d" % sim[-1][-1])
        corner = []
        for var in vartab[:-2]:
            if var in basic:
                val = float(sim[basic.index(var)][-1])
                if val.is_integer():
                    val = int(val)
                else:
                    val = round(val, precision)
                corner.append(str(val))
            else:
                corner.append("0")
        print("Final Corner")
        print("(%s):" % ", ".join(vartab[:numvar]))
        print("(%s)" % ", ".join(corner[:numvar]))
        print("Slacks")
        print("(%s)" % ", ".join(vartab[numvar:numvar + numconst]))
        print("(%s)" % ", ".join(corner[numvar:numvar + numconst]))
        print("Number of pivots: %d" % (step - 1))
        print("Simplex time = %f ms" % (1000 * (end_algorithm - start_algorithm)))
        print("Program execution time = %f ms" % (1000 * (time.time() - start_time)))
    else:
        print("Errors:")
        for err in errors:
            print(err)
        print("Program execution time = %f ms" % (1000 * (time.time() - start_time)))


# DRAFT
