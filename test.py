def run():
    def add_to_list(item):
        my_list.append(item)

    my_list = []

    add_to_list(1)
    add_to_list(2)

    return my_list


print(run())
