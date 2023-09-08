import igraph as ig
import requests, json
import matplotlib.pyplot as plt

# this script plots reconstruction tree nicely
# use parameter "pids" to specify the sub-trees
# you need igraphy and matplotlib
# python3 -m venv my-venv
# source my-venv/bin/activate
# pip3 install matplotlib igraph

r = requests.get(
    "http://localhost:18000/rotation/get_reconstruction_tree_edges/?model=seton2012&level=4&pids=707,702,314,833",
    verify=False,
)
print(r.text)
edges = json.loads(r.text)

if len(edges) < 1:
    raise Exception("No edge found!!!")

# make the reconstruction edges good for igraph
v_dict = dict()
count = 0
names = []
fp = []
mp = []
for e in edges:
    if not str(e[0]) in v_dict:
        v_dict[str(e[0])] = count
        names.append(str(e[0]))
        fp.append(e[0])
        count += 1
    if not str(e[1]) in v_dict:
        v_dict[str(e[1])] = count
        names.append(str(e[1]))
        mp.append(e[1])
        count += 1
# print(count)
# print(v_dict)

# find the indexes of the roots of trees
roots = [i for i in fp if i not in mp]
root_idx = []
for r in roots:
    root_idx.append(names.index(str(r)))


i_edges = []
for e in edges:
    i_edges.append((v_dict[str(e[0])], v_dict[str(e[1])]))
n_vertices = len(v_dict)

g = ig.Graph(n_vertices, i_edges)

# Set attributes for the graph, nodes, and edges
g["title"] = "Reconstruction Tree"

fig, ax = plt.subplots(figsize=(40, 20))
lo = g.layout_reingold_tilford(mode="out", root=root_idx)
lo.rotate(180)
ig.plot(
    g,
    target=ax,
    layout=lo,
    # layout="circle",  # print nodes in a circular layout
    vertex_size=0.1,
    vertex_frame_width=1.0,
    vertex_frame_color="white",
    vertex_label=names,
    # vertex_label_size=7.0,
)

# plt.show()

fig.savefig("reconstruction-tree.png")
