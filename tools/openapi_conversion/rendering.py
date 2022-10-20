import keyword
from typing import List

from data_types import DataType, ObjectField, is_primitive_python_type


def docstring_comment(lines: List[str]) -> List[str]:
    if len(lines) == 0:
        return []
    if len(lines) == 1:
        return [f'"""{lines[0]}"""']
    result = ['"""' + lines[0]]
    result += lines[1:]
    result += ['"""']
    return result


def indent(lines: List[str], level: int) -> List[str]:
    """Indent each line.

    :param lines: Lines of text to be indented
    :param level: Level of indent (each indent level is four spaces)
    :return: Same lines of text provided after each line is indented
    """
    if level == 0:
        return lines
    else:
        return ['    ' * level + line if line else '' for line in lines]


def data_type(d_type: DataType) -> List[str]:
    """Generate Python code defining the provided data type.

    :param d_type: Parsed API data type to render into Python code
    :return: Lines of Python code defining the provided data type
    """
    docstring_lines = docstring_comment(
        d_type.description.split('\n')) if d_type.description else []
    lines = []

    if d_type.enum_values:
        if any(str(v) in keyword.kwlist for v in d_type.enum_values):
            lines.append(f'{d_type.name} = {d_type.python_type}')
            docstring_lines = d_type.description.split(
                '\n') if d_type.description else []
            docstring_lines += ['', 'Acceptable values:'] + ['* ' + str(v) for v
                                                             in
                                                             d_type.enum_values]
            lines.extend(docstring_comment(docstring_lines))
        else:
            lines.append(f'class {d_type.name}({d_type.python_type}, Enum):')
            lines.extend(indent(docstring_lines, 1))
            if docstring_lines:
                lines.append('')

            lines.extend(
                indent([f'{v} = "{v}"' for v in d_type.enum_values], 1))
    elif is_primitive_python_type(d_type.python_type):
        lines.append(f'{d_type.name} = {d_type.python_type}')
        lines.extend(docstring_lines)
    elif d_type.python_type == 'ImplicitDict':
        if any(f.api_name in keyword.kwlist for f in d_type.fields):
            lines.append(f'{d_type.name} = dict')
            if d_type.description:
                docstring_lines = d_type.description.split('\n')
                docstring_lines.append('')
            else:
                docstring_lines = []
            docstring_lines.append('Expected keys:')
            docstring_lines.extend('* ' + f.api_name for f in d_type.fields)
            lines.extend(docstring_comment(docstring_lines))
            lines.append('')
        else:
            lines.append(f'class {d_type.name}(ImplicitDict):')
            lines.extend(indent(docstring_lines, 1))
            if docstring_lines:
                lines.append('')

            for field in d_type.fields:
                lines.extend(indent(_object_field(field), 1))
                lines.append('')
            if d_type.fields:
                lines.pop()
    else:
        lines.append(f'{d_type.name} = {d_type.python_type}')

    return lines


def _object_field(field: ObjectField) -> List[str]:
    """Generate an unindented definition of the provided field in Python code.

    :param field: Data type field to render into Python code
    :return: Lines of Python code defining the provided field
    """
    d_type = field.python_type if field.required else f'Optional[{field.python_type}]'
    if field.default is not None:
        if field.literal_default:
            default_suffix = f' = {field.default}'
        elif isinstance(field.default, str):
            default_suffix = f' = "{field.default}"'
        else:
            default_suffix = f' = {str(field.default)}'
    else:
        default_suffix = ''
    lines = [f'{field.api_name}: {d_type}{default_suffix}']
    if field.description:
        lines.extend(docstring_comment(field.description.split('\n')))
    return lines


def data_types(d_types: List[DataType]) -> List[str]:
    already_defined = [kw for kw in keyword.kwlist]
    already_defined += ['int', 'float', 'complex', 'str', 'list', 'tuple',
                        'range', 'bytes', 'bytearray', 'memoryview', 'dict',
                        'bool', 'set', 'frozenset']

    lines = ['# This file is autogenerated; do not modify manually!', '']
    lines.extend(['from __future__ import annotations', ''])

    if any(d.enum_values for d in d_types):
        lines.append('from enum import Enum')

    basic_types = []
    if any(d.python_type.startswith('List[') for d in d_types) or any(
            any(f.python_type.startswith('List[') for f in d.fields) for d in
            d_types):
        basic_types.append('List')
    if any(any(not f.required for f in d.fields) for d in d_types):
        basic_types.append('Optional')
    lines.append('from typing import ' + ', '.join(basic_types))
    lines.append('')

    lines.append('from implicitdict import ImplicitDict')
    if any(('StringBasedDateTime' in d.python_type) for d in d_types) or any(
            any(('StringBasedDateTime' in f.python_type) for f in d.fields) for
            d in d_types):
        lines[-1] = lines[-1] + ', StringBasedDateTime'
        already_defined.append('StringBasedDateTime')
    already_defined.append('ImplicitDict')

    # Declare types in dependency order
    total_defined = 0
    n_defined = 1

    def _core_type(type_name):
        core_type = type_name
        while '[' in core_type:
            core_type = core_type[core_type.index('[') + 1:]
        while ']' in core_type:
            core_type = core_type[0:core_type.index(']')]
        return core_type

    while n_defined > 0:
        n_defined = 0
        for d_type in d_types:
            if d_type.name in already_defined:
                continue
            if _core_type(d_type.python_type) not in already_defined:
                continue
            if any((_core_type(f.python_type) not in already_defined) for f in
                   d_type.fields):
                continue

            lines.extend(['', ''])
            lines.extend(data_type(d_type))
            already_defined.append(d_type.name)
            n_defined += 1
            total_defined += 1
    not_defined = [d_type for d_type in d_types if
                   d_type.name not in already_defined]
    if not_defined:
        not_defined_list = ', '.join(d_type.name for d_type in not_defined)
        raise RuntimeError(f'Failed to define data types: {not_defined_list}')

    lines.append('')
    return lines