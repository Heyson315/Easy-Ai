# Write a function that takes a list of numbers and returns the average
def calculate_average(numbers):
	if not numbers:
		return 0
	return sum(numbers) / len(numbers)
