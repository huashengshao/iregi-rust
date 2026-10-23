# Scalar-master qualification

`qualification.json` records the final frozen master source and exact test
binary/dependency hashes for 26 passing checks. The adjacent logs preserve
their complete output. Wall times are validation timings with serialized
Symbolica execution, not performance measurements.

Coverage includes batched A0/B0/DB0/C0/D0 reference parity, f64/DoubleFloat/Float
and static/dynamic Dual inputs, mixed component precision, lane isolation,
UV/IR metadata, B0 lightlike and massive pseudothreshold neighborhoods,
physical C0 and B0/DB0 mixed derivatives, genuine-threshold diagnostics,
constant-kinematic scale jets including infrared double poles, and extreme
independent kinematic/renormalization scales.

Physical D0 is qualified separately: the equal-complex case previously passed
first, second, and mixed derivative checks against high-precision finite
differences. The complete five-case mixed batch remains pending. These logs
do not claim that broader qualification.

The direct binaries preserve the dependency artifacts used during the checks;
later workspace-level dependency additions have separate central validation.
Historical failing probes and their subsequent fixes are tracked in
`crates/iregi-masters/tests/validation_evidence.json`.
