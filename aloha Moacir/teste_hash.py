import hashlib
from aloha.member_node import MemberNode
from aloha.stack import Stack

class TesteHash():
    """ numero = str(3 + 10)
    teste = hashlib.sha256(numero.encode()) """
    """ hash_dig = teste.hexdigest()
    print((int(hash_dig, 16))%101) """
    """ print(str(int(teste.hexdigest(), 16)%1001)) """
    list_test = [6, 2, 3, 5, 1, 4, 0, 0, 0]
    for i in range(len(list_test)):
        if list_test[i] > 0:    
            if list_test[i] == 0:
                list_test[i] += 1
            print(i)
        elif i == len(list_test) - 1:
            list_test = [6, 2, 3, 5, 1, 4, 0, 0, 0, None]
            list_test[i + 1] = 100
            print(list_test[i+1])
    
#node = MemberNode(None, 1, 1, 1)
#node.generate(1)

#print(int(hashlib.sha256(str(int(node.buffer[0]) + 1).encode()).hexdigest(), 16)%1001)

""" list_test = [6, 2, 3, 5, 1, 4]

ord_list = sorted(list_test)
print(str(ord_list))
ord_list.pop()
print(str(ord_list)) """

""" stack = Stack()

for i in ord_list:
    stack.push(i)

stack.pop()

print(stack.get_head()) """