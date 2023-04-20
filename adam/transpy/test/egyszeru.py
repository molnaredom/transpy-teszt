def something():
    print("jee")
def something_else():
    print("jeeeee")

def teszt(obj, Class, a, b):
    if isinstance(obj, Class) and a:
        if b:
            return obj.copy()
        return obj

if __name__ == '__main__':
    print(type)
    teszt(1, int, int, int)
