# -*- coding: utf-8 -*-
def strip(in_str):
    return in_str.replace('\n', '').replace('\t', '').replace(' ', '')


def children_as_text(node):
    text = []
    for sub_node in node[0].iterchildren():
        stripped_text = strip(sub_node.text)
        if stripped_text == '':
            continue
        else:
            text.append(sub_node.text)

    return text


def print_error(rec):
    pass
