//! Private concrete-f64 dispatcher over unchanged generated kernels.
use oneloop::{
    ScalarIntegral,
    rust_codegen::runtime::{
        BatchExecutionPolicy, BatchWorkspace, C, ConstantSpec, Context, NativeFloat, batch, primitives,
    },
};

#[rustfmt::skip]
#[allow(clippy::all, unused_assignments, dead_code)]
#[path = "generated/a0.rs"]
mod a0;
#[rustfmt::skip]
#[allow(clippy::all, unused_assignments, dead_code)]
#[path = "generated/b0.rs"]
mod b0;
#[rustfmt::skip]
#[allow(clippy::all, unused_assignments, dead_code)]
#[path = "generated/c0.rs"]
mod c0;
#[rustfmt::skip]
#[allow(clippy::all, unused_assignments, dead_code)]
#[path = "generated/constants.rs"]
mod constants;

#[derive(Clone)]
pub(crate) struct SelectedBatchEvaluator {
    family: ScalarIntegral,
    context: Context<f64>,
    workspace: BatchWorkspace<f64>,
    policy: BatchExecutionPolicy,
}

impl SelectedBatchEvaluator {
    pub(crate) fn new(family: ScalarIntegral) -> Result<Self, String> {
        if !matches!(family, ScalarIntegral::A0 | ScalarIntegral::B0 | ScalarIntegral::C0) {
            return Err("private native selection supports A0/B0/C0 only".into());
        }
        Ok(Self {
            family,
            context: Context::new(constants::CONSTANTS, 53)?,
            workspace: BatchWorkspace::new(0.),
            policy: BatchExecutionPolicy::Whole,
        })
    }

    pub(crate) fn set_policy(&mut self, policy: BatchExecutionPolicy) {
        self.policy = policy;
    }

    pub(crate) fn evaluate_batch<T: super::NativeFloat>(
        &mut self,
        input: &Vec<C<T>>,
        output: &mut Vec<C<T>>,
        rows: usize,
    ) -> Result<(), String> {
        let input = (input as &dyn std::any::Any)
            .downcast_ref::<Vec<C<f64>>>()
            .ok_or("private native input type differs from f64")?;
        let output = (output as &mut dyn std::any::Any)
            .downcast_mut::<Vec<C<f64>>>()
            .ok_or("private native output type differs from f64")?;
        let family = self.family;
        let context = &self.context;
        self.policy.evaluate(
            input,
            output,
            rows,
            (family.arity(), super::OUTPUTS),
            &mut self.workspace,
            |input, output, rows, workspace| match family {
                ScalarIntegral::A0 => a0::evaluate_batch(input, output, rows, context, workspace),
                ScalarIntegral::B0 => b0::evaluate_batch(input, output, rows, context, workspace),
                ScalarIntegral::C0 => c0::evaluate_batch(input, output, rows, context, workspace),
                _ => unreachable!("selected family validated at construction"),
            },
        )
    }
}
