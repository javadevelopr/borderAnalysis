#Border Crossing Analysis

##Approach
Thanks to Python's "all batteries-included" standard library, this was a fairly straightforward challenge and my 
approach should be fairly readable from the code.

My core data structure iss a search Tree. Since Python does not come with a Tree structure out of the box (except 
dict objects which are basically trees of depth 2) I simulate one using nested dicts (defaultdict to be exact). 
Python does not allow you to nest dicts to an arbitrary depth so I created one using a known python hack:

```python
def Tree():
	return defaultdict(tree)

```	 
This allowed categorization of the data points as the were being read line by line like so:

```python
tree = Tree()
tree[border][date][measure] = value
```

With the data grouped by Border,Date and Measure (in that order ) it was then straightforward to sum for each group 
as required for the first part of this challenge (actually this was done on the fly as the input data was being parsed
line by line).
To calculate running Monthly averages for each border and means of crossing the results obtained from the
first step were sorted in descending order (as required). It was then straightforward to calculate a running monthly
average using the ff procedure:
- Read each row of results
- for each row, find all the other rows in the result set with the same border and measure by searching forward
  in the result set, since the result set is already sorted in descending order ( and using Python's nice
  filter() function)
- Sum up the rows obtained from step 2 and take the average
