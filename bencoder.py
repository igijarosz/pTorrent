def Bdecode(input_data):
    data = list(input_data)

    while len(data) > 0:

        element = data.pop(0)
        if element.isnumeric():
            length = ""
            while element.isnumeric():
                length += str(element)
                if len(data) > 0:
                    element = data.pop(0)
            string = ""
            for i in range(int(length)):
                if len(data) > 0:
                    string += data.pop(0)

            return string, data

        if element == "i":
            integer = ""
            element = data.pop(0)
            while element.isnumeric() or element == "-":
                integer += element
                element = data.pop(0)
            return integer, data

        if element == "l":
            lista = []
            element = data.pop(0)
            while element != "e":
                if len(data) == 0:
                    return lista, data
                data.insert(0, element)
                value, data = Bdecode(data)
                lista.append(value)
                element = data.pop(0)
            return lista, data

        if element == "d":
            dictionary = {}
            element = data.pop(0)
            while element != "e":
                if len(data) == 0:
                    return dictionary, data
                data.insert(0, element)
                key, data = Bdecode(data)
                value, data = Bdecode(data)
                dictionary[key] = value
                if len(data) > 0:
                    element = data.pop(0)
            return dictionary, data

