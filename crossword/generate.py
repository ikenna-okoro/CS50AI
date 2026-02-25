import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # for each variable in domains:
        for v in self.domains:
            # for each word in variable's domain:
            for x in list(self.domains[v]):
                # if len word not same as len variable: remove word from variable's domain
                if len(x) != v.length:
                    self.domains[v].remove(x)
        # return
        return

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revise = False
        if self.crossword.overlaps[x, y] is None:
            return revise
        a = self.crossword.overlaps[x, y][0]
        b = self.crossword.overlaps[x, y][1]
        for word_x in list(self.domains[x]):
            count = 0
            for word_y in list(self.domains[y]):
                if word_x[a] == word_y[b]:
                    count += 1
            if count < 1:
                self.domains[x].remove(word_x)
                revise = True
        return revise
    
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            queue = [arc for arc in self.crossword.overlaps]
            while len(queue) != 0:
                (x, y) = queue[0]
                queue = queue[1:]
                if self.revise(x, y):
                    if len(self.domains[x]) == 0:
                        return False
                    for z in self.crossword.neighbors(x):
                        if z != y:
                            queue.append((z, x))
            return True
        else:
            queue = arcs
            while len(queue) != 0:
                (x, y) = queue[0]
                queue = queue[1:]
                if self.revise(x, y):
                    if len(self.domains[x]) == 0:
                        return False
                    for z in self.crossword.neighbors(x):
                        if z != y:
                            queue.append((z, x))
            return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.domains):
            return True
        return False
        # complete = False
        # size = len(assignment)
        # count = 0
        # for var, val in assignment.items():
        #     if len(var) == len(val):
        #         count += 1
        # if count == size:
        #     complete = True
        # return complete

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check unary constraints
        # self.enforce_node_consistency()
        for var, val in assignment.items():
            if var.length != len(val):
                return False
                
        # Check binary constraints
        # if not self.ac3():
        #     return False
        for (v1, v2), overlap in self.crossword.overlaps.items():
            if overlap is not None:
                a, b = overlap
                if v1 in assignment and v2 in assignment:
                    if assignment[v1][a] != assignment[v2][b]:
                        return False
        # Check no duplicates
        seen = set()
        words = assignment.values()
        for word in words:
            if word in seen:
                return False
            seen.add(word)
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        domain = []
        for value in list(self.domains[var]):
            if value not in assignment.values():
                domain.append(value)
        return domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [v for v in self.domains if v not in assignment]
        if not unassigned:
            return None
        # Select by MRV (minimum remaining values), then by degree
        unassigned.sort(key=lambda v: (len(self.domains[v]), -len(self.crossword.neighbors(v))))
        return unassigned[0]
            
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        if var is None:
            return None
        for val in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = val
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None
            

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
