def determine_max_bid(value):
	value = float(value)
	a = -2.94 * 10**-7
	b = 0.0003
	c = 0.044
	d = 1.274

	# Produce a max bid value based on cubic regression formula
	answer = a*value**3 + b*value**2 + c*value + d
	roundedAnswer = '{0:.2f}'.format(answer)
	return roundedAnswer