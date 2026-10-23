# Boundary for a later input-enclosure API

This private experiment adds no production API. If qualified, the smallest
follow-up is a separate explicit method on `AccuracyMasterEvaluator<T>` that
accepts component-wise physical-input rectangles alongside ordinary numeric
input and the existing accuracy/policy context. The ordinary represented-input
method remains unchanged. The series workspace can share its existing
instruction-major programs, using enclosed physical normalization and the
all-component tail majorant only when the extra input is supplied.

The numerical input still includes the ordinary scale argument and is validated
through the existing public adapter. The experimental series method receives
ten physical D0 arguments (six invariants and four squared masses) per Taylor
component; finite D0 is scale independent. A future public method must state
this mapping explicitly or accept full ordinary-arity enclosures and validate
scale consistently. It must not silently reinterpret sample lanes as Taylor
components.

Required contracts:

- Each rectangle is ordered, contains the exact represented nominal component,
  and covers the intended mathematical component by a documented caller proof.
- The whole physical rectangle satisfies the bounded analytic branch guards.
- The frozen auxiliary anchor is a represented primal mass, with zero auxiliary
  derivatives; varying physical mass components remain in the input rectangles.
- An accepted component includes physical-input uncertainty, normalization
  rounding, retained-series arithmetic and the complete component tail.
- Ordinary fallback remains explicitly uncertified. Required certification
  failure retains diagnostics and exposes no successful zero placeholder.
- Scope diagnostics distinguish represented-input certificates from certificates
  conditional on caller-supplied physical rectangles.

The contour probe supplies exact unshifted Cayley coefficients from an
independent oracle. It therefore covers the non-dyadic contour map, shift,
coefficient update, finite D0 evaluation, contraction and contour Jacobian at
one point. It does not cover errors in producing the unshifted geometry.

Before public E6 integration, separate work remains to enclose rounded geometry
solves/coefficients, actual quadrature nodes and weights, and both quadrature
rounding and the analytic integral tail. A sequence of quadrature estimates is
not by itself an integral certificate. Requested component budgets must survive
contraction and quadrature without reusing the former fixed low-bit acceptance
rule. Higher/mixed Dual interval families need accepted independent-oracle
checks in addition to the degree3 no-false-success rejection control here.
