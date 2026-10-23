//! Private lowering experiment: no algebra or new numeric primitives.
use oneloop::rust_codegen::runtime::{C, Context, NativeFloat, primitives};

#[derive(Clone, Copy, Debug)]
pub(crate) enum BinaryOperand {
    Column(usize),
    Constant(usize),
}

#[inline(always)]
fn operation<T: NativeFloat, const MULTIPLY: bool, const INLINE: bool>(a: &C<T>, b: &C<T>) -> C<T> {
    if MULTIPLY {
        if INLINE { primitives::inline_mul(a, b) } else { primitives::mul(a, b) }
    } else if INLINE {
        primitives::inline_add(a, b)
    } else {
        primitives::add(a, b)
    }
}

/// One instruction across its active lanes. All operand reads finish before
/// the target is replaced, including either/both source aliases of the target.
/// The generator guarantees sorted unique lanes and a matching dense span.
/// This boundary intentionally prevents reinlining dispatch at every DAG node.
#[inline(never)]
pub(crate) fn shared_binary<T: NativeFloat, const MULTIPLY: bool, const INLINE: bool>(
    arena: &mut [C<T>],
    stride: usize,
    lanes: &[usize],
    dense_span: Option<(usize, usize)>,
    destination: usize,
    left: BinaryOperand,
    right: BinaryOperand,
    ctx: &Context<T>,
) {
    let destination = destination * stride;
    macro_rules! lanes {
        ($lane:ident, $left:expr, $right:expr) => {{
            if let Some((begin, end)) = dense_span {
                for $lane in begin..end {
                    let value = operation::<T, MULTIPLY, INLINE>($left, $right);
                    arena[destination + $lane] = value;
                }
            } else {
                for &$lane in lanes {
                    let value = operation::<T, MULTIPLY, INLINE>($left, $right);
                    arena[destination + $lane] = value;
                }
            }
        }};
    }
    match (left, right) {
        (BinaryOperand::Column(a), BinaryOperand::Column(b)) => {
            let (a, b) = (a * stride, b * stride);
            lanes!(lane, &arena[a + lane], &arena[b + lane]);
        }
        (BinaryOperand::Column(a), BinaryOperand::Constant(b)) => {
            let a = a * stride;
            let b = ctx.constant(b);
            lanes!(lane, &arena[a + lane], b);
        }
        (BinaryOperand::Constant(a), BinaryOperand::Column(b)) => {
            let a = ctx.constant(a);
            let b = b * stride;
            lanes!(lane, a, &arena[b + lane]);
        }
        (BinaryOperand::Constant(a), BinaryOperand::Constant(b)) => {
            let (a, b) = (ctx.constant(a), ctx.constant(b));
            lanes!(lane, a, b);
        }
    }
}
