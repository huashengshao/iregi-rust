import tirust

dot = """
digraph interop_bubble {
    graph [num="3 + 2*iregi::q0 + iregi::q1*iregi::q2", overall_factor="1"];
    edge [particle="phi"];
    ext [style=invis];
    ext -> a;
    a -> b [lmb_id=0];
    a -> b;
    b -> ext;
}
"""
diagram = tirust.FeynmanDiagram.from_dot(tirust.Model.phi3(), dot)
print(diagram._repr_svg_())
