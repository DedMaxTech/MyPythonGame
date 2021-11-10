#1
# from random import randint as rd
# n,s=10,1
# x=rd(20,35)
# a = [rd(20,35) for i in range(n)]

# for i in range(len(a)-1):
#     if a[i]==x: 
#         print(s)
#         break
#     s*=a[i]

#2
# from random import randint as rd
# n=10
# a = [rd(10,40) for i in range(n)]

# def findmax(a):
#     max, ind=a[0],0
#     for i in range(len(a)-1):
#         if a[i]>max:
#             max = a[i]
#             ind = i
#     return ind

# a[findmax(a)], a[len(a)-1] = a[len(a)-1],a[findmax(a)]
# print(a)

# 3
# from random import randint as rd
# n=10
# a = [rd(1,100) for i in range(n)]
# ids=[]

# for i in range(0,len(a)-2):
#     if a[i+1]%a[i]==0: ids+=[i]

# print(ids, len(ids))

#4
# from random import randint as rd
# n,s=10,1
# x=rd(-10,10)
# a = [rd(-10,10) for i in range(n)]

# for i in range(0,len(a)-2):
#     if a[i+1]<0 and a[i]<0:
#         for b in range(len(a)-1,i+1,-1):
#             a[b]=a[b-1]
#         a[i+1]=x
#         break
# print(a)

# def is_palindrom(k):
#     b = []
#     while k > 0:
#         b.append(k % 10)
#         k = k // 10
#     for i in range(0,len(b)-1):
#         if b[i]!=b[len(b)-1-i]: return False
#     return True
# print(is_palindrom(12321))
e,i=float(input()),1
while 1/((i+1)**2)>e: 
    print(1/((i+1)**2))
    i+=1
print(i)
