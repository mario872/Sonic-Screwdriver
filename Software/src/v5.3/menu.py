class Menu:
    def __init__(self, input_menu=None):
        if input_menu is not None:
            self.menu = input_menu
        else:
            self.menu = {}
        
        self.previous_menus = []
        
        self.current_index = 0
        self.current_menu = self.menu

    def forward(self, num_items=1):
        if len(self.current_menu['items']) == 1:
            self.current_index = 0
        elif self.current_index + num_items > len(self.current_menu['items'])-1:
            self.current_index = 0
        else:
            self.current_index += num_items
            

    def backward(self, num_items=1):
        if len(self.current_menu['items']) == 1:
            self.current_index = 0
        elif self.current_index - num_items < 0:
            self.current_index = len(self.current_menu['items'])-1
        else:
            self.current_index -= num_items

    def inward(self):
        try:
            self.current_menu['items'][self.current_index]['function']()
        except KeyError:
            pass
        
        if 'items' in list(self.current_menu['items'][self.current_index].keys()):
            self.previous_menus.append(self.current_menu)
            self.current_menu = self.current_menu['items'][self.current_index]
            self.current_index = 0

    def outward(self):
        try:
            self.current_menu = self.previous_menus[-1]
            self.previous_menus.pop()
            self.current_index = 0
        except IndexError:
            pass

    def select(self):
        try:
            pass # Run function
        except:
            pass # No function provided, run inwards function
        
    def get_current_menu(self):
        return self.current_menu

    def get_current_index(self):
        return self.current_index
    
    def is_current_item(self, item):
        if self.current_menu['items'][self.current_index] == item:
            return True
        else:
            return False
"""
menu = Menu(
    {'title': 'Menu', 'items': [
        {'title': 'item1', 'items': [
            {'title': 'item1-1', 'items': [{'title': 'item1-1-1', 'function': lambda: print("Stupid")}]},
            {'title': 'item1-2', 'items': [{'title': 'item1-1-2', 'items': None}]},
            {'title': 'item1-3', 'items': None}
        ]},
        {'title': 'item2', 'items': [
            {'title': 'item2-1', 'items': None},
            {'title': 'item2-2', 'items': None},
            {'title': 'item2-3', 'items': None}
        ]},
        {'title': 'item3', 'items': [
            {'title': 'item3-1', 'items': None},
            {'title': 'item3-2', 'items': None},
            {'title': 'item3-3', 'items': None}
        ]}
    ]}
    )
 """       

#while True:
#    print('------------------------')
#    for item in menu.get_current_menu():
#        if menu.is_current_item(item):
#            print(colored('  * ' + item['title'], "yellow"))
#        else:
#            print('  * ' + item['title'])
#    print('------------------------') 
        
#    action = input('Next Action (Up, Down, In, Out, Add, Remove): ')
#    if action == 'Up':
#        menu.backward()
#    elif action == 'Down':
#        menu.forward()
#    elif action == 'In':
#        menu.inward()
#    elif action == 'Out':
#        menu.outward()
#    elif action == 'Add':
#        menu.menu['items'][0]['items'].append({'title': 'NEW ITEM'})
#    elif action == 'Remove':
#        menu.menu['items'][0]['items'].pop()
