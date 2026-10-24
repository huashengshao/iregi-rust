# Confirmed native SVG serialization failure

The unchanged installed wheel was stopped in the actual upstream decoder.
`render-gdb-pretty.log.gz` captures ordinary two-dimensional floating origins
and command coordinates encoded as `$serde_json::private::Number` marker maps.
This confirms feature-unified arbitrary-precision JSON is crossing a CBOR
geometry boundary through `serde_json::Value`. The graph geometry and packaged
font validation are valid.

The baseline 28/29 API tests remain unchanged. A typed native wire DTO repair
is proposed separately; this supplement claims diagnosis only, with no fix
compiled or executed. Original unsuccessful optimized-variable capture attempts
are retained alongside the successful parsed capture. No wheel/shared library
or provided license is included.
