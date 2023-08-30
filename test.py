from copy import deepcopy

class A:
    def __init__(self, a):
        self.a = a


list = [A(0)]
print("Before Copy: ", list[0].a)

newlist = deepcopy(list)
newlist[0].a = 1

print("After copy and modify: ", list[0].a)
print("The copy: ", newlist[0].a)

print(list[0])