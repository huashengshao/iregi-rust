set pagination off
set confirm off
set breakpoint pending on
set print thread-events off
set print pretty on
set print elements 40
set print repeats 3
break /shared/external/iregi/iregi-rust/.local/cargo-home/git/checkouts/gammaloop-277a30c7f1437c23/865afdc/crates/linnest/src/label_placement.rs:1841
run
bt 5
source /nix/store/1qg7z7i461qsv0lczc40nyi8ps6snlca-rustc-1.99.0/lib/rustlib/etc/gdb_load_rust_pretty_printers.py
frame 1
info args
print *self
frame 2
info args
python
import gdb
try:
    arg = gdb.selected_frame().read_var("arg")
    gdb.write("RAW_CBOR_SLICE " + str(arg) + "\n")
    address = int(arg["data_ptr"])
    length = int(arg["length"])
    memory = gdb.selected_inferior().read_memory(address, length)
    with open("target/python-interface-build/render-captured.cbor", "wb") as stream:
        stream.write(bytes(memory))
    gdb.write("RAW_CBOR_BYTES " + str(length) + "\n")
except Exception as error:
    gdb.write("RAW_CBOR_UNAVAILABLE " + str(error) + "\n")
end
quit
