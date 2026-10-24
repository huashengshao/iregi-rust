set pagination off
set confirm off
set breakpoint pending on
set print pretty on
set print elements 20
set print repeats 5
break /shared/external/iregi/iregi-rust/.local/cargo-home/git/checkouts/gammaloop-277a30c7f1437c23/865afdc/crates/linnest/src/label_placement.rs:1841
run
bt 12
info args
info locals
python
import gdb
for expression in ("coordinate", "*coordinate", "value", "*value", "arg"):
    try:
        gdb.write("CAPTURE_EXPRESSION " + expression + "\n")
        gdb.execute("print " + expression)
    except gdb.error as error:
        gdb.write("CAPTURE_UNAVAILABLE " + str(error) + "\n")
end
quit
