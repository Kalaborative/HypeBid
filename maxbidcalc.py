def determine_max_bid(value):
	a = -2.94 * 10**-7
	b = 0.0003
	c = 0.044
	d = 1.274

	# Produce a max bid value based on cubic regression formula
	answer = a*value**3 + b*value**2 + c*value + d
	return answer

try:
	sampleVal = float(input("Enter a value: "))
	sampleResponse = determine_max_bid(sampleVal)
	# Round to 2 decimal places
	print('{0:.2f}'.format(sampleResponse))
except ValueError:
	print("The value was not a valid number.")
