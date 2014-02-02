import vmflib


## We make a number divisible by n by rounding up. For that, 
## we calculate how much we would have to add to the number for it to
## be divisible without leaving any remains beyond the decimal point.
def make_number_divisible_by_n(num, n):
    if num % n != 0:
        remaining = n - (num % n)
        return num + remaining
    else:
        return num

## A helper function which will be used with map()
## on a list of height values to create normals.
def map_list_with_vertex(height):
    return vmflib.types.Vertex(0,0, height)