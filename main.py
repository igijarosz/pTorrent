text = "d4:dictd3:1234:test3:4565:thinge4:listl11:list-item-111:list-item-2e6:numberi123456e6:string5:valuee"


def Bdecode(input_data):
    data = list(input_data)

    while len(data) > 0:

        element = data.pop(0)
        if element.isnumeric():
            length = ""
            while element.isnumeric():
                length += str(element)
                element = data.pop(0)
            string = ""
            for i in range(int(length)):
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
                data.insert(0, element)
                value, data = Bdecode(data)
                lista.append(value)
                element = data.pop(0)
            return lista, data

        if element == "d":
            dictionary = {}
            element = data.pop(0)
            while element != "e":
                data.insert(0, element)
                key, data = Bdecode(data)
                value, data = Bdecode(data)
                dictionary[key] = value
                element = data.pop(0)
            return dictionary, data

print(Bdecode(text))
print("siema")