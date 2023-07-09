# WISHLIST:
# (1) coloured output

import numpy as np
import scipy.linalg as la
import numpy.linalg as nla

from copy import deepcopy
from typing import Optional

Matrix: type = np.array
Vector: type = np.array
MagicSquareValues: type = list[list[int | str]]

class NoSolutionException(Exception):
	pass

class NoIntegerSolutionException(Exception):
	pass

class NegativeSolutionException(Exception):
	pass

class ZeroSolutionException(Exception):
	pass

class MultipleSolutionException(Exception):
	pass

class DuplicateEntryException(Exception):
	pass

def int_precise(num: float) -> int:
	return int(num + (0.1 if num > 0 else -0.1)) # 0.1 is to correct rounding errors in computer representation

def exception_case(message: str, exception_type: type):
	if input(f"\n{message}\nWould you like to continue anyway? Enter \"yes\" or \"no\": ") != "yes":
		print("\nThe program will now terminate.\n")
		raise exception_type
		
def welcome_and_input_data() -> tuple[MagicSquareValues, Optional[int], int]:

	print("\nWelcome to the Magic Square Solver!\n\n" +
				"Please enter your incomplete magic square, with spaces separating entries in each row, " +
				"and with one row per line.\n" +
				"If an entry is not filled in, please enter \"?\" for that entry.\n\n" +
			  "Enter your magic square below:\n")

	curr_input: str = ""
	raw_inputs: list[list[str]] = []
	num_rows: Optional[int] = None
	curr_row_num: int = 1
	
	while num_rows is None or curr_row_num <= num_rows:
		
		curr_input = input()
		
		if curr_input != "done":

			curr_row: list[str] = curr_input.split(" ")
			raw_inputs.append(curr_row)
			curr_row_num += 1
			
			if num_rows is None:
				num_rows = len(curr_row)
			
	sum_raw: str = input("\nPlease enter the desired sum of each row, column, and diagonal.\n" + 
											 "If the sum is not given, please enter \"?\".\n\n" + 
											 "Enter the sum here: ")
	
	sum: Optional[int] = int(sum_raw) if sum_raw != "?" else None
	variable_counter: int = 0
	
	def next_var_label() -> str:
		nonlocal variable_counter
		return "x" + str(variable_counter := variable_counter + 1)
		
	return [[(int(entry) if entry != "?" else next_var_label()) for entry in row] \
					for row in raw_inputs], sum, variable_counter

def construct_matrix_A(ms_vals: MagicSquareValues, nv: int, sum_not_given: bool) -> Matrix:

	n: int = len(ms_vals)
	A: Matrix = np.zeros([2 * n + 2, nv])

	# setting up rows 1 to n
	for i in range(0, n):
		for var in range(0, nv):
			if "x" + str(var + 1) in ms_vals[i]:
				A[i, var] = 1

	# setting up rows n+1 to 2n
	for i in range(n, 2 * n):
		for var in range(0, nv):
			if "x" + str(var + 1) in [row[i - n] for row in ms_vals]:
				A[i, var] = 1

	# setting up rows 2n+1 and 2n+2
	for var in range(0, nv):
		if "x" + str(var + 1) in [ms_vals[i][i] for i in range(n)]:
			A[2 * n, var] = 1
		if "x" + str(var + 1) in [ms_vals[i][n - i - 1] for i in range(n)]:
			A[2 * n + 1, var] = 1

	# adding a column of -1's if sum is not given
	if sum_not_given:
		A = np.column_stack([A, -1 * np.ones(2 * n + 2)])

	# check that A does not have a condition number of "infinity" (which would indicate multiple solutions)
	if nla.cond(A) > 10 ** 15:
		exception_case("This magic square has multiple solutions (i.e. the solution is not unique).",
									 MultipleSolutionException)
	
	return A

def construct_vector_b(ms_vals: MagicSquareValues, ks: Optional[int]) -> Vector:

	ks = ks if ks is not None else 0
	n: int = len(ms_vals)
	k_vec: Vector = ks * np.ones(2 * n + 2)
	e_vec: Vector = np.zeros(2 * n + 2)

	# 1st to n-th entries
	for i in range(0, n):
		e_vec[i] = sum(filter(lambda entry : type(entry) is int, ms_vals[i]))

	# (n+1)-th to (2n)-th entries
	for i in range(n, 2 * n):
		e_vec[i] = sum(filter(lambda entry : type(entry) is int, [row[i - n] for row in ms_vals]))

	# (2n+1)-th to (2n+2)-th entries
	e_vec[2 * n] = sum(filter(lambda entry : type(entry) is int, [ms_vals[i][i] for i in range(n)]))
	e_vec[2 * n + 1] = sum(filter(lambda entry : type(entry) is int, [ms_vals[i][n - i - 1] for i in range(n)]))

	return k_vec - e_vec

def solve_and_get_final_answer(ms_vals: MagicSquareValues, A: Matrix, b: Vector, sum_not_given: bool) \
-> tuple[MagicSquareValues, Optional[int]]:

	Q1: Matrix; R1: Matrix
	Q1, R1 = la.qr(A, mode = "economic")

	x: Vector = la.solve(R1, Q1.T @ b) # using QR instead of A transpose * A controls the condition number better

	# check that x is an exact solution to Ax = b (rather than the least squares approximation)
	if not np.allclose(A @ x, b):
		exception_case("This magic square does not have a solution.",
									 NoSolutionException)

	# check that x only contains integers
	if not np.allclose(x, np.array([int_precise(entry) for entry in x])):
		exception_case("This magic square does not have a solution that contains only integers.",
									 NoIntegerSolutionException)
		
	ms_solved: MagicSquareValues = deepcopy(ms_vals)
	curr_index: int = -1

	def next_x_value() -> int:
		nonlocal curr_index
		return int_precise(x[curr_index := curr_index + 1])

	ms_solved = [[(entry if type(entry) is int else next_x_value()) for entry in row] for row in ms_solved]
	ms_solved_np: Matrix = np.array(ms_solved)
	num_distinct: int = len({int_precise(entry) for entry in ms_solved_np.reshape(np.prod(ms_solved_np.shape))})

	# check that the magic square does not contain duplicate entries
	if num_distinct != len(ms_solved) ** 2:
		exception_case("The solution of this magic square contains duplicate entries.",
									 DuplicateEntryException)

	# check that the magic square does not contain negative entries
	if any([any([entry < 0 for entry in row]) for row in ms_solved]):
		exception_case("This magic square does not have a solution that avoids negative entries.",
									 NegativeSolutionException)

	# check that the magic square does not contain 0 entries
	if any([any([entry == 0 for entry in row]) for row in ms_solved]):
		exception_case("This magic square does not have a solution that avoids 0 entries.",
									 ZeroSolutionException)
	
	sum_solved: Optional[int] = int_precise(x[-1]) if sum_not_given else None
	return ms_solved, sum_solved

def print_formatted(ms: MagicSquareValues, ks: Optional[int]):

	longest_entry_size: int = max([max([len(str(entry)) for entry in row]) for row in ms])
	padded: list[list[str]] = [[(longest_entry_size - len(str(entry))) * " " + str(entry) for entry in row] for row in ms]

	print("\nHere is the completely filled-in magic square:\n")

	for row in padded:
		for entry in row:
			print(3 * " " + entry, end = "")
		print()
	print()

	if ks is not None:
		print(f"The constant sum of this magic square is {ks}.\n")

def check_sum(ms: MagicSquareValues, s: int):

	SumInfo: type = tuple[str, int, int] # ex. ("row", 3, 40) means the sum of entries in row 3 is 40
	sums: list[SumInfo] = []
	n: int = len(ms)

	for row in range(n):
		sums.append(("row", row + 1, sum(ms[row])))

	for col in range(n):
		sums.append(("column", col + 1, sum([row[col] for row in ms])))

	sums.append(("diagonal", 1, sum([ms[i][i] for i in range(n)])))
	sums.append(("diagonal", 2, sum([ms[i][n - i - 1] for i in range(n)])))

	check_failed: bool = False
	for sum_info in sums:
		if sum_info[2] != s:
			check_failed = True
			print(f"!!! CHECK FAILURE: The sum of the entries in {sum_info[0]} {sum_info[1]} " +
						f"is {sum_info[2]} (not {s} as expected).")

	if check_failed:
		print()

# --------------------------------

def main():

	try:

		magic_square_values: MagicSquareValues; const_sum: Optional[int]; num_vars: int
		magic_square_values, const_sum, num_vars = welcome_and_input_data()
		
		A: Matrix = construct_matrix_A(magic_square_values, num_vars, const_sum is None)
		b: Vector = construct_vector_b(magic_square_values, const_sum)
		
		magic_square_solved: MagicSquareValues; sum_solved: Optional[int]
		magic_square_solved, sum_solved = solve_and_get_final_answer(magic_square_values, A, b, const_sum is None)

		print_formatted(magic_square_solved, sum_solved)
		check_sum(magic_square_solved, const_sum if const_sum is not None else sum_solved)

	except (NoSolutionException, NoIntegerSolutionException, NegativeSolutionException,
					ZeroSolutionException, MultipleSolutionException, DuplicateEntryException):
		
		pass # in the future maybe something more sophisticated can be done in these situations

main()