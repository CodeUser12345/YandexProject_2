import os
import shutil
import importlib


class ListClasses:
    def __init__(self):
        self.paths_classes = []
        self.indexes_classes = []
        self.flag_edit = False

        self._set_start_data()

        import list_classes
        global list_classes

    def add_class(self, path, index):
        self.paths_classes.append(path)
        self.indexes_classes.append(index)
        self.flag_edit = True

    def delete_class(self, inedx):
        if inedx in self.indexes_classes:
            index = self.indexes_classes.index(inedx)
            self.paths_classes.pop(index)
            self.indexes_classes.pop(index)
            self.flag_edit = True

    def get_object_class(self, index):
        self._edit_list_classes()
        return list_classes.create_object_class(index)

    def _edit_list_classes(self):
        if self.flag_edit:
            self.flag_edit = False

            files = os.listdir("dir_classes")
            names = [os.path.basename(n) for n in self.paths_classes]
            names_cod = ["dir_classes." + n if n.rfind(".") == -1
                         else "dir_classes." + n[:n.rfind(".")] for n in names]

            string = "import importlib\n\n"
            for n in names_cod:
                string += "import " + n + "\n"
            string += "\n"
            for n in names_cod:
                string += "importlib.reload(" + n + ")\n"
            string += "\n\ndef create_object_class(index):\n"
            if len(names_cod) == 0:
                string += "    return None"
            else:
                string += "    if index == " + str(self.indexes_classes[0]) + ":\n"
                string += "        return " + names_cod[0] + ".Object()\n"
                for n in range(1, len(names_cod)):
                    string += "    elif index == " + str(self.indexes_classes[n]) + ":\n"
                    string += "        return " + names_cod[n] + ".Object()\n"
                string += "    else:\n"
                string += "        return None\n"

            if os.path.exists("list_classes.py"):
                os.remove("list_classes.py")
            with open("list_classes.py", "w", encoding="utf-8") as file:
                file.write(string)

            for n in range(len(self.paths_classes)):
                flag = True
                for s in files:
                    if names[n] == s:
                        flag = False
                        break
                if flag:
                    path_1 = self.paths_classes[n]
                    index = names[n].rfind(".")
                    path_2 = names[n] if index == -1 else names[n][:index]
                    path_2 = "dir_classes\\" + path_2 + ".py"
                    with open(path_1, "r", encoding="utf-8") as file_read, \
                            open(path_2, "w", encoding="utf-8") as file_write:
                        file_write.write(file_read.read())

            for n in files:
                if n not in names and n != "__init__.py" and n[-3:] == ".py":
                    os.remove("dir_classes\\" + n)

            importlib.reload(list_classes)

    def _set_start_data(self):
        if os.path.exists("list_classes.py"):
            os.remove("list_classes.py")
        with open("list_classes.py", "w", encoding="utf-8") as file:
            file.write("import importlib\n\n\ndef create_object_class(index):\n    return None\n")
        if os.path.exists("dir_classes"):
            shutil.rmtree("dir_classes")
        os.makedirs("dir_classes")
        with open("dir_classes\\__init__.py", "w", encoding="utf-8") as file:
            file.write("")
