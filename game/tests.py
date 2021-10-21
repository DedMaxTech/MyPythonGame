# def del_count(a):
#     return len([d for d in range(2,a) if a%d ==0])

# a,b,n = int(input()),int(input()),int(input())
# print([i for i in range(a,b) if del_count(i)>n])


import math
def power(k):
    return math.log(k,5)%1==0

print(power(25))