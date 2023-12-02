import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from utils import parameter_helper
from utils.model_utils import get_rotation_model


def get_child_edges(edges, pid):
    """get edges which have the given fixed plate id.
    this is in fact just to get the direct child edges of a node(pid).
    i don't understand why i wrote so many lines comments for one line code
    i guess i want to show people that i am a good SE?
    anyway, don't do this!!

    :param edges: all edges in the reconstruction tree
    :param pid: fixed plate id

    :returns: the edges whose fixed plate id is the same with the given one
    """
    return [e for e in edges if e[0] == pid]


def get_roots(edges):
    """find all the roots from the list of edges

    :param edges: list[[number, number]]
    """
    parents = set([e[0] for e in edges])
    children = set([e[1] for e in edges])

    return [i for i in parents if i not in children]  # this guy has no parent


def build_json_trees(edges):
    """build json trees from edges

    {
    'pid':0,
    'children':[
        {'pid':1, children:[...]},
        {'pid':2, children:[...]},
        {'pid':3, children:[..]},
        ]
    }
    """

    def get_children(root, edges):
        children = []
        for edge in edges:
            if edge[0] == root:
                children.append(edge[1])

        ret = []
        for child in children:
            ret.append(
                {
                    "pid": child,
                    "children": get_children(child, edges),
                }
            )

        return ret

    trees = []
    roots = get_roots(edges)
    for root in roots:
        nodes = get_children(root, edges)
        trees.append({"pid": root, "children": nodes})

    print(trees)

    return trees


def get_reconstruction_tree(request):
    return get_reconstruction_tree_edges(request, return_json_trees=True)


def get_reconstruction_tree_edges(request, return_json_trees=False):
    """return edges in a reconstruction tree at a given time
    http://localhost:18000/rotation/get_reconstruction_tree_edges/?model=MERDITH2021&time=100&level=4&pids=452,447,712

    :param level: the numbre of tree levels to return. if 0 or not present, means all
    :param pids: the roots of the subtrees. if not present, return all
    :param maxpid: ignore all pids>maxpid

    :returns: a list of [fixed plate ID, moving plate ID]
    """

    time = parameter_helper.get_float(request.GET, "time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    level = parameter_helper.get_int(request.GET, "level", 0)
    pids = parameter_helper.get_int_list(request.GET, "pids")
    max_pid = parameter_helper.get_int(request.GET, "maxpid", None)

    rotation_model = get_rotation_model(model)
    tree = rotation_model.get_reconstruction_tree(time)
    edges = tree.get_edges()

    edge_list = list(
        set([(e.get_fixed_plate_id(), e.get_moving_plate_id()) for e in edges])
    )
    if max_pid is not None:
        edge_list = [ee for ee in edge_list if ee[0] < max_pid and ee[1] < max_pid]

    if level > 0 or len(pids) > 0:
        edges_buf = []

        if len(pids) == 0:
            pids = get_roots(edge_list)
        safe_guard = 0
        while True:
            new_pids = []
            for pid in pids:
                es = get_child_edges(edge_list, pid)
                edges_buf.extend(es)
                new_pids.extend([i[1] for i in es])
            pids = set(new_pids)
            if level > 0:
                level -= 1
                if level == 0:
                    break
            elif len(new_pids) == 0:
                break
            safe_guard += 1
            if safe_guard > 20:
                break
        edge_list = edges_buf

    if return_json_trees:
        response = HttpResponse(
            json.dumps(build_json_trees(edge_list)), content_type="application/json"
        )
    else:
        response = HttpResponse(json.dumps(edge_list), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_reconstruction_tree_height(request):
    """return the height of a reconstruction sub-tree
    http://localhost:18000/rotation/get_reconstruction_tree_height?pid=304

    :param pid: the root of the sub-tree, default 0

    :returns: a number which indicates the tree height
    """
    time = parameter_helper.get_float(request.GET, "time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    pid = parameter_helper.get_int(request.GET, "pid", 0)

    rotation_model = get_rotation_model(model)
    tree = rotation_model.get_reconstruction_tree(time)

    height = 1

    def traverse_sub_tree(edge, depth):
        nonlocal height
        if depth > height:
            height = depth

        for child_edge in edge.get_child_edges():
            traverse_sub_tree(child_edge, depth=depth + 1)

    if pid:
        traverse_sub_tree(tree.get_edge(pid), depth=1)
    else:
        for anchor_plate_edge in tree.get_anchor_plate_edges():
            # print(
            #    f">>>>{anchor_plate_edge.get_fixed_plate_id()}>>>{anchor_plate_edge.get_moving_plate_id()}"
            # )
            traverse_sub_tree(anchor_plate_edge, depth=2)

    response = HttpResponse(json.dumps(height), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_reconstruction_tree_leaves(request):
    """return all the leaves of the reconstruction tree
    http://localhost:18000/rotation/get_reconstruction_tree_leaves
    """
    time = parameter_helper.get_float(request.GET, "time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)

    rotation_model = get_rotation_model(model)
    tree = rotation_model.get_reconstruction_tree(time)

    leaves = []

    def traverse_sub_tree(edge):
        nonlocal leaves
        child_edges = edge.get_child_edges()
        if len(child_edges) == 0:
            leaves.append(edge.get_moving_plate_id())
        else:
            for child_edge in edge.get_child_edges():
                traverse_sub_tree(child_edge)

    for anchor_plate_edge in tree.get_anchor_plate_edges():
        traverse_sub_tree(anchor_plate_edge)

    response = HttpResponse(
        json.dumps(list(set(leaves))), content_type="application/json"
    )

    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_ancestors_in_reconstruction_tree(request):
    """return all ancestors PIDs for a given pid
    http://localhost:18000/rotation/get_ancestors_in_reconstruction_tree?pid=101
    """
    time = parameter_helper.get_float(request.GET, "time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    pid = parameter_helper.get_int(request.GET, "pid", None)

    if pid is None:
        return HttpResponseBadRequest(f"The parameter 'pid' is required!")

    rotation_model = get_rotation_model(model)
    tree = rotation_model.get_reconstruction_tree(time)
    edge = tree.get_edge(pid)
    ancestors = []
    while edge:
        ancestors.append(edge.get_fixed_plate_id())
        edge = edge.get_parent_edge()

    response = HttpResponse(json.dumps(ancestors), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response
