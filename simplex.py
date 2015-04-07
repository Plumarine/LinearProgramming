# Simplex algorithm pivoting tool by Abdulla Almansoori 2015 (C)

import time
import re


def simplex(variables, objective, *constraints, **options):
    """
    This function shows each step of the simplex algorithm in tableau form,
    and then shows the final results of the optimum solution.

    INPUT: First you should only use strings as your input. Second, please make sure you follow the correct syntax when
        inputting the expressions. A correct syntax is as following:
        1) All variables should be declared in the first input as a string. They should be separated by spaces only.
        2) Variables can be alphanumeric with underscores, BUT should start with a letter.
        3) The constraints should include either <= or >= (not <, >, or =).
        4) You can use * to multiply a number with a variable, but not two numbers together (5*x ok, 5*5 no)
        5) You can use decimal numbers however you want (1.5, 1., .5 will all work)
        6) Of course, no floating or multiple symbols allowed (it's common sense, no **, +-, --, +.-, -*, 5+, x+y*, etc)
        7) You can use spaces however you want.

        For the options, you can choose the following:
            1) maximize: if true, maximize, if false, minimize. (Note -1 is considered true so it means maximize)
            2) precision: any integer between 0 and 6. Otherwise, it will be converted to integer, or defaulted to 3
            LATER... 3) dual: do the simplex for the dual

    PROCESS: The whole process of the simplex will be shown in multiple tableau, and steps taken are explained.

    OUTPUT: None

    EXAMPLES: Here are some examples to see how the function works:
        1) simplex('x y', 'x + y', '2x + y <= 4', 'x + 2y <= 4')
        2) simplex("x y z xyz", "x + y - z", "2x + y - xyz <= 4", "x + 2y +10*z <= 4", "5>= .7 y - xyz")
        3) simplex("x1 x2", '4x1+3x2', "2x1+3x2<=6", "-3x1+2x2<=3", "2x2<=5", "2x1+x2<=4")
        4) simplex("xxxxxx x22", "3xxxxxx+5x22", "xxxxxx<=4", "2x22<=12", "3*xxxxxx+2x22<=18")
        5) simplex("x1 x2", '2x1+x2', "-x1+x2<=-1", "-x1-2x2<=-2", "x2<=1", maximize = 0, precision = 2)
        6)...

    PARAMETERS:
    :param variables: You have to declare all your variables here
    :param objective: The objective function that you want to maximize/minimize
    :param constraints: Write as many constraints as you want here, each as a string as a separate input
    :param options: You can edit some optional parameters in the function, like max or min, the precision of output, etc
    :return: Nothing


    """
    """
    :param variables: You have to declare all your variables here
    :param objective: The objective function that you want to maximize/minimize
    :param constraints: Write as many constraints as you want here, each as a string as a separate input
    :param options: You can edit some optional parameters in the function, like max or min, the precision of output, etc
    :return: Nothing
    """

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

        print("Tableau #%d" % step)
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
                expr = expr[0:i] + " " + expr[i:]
                skip = True
            i += 1

        expr = expr.replace("<", " <")
        expr = expr.replace(">", " >")
        expr = expr.replace("+"," +")
        expr = expr.replace("-"," -")

        i = 0
        while i < len(expr):
            if expr[i] == " ":
                i += 1
            else:
                expr = expr[i:]
                i = len(expr)  # Break

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
    precision = options.get("precision", 3)
    if is_number(precision):
        if precision < 0 or precision > 6:
            precision = 3
        else:
            precision = int(precision)
    else:
        precision = 3
    optimmode = options.get("maximize", 1)
    if optimmode:
        optimmode = 1
    else:
        optimmode = -1
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
    i = 0
    while i < numconst + 1:
        exprlist[i] = exprlist[i].replace(' ', '')
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
                objc = -1 * optimmode  # the same if maximize, the opposite if minimize

            # Check symbols in input
            if i == numconst:
                if not re.match(objcheck, row):
                    errors.append("Objective function => unknown symbols used")
                    i += 1
                    continue
            else:
                if not re.match(constcheck, row):
                    errors.append("Constraint #%d => unknown symbols used" % (i + 1))
                    i += 1
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
                                sim[i][-1] += -1 * side * objc * float(coeff)
                            elif var in variables:  # Check if variable declared
                                x = variables.index(var)
                                sim[i][x] += side * objc * float(coeff)
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
    infeasible = False
    numpivots = 0
    step = 1

    '''
    # Transpose Negative (Dual)
    simdual = [[0 for x in range(1+numconst)] for x in range(2+numvar+numconst)]
    m = 0
    while m < len(sim):
        n = 0
        while n < len(sim[0]):
            simdual[n][m] = - sim[m][n]
            n += 1
        m += 1

    sim = simdual
    '''

    if not errors:
        while not optimum and not unbounded:
            # Check if infeasible origin
            if step == 1:
                if any((True for row in sim[:-1] if row[-1] < 0)):
                    infeasible = True
                    original_obj = sim[-1]
                else:
                    infeasible = False

            # Check if optimum
            if any((True for x in sim[-1][:-2] if x < 0)) or step == 1:  # Check if optimum, or origin
                show_tab(sim, vartab, basic, step, precision)
                step += 1

                maxratio = 0
                # Simplex
                # If origin infeasible, do this once (after showing first tableau)
                if infeasible and step == 2:
                    print("Infeasible origin")
                    print("Add artificial variable x!")
                    print("Sub-problem objective: minimize x!\n")
                    vartab = ['x!'] + vartab
                    i = 0
                    while i < len(sim) - 1:
                        sim[i] = [-1] + sim[i]
                        if sim[i][-1] < maxratio:
                            maxratio = sim[i][-1]
                            leave = i
                        i += 1
                    sim[-1] = [1] + (numvar + numconst) * [0] + [1, 0]
                    enter = 0  # artificial variable is always entering

                    show_tab(sim, vartab, basic, step, precision)
                    step += 1

                    print("Entering variable: %s" % vartab[enter])
                    print("Leaving variable: %s\n" % basic[leave])
                    basic[leave] = vartab[enter]  # Update basic variables
                    numpivots += 1

                # Choose entering and leaving variables according to simplex algorithm
                else:
                    enter = sim[-1].index(min(sim[-1][:-2]))  # Max obj coeff (in sim, obj function is negative)
                    # Assume unbounded until a positive value in the entering column is found
                    unbounded = True
                    # Check ratios (and also check if unbounded)
                    m = 0
                    while m < len(sim) - 1:
                        if sim[m][enter] > 0:
                            if sim[m][-1] == 0:
                                ratio = 0
                            else:
                                ratio = sim[m][enter] / sim[m][-1]
                            if unbounded:
                                unbounded = False
                        else:
                            ratio = -1

                        if maxratio <= ratio:
                            maxratio = ratio
                            leave = m
                        m += 1

                # If everything was fine and problem is bounded, do the row and column operations
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

                    if not (infeasible and step == 3):  # Because we already showed the variables for this step
                        print("Entering variable: %s" % vartab[enter])
                        print("Leaving variable: %s\n" % basic[leave])
                        basic[leave] = vartab[enter]  # Update basic variables
                        numpivots += 1
            # Optimum
            else:
                if not unbounded:
                    if infeasible:
                        infeasible = False
                        print("---- SUB-OPTIMAL ----")  # optimal for artificial variable problem
                        show_tab(sim, vartab, basic, step, precision)
                        step += 1
                        print("Drop x!, return to original problem")
                        print("Write objective function in terms of nonbasic variables\n")

                        # Return to original problem (delete x! column, and put original obj back)
                        vartab = vartab[1:]
                        i = 0
                        while i < len(sim) - 1:
                            sim[i] = sim[i][1:]
                            i += 1
                        sim[-1] = original_obj
                        i = 0
                        while i < numvar:
                            if sim[-1][i]:  # if not zero
                                if vartab[i] in basic:  # and if was basic variable
                                    m = basic.index(vartab[i])
                                    pivot = sim[-1][i]
                                    n = 0
                                    while n < len(sim[-1]):
                                        sim[-1][n] -= pivot * sim[m][n]
                                        n += 1
                            i += 1


                    else:
                        optimum = True

    # Show last tableau
    if unbounded:
        print("---- UNBOUNDED ----")
        show_tab(sim, vartab, basic, step, precision)
    elif optimum:
        print("---- OPTIMAL ----")
        show_tab(sim, vartab, basic, step, precision)

    end_algorithm = time.time()

    # --- PRINT RESULTS ---
    if not errors:
        print("--- Final Results ---")
        print("Number of decision variables: %s" % numvar)
        print("Number of constraints: %s" % numconst)
        print("Maximize:")
        print(" %s" % make_pretty(objective))
        print("Subject to:")
        for const in constraints:
            print(" %s" % make_pretty(const))
        print("Objective value = %d" % (optimmode * sim[-1][-1]))
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
        print("Final Corner (%s):" % ", ".join(vartab[:numvar]))
        print("(%s)" % ", ".join(corner[:numvar]))
        print("Slacks (%s):" % ", ".join(vartab[numvar:numvar + numconst]))
        print("(%s)" % ", ".join(corner[numvar:numvar + numconst]))
        print("Number of pivots: %d" % (numpivots))
        print("Simplex execution time = %f ms" % (1000 * (end_algorithm - start_algorithm)))
        print("Function execution time = %f ms" % (1000 * (time.time() - start_time)))
    else:
        print("Errors:")
        for err in errors:
            print(err)
        print("Function execution time = %f ms" % (1000 * (time.time() - start_time)))

# DRAFT
