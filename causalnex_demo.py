import warnings
from causalnex.structure import StructureModel

warnings.filterwarnings("ignore")  # silence warnings

sm = StructureModel()

sm.add_edges_from([
    ('export', 'supply'),
    ('import', 'supply'),
    ('production', 'supply'),
    ('supply', 'price'),
    ('demand', 'price'),
    ('history_price', 'price'),
    ('stock', 'price'),
    ('fproduct_price', 'price'),
    ('sproduct_price', 'demand'),
    ('fproduct_price', 'demand'),
    ('sproduct_demand', 'demand'),
    ('demand', 'sales'),
    ('price', 'income'),
    ('sales', 'income'),
    ('fproduct_price', 'cost'),
    ('income', 'profit'),
    ('cost', 'profit'),
    ('profit', 'company_profit'),
    ('company_profit', 'eps'),
    ('eps', 'pe'),
])

print(sm.edges)

from IPython.display import Image
from causalnex.plots import plot_structure, NODE_STYLE, EDGE_STYLE

viz = plot_structure(
    sm,
    graph_attributes={"scale": "0.5"},
    all_node_attributes=NODE_STYLE.WEAK,
    all_edge_attributes=EDGE_STYLE.WEAK,
)
Image(viz.draw(format='png'))