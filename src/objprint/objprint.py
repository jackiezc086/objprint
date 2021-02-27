# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/gaogaotiantian/objprint/blob/master/NOTICE.txt


class ObjPrint:
    def __init__(self):
        self._configs = {
            "indent": 2,
            "depth": 3,
            "width": 80
        }

        self.indicator_map = {
            list: "[]",
            tuple: "()",
            dict: "{}",
            set: "{}"
        }

        self.config(**self._configs)

    def objprint(self, obj, **kwargs):
        if kwargs:
            cfg = self._save_config()
            self.config(**kwargs)
            print(self.objstr(obj))
            self._load_config(cfg)
        else:
            print(self.objstr(obj))

    def objstr(self, obj, indent_level=0):
        # If it's builtin type, return it directly
        if isinstance(obj, str):
            return f"'{obj}'"
        elif isinstance(obj, int) or \
                isinstance(obj, float):
            return str(obj)

        # Otherwise we may need to unpack it. Figure out if we should do that first
        if indent_level >= self.depth:
            return self._get_ellipsis(obj)

        if isinstance(obj, list) or isinstance(obj, tuple) or isinstance(obj, set):
            elems = [f"{self.objstr(val, indent_level + 1)}" for val in obj]
        elif isinstance(obj, dict):
            elems = [f"{self.objstr(key, indent_level + 1)}: {self.objstr(val, indent_level + 1)}" for key, val in obj.items()]
        else:
            elems = [f".{key} = {self.objstr(val, indent_level + 1)}" for key, val in obj.__dict__.items()]
        return self._get_pack_str(elems, type(obj), indent_level)

    def config(self, **kwargs):
        for key, val in kwargs.items():
            if key in self._configs:
                self._configs[key] = val
            else:
                raise TypeError(f"{key} is not configurable")

        self._load_config(self._configs)

    def _save_config(self):
        return {key: val for key, val in self._configs.items()}

    def _load_config(self, config):
        for key, val in config.items():
            setattr(self, key, val)

    def add_indent(self, line, indent_level):
        if isinstance(line, str):
            return " " * (indent_level * self.indent) + line
        return [" " * (indent_level * self.indent) + ll for ll in line]

    def _get_header_footer(self, obj_type):
        if obj_type in self.indicator_map:
            indicator = self.indicator_map[obj_type]
            return indicator[0], indicator[1]
        else:
            return f"<{obj_type.__name__}", ">"

    def _get_ellipsis(self, obj):
        header, footer = self._get_header_footer(type(obj))
        return f"{header} ... {footer}"

    def _get_pack_str(self, elems, obj_type, indent_level):
        """
        :param elems list: list of string elements to pack together
        :param obj_type type: object type
        :param indent_level int: current indent level
        """
        header, footer = self._get_header_footer(obj_type)

        multiline = False
        if len(header) > 1:
            # If it's not built in, always do multiline
            multiline = True
        elif any(("\n" in elem for elem in elems)):
            # Has \n, need multiple mode
            multiline = True
        elif sum((len(elem) for elem in elems)) > self.width:
            multiline = True

        if multiline:
            s = ",\n".join(self.add_indent(elems, indent_level + 1))
            return f"{header}\n{s}\n{self.add_indent('', indent_level)}{footer}"
        else:
            s = ", ".join(elems)
            return f"{header}{s}{footer}"
