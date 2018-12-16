#!/usr/bin/python3

def rearrange(*args, **kwargs):
    def get_function(func):
        def process(*args_func, **kwargs_func):
            new_args = [args_func[index] for index in args]
            for arg in args_func:
                if arg not in new_args:
                    new_args.append(arg)

            new_kwargs = {kwargs[key]:key for key in kwargs.keys()}
            for key in kwargs_func.keys():
                if key not in new_kwargs.keys():
                    new_kwargs[key] = kwargs_func[key]

            return func(*new_args, **new_kwargs)
    
        return process
        
    return get_function


@rearrange(1, 0, keyword="argument")
def example(first, second, argument="default"):
    print("first", first)
    print("second", second)
    print("argument", argument)
    return None

@rearrange(2,0, 1, minus="param")
def func(one, two, three, four, five, six, param="plus", get="get"):
    print(one, two, three, four, five, six)
    print(param)
    print(get)

if __name__ == '__main__':
    print("main")
    example('hi', 'paul', argument="new_value")

    func(1,2,3,4,5,six=7)

