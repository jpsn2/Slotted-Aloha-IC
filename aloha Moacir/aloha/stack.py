class Stack():
    
    def __init__(self):
        self.stack_list = []
        
    def push(self, item):
        self.stack_list.append(item)
        
    def pop(self):
        return self.stack_list.pop()
    
    def get_head(self):
        return self.stack_list[len(self.stack_list) - 1]
    
    def is_empty(self):
        return len(self.stack_list) == 0
    
    def clear(self):
        self.stack_list = []
        
    def sorted_stack(self):
        self.stack_list = sorted(self.stack_list)
        
    def contains(self, item):
        return item in self.stack_list
    
    def length(self):
        return len(self.stack_list)
    
    def __str__(self):
        return str(self.stack_list)