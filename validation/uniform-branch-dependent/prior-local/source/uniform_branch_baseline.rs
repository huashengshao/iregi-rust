use super::*;

/// An expression evaluator that applies each instruction across a batch.
///
/// Inputs and outputs are row-major: a row contains all parameters or results
/// for one sample. Internally, lanes of each stack slot are contiguous. Shared
/// functions receive the same batch, and branches evaluate only their active
/// lanes. Storage is retained between calls and grows to the largest batch seen.
///
/// Map exact coefficients to the desired numeric domain and precision before
/// calling [`ExpressionEvaluator::into_frozen_batch_evaluator`]. Dual numbers can be
/// represented by flattening their components with [`Dualizer`] first.
#[derive(Clone)]
pub struct FrozenBatchExpressionEvaluator<T> {
    evaluator: ExpressionEvaluator<T>,
    workspace: BatchWorkspace<T>,
    functions: Vec<BatchWorkspace<T>>,
    lanes: Vec<usize>,
    capacity: usize,
}

#[derive(Clone)]
struct BatchWorkspace<T> {
    stack: Vec<T>,
    active: Vec<usize>,
    // Forward instruction index at which each lane resumes after a branch.
    resume: Vec<usize>,
}

impl<T> Default for BatchWorkspace<T> {
    fn default() -> Self {
        Self {
            stack: Vec::new(),
            active: Vec::new(),
            resume: Vec::new(),
        }
    }
}

impl<T> ExpressionEvaluator<T> {
    /// Convert to an interpreter that carries batches through instructions and
    /// shared function calls, with reusable storage and lazy per-lane branches.
    ///
    /// ```
    /// use symbolica::prelude::*;
    /// let mut evaluator = parse!("x^2+y")
    ///     .evaluator(&[parse!("x"), parse!("y")]).build().unwrap()
    ///     .map_coeff(&|c| c.re.to_f64()).into_frozen_batch_evaluator();
    /// let mut output = [0.; 3];
    /// evaluator.evaluate_batch(&[2., 1., 3., 2., 4., 3.], &mut output, 3).unwrap();
    /// assert_eq!(output, [5., 11., 19.]);
    /// ```
    pub fn into_frozen_batch_evaluator(self) -> FrozenBatchExpressionEvaluator<T> {
        let functions = (0..self.external_fns.len())
            .map(|_| BatchWorkspace::default())
            .collect();
        FrozenBatchExpressionEvaluator {
            evaluator: self,
            workspace: BatchWorkspace::default(),
            functions,
            lanes: Vec::new(),
            capacity: 0,
        }
    }
}

impl<T> FrozenBatchExpressionEvaluator<T> {
    /// Number of parameters in each input row.
    pub fn get_input_len(&self) -> usize {
        self.evaluator.param_count
    }

    /// Number of results in each output row.
    pub fn get_output_len(&self) -> usize {
        self.evaluator.result_indices.len()
    }

    /// Return the original scalar evaluator, discarding batch workspaces.
    pub fn into_expression_evaluator(self) -> ExpressionEvaluator<T> {
        self.evaluator
    }

    fn size_overflow() -> EvaluationError {
        EvaluationError::EvaluationFailed {
            expression: Atom::num(0),
            reason: "Batch dimensions exceed the addressable buffer size".into(),
        }
    }
}

impl<T: Real> BatchWorkspace<T> {
    fn reserve(&mut self, slots: usize, lanes: usize) -> Result<(), EvaluationError> {
        let size = slots
            .checked_mul(lanes)
            .ok_or_else(FrozenBatchExpressionEvaluator::<T>::size_overflow)?;
        self.stack.resize_with(size, T::new_zero);
        self.resume.resize(lanes, 0);
        if self.active.capacity() < lanes {
            self.active.reserve(lanes - self.active.len());
        }
        Ok(())
    }
}

impl<T: Real> FrozenBatchExpressionEvaluator<T> {
    /// Preallocate reusable root and shared-function workspaces for `rows`.
    pub fn reserve(&mut self, rows: usize) -> Result<(), EvaluationError> {
        if rows <= self.capacity {
            return Ok(());
        }
        self.workspace.reserve(self.evaluator.stack.len(), rows)?;
        for (workspace, function) in self
            .functions
            .iter_mut()
            .zip(&mut self.evaluator.external_fns)
        {
            if let Some(body) = &function.body {
                workspace.reserve(body.stack_size, rows)?;
            }
        }
        self.lanes = (0..rows).collect();
        self.capacity = rows;
        Ok(())
    }

    /// Evaluate `rows` samples. Input and output lengths must be exactly
    /// `rows * get_input_len()` and `rows * get_output_len()`, respectively.
    /// Empty batches are supported, including evaluators with no parameters.
    /// Shape errors leave the output buffer unchanged.
    pub fn evaluate_batch(
        &mut self,
        parameters: &[T],
        out: &mut [T],
        rows: usize,
    ) -> Result<(), EvaluationError> {
        let inputs = rows
            .checked_mul(self.get_input_len())
            .ok_or_else(Self::size_overflow)?;
        let outputs = rows
            .checked_mul(self.get_output_len())
            .ok_or_else(Self::size_overflow)?;
        if parameters.len() != inputs {
            return Err(EvaluationError::InvalidParameterCount {
                expected: inputs,
                actual: parameters.len(),
            });
        }
        if out.len() != outputs {
            return Err(EvaluationError::InvalidOutputCount {
                expected: outputs,
                actual: out.len(),
            });
        }
        if rows == 0 {
            return Ok(());
        }
        // Avoid packing overhead and batch allocations for the scalar case.
        if rows == 1 {
            return self.evaluator.try_evaluate(parameters, out);
        }
        self.reserve(rows)?;
        let stride = self.capacity;
        let evaluator = &mut self.evaluator;
        for parameter in 0..evaluator.param_count {
            for lane in 0..rows {
                self.workspace.stack[parameter * stride + lane]
                    .set_from(&parameters[lane * evaluator.param_count + parameter]);
            }
        }
        for constant in evaluator.param_count..evaluator.reserved_indices {
            for lane in 0..rows {
                self.workspace.stack[constant * stride + lane].set_from(&evaluator.stack[constant]);
            }
        }
        Self::evaluate_program(
            &evaluator.instructions,
            &mut self.workspace,
            &mut evaluator.external_fns,
            &mut self.functions,
            &self.lanes[..rows],
            stride,
        )?;
        for (column, slot) in evaluator.result_indices.iter().enumerate() {
            for lane in 0..rows {
                out[lane * evaluator.result_indices.len() + column]
                    .set_from(&self.workspace.stack[slot * stride + lane]);
            }
        }
        Ok(())
    }

    fn evaluate_program(
        instructions: &[(Instr, ComplexPhase)],
        workspace: &mut BatchWorkspace<T>,
        external_fns: &mut [ExternalFunctionContainer<T>],
        functions: &mut [BatchWorkspace<T>],
        lanes: &[usize],
        stride: usize,
    ) -> Result<(), EvaluationError> {
        let BatchWorkspace {
            stack,
            active,
            resume,
        } = workspace;
        active.clear();
        active.extend_from_slice(lanes);
        for lane in lanes {
            resume[*lane] = 0;
        }
        let mut temporary = T::new_zero();
        for (pc, (instruction, _)) in instructions.iter().enumerate() {
            #[cfg(test)]
            super::batch::uniform_branch_tests::record_step(pc, instruction, lanes.len(), active);
            match instruction {
                Instr::Label(_) => {
                    active.clear();
                    active.extend(lanes.iter().copied().filter(|lane| resume[*lane] <= pc));
                }
                Instr::Goto(label) => {
                    debug_assert!(label.0 > pc, "Batch programs have forward branches");
                    for lane in active.iter() {
                        resume[*lane] = label.0;
                    }
                    active.clear();
                }
                Instr::IfElse(condition, label) => {
                    debug_assert!(label.0 > pc, "Batch programs have forward branches");
                    active.retain(|lane| {
                        if stack[condition * stride + lane].is_fully_zero() {
                            resume[*lane] = label.0;
                            false
                        } else {
                            true
                        }
                    });
                }
                Instr::Add(out, args) | Instr::Mul(out, args) => {
                    for lane in active.iter().copied() {
                        temporary.set_from(&stack[args[0] * stride + lane]);
                        for arg in &args[1..] {
                            if matches!(instruction, Instr::Add(..)) {
                                temporary += &stack[arg * stride + lane];
                            } else {
                                temporary *= &stack[arg * stride + lane];
                            }
                        }
                        std::mem::swap(&mut stack[out * stride + lane], &mut temporary);
                    }
                }
                Instr::Pow(out, base, exponent) => {
                    for lane in active.iter().copied() {
                        let value = &stack[base * stride + lane];
                        temporary = if *exponent == -1 {
                            value.inv()
                        } else if *exponent >= 0 {
                            value.pow(*exponent as u64)
                        } else {
                            value.pow(exponent.unsigned_abs()).inv()
                        };
                        std::mem::swap(&mut stack[out * stride + lane], &mut temporary);
                    }
                }
                Instr::Powf(out, base, exponent) => {
                    for lane in active.iter().copied() {
                        temporary =
                            stack[base * stride + lane].powf(&stack[exponent * stride + lane]);
                        std::mem::swap(&mut stack[out * stride + lane], &mut temporary);
                    }
                }
                Instr::BuiltinFun(out, symbol, arg) => {
                    for lane in active.iter().copied() {
                        let value = &stack[arg * stride + lane];
                        temporary = match symbol.get_id() {
                            Symbol::EXP_ID => value.exp(),
                            Symbol::LOG_ID => value.log(),
                            Symbol::SIN_ID => value.sin(),
                            Symbol::COS_ID => value.cos(),
                            Symbol::SQRT_ID => value.sqrt(),
                            Symbol::ABS_ID => value.norm(),
                            Symbol::CONJ_ID => value.conj(),
                            _ => unreachable!("Unsupported built-in evaluator instruction"),
                        };
                        std::mem::swap(&mut stack[out * stride + lane], &mut temporary);
                    }
                }
                Instr::Join(out, condition, then_value, else_value) => {
                    for lane in active.iter().copied() {
                        let value = if stack[condition * stride + lane].is_fully_zero() {
                            else_value
                        } else {
                            then_value
                        };
                        temporary.set_from(&stack[value * stride + lane]);
                        std::mem::swap(&mut stack[out * stride + lane], &mut temporary);
                    }
                }
                Instr::ExternalFun(out, index, args) => {
                    if active.is_empty() {
                        continue;
                    }
                    let (callees, current) = external_fns.split_at_mut(*index);
                    let (callee_workspaces, current_workspace) = functions.split_at_mut(*index);
                    let external = &mut current[0];
                    if let Some(body) = &external.body {
                        let workspace = &mut current_workspace[0];
                        debug_assert_eq!(args.len(), body.param_count);
                        for (parameter, arg) in args.iter().enumerate() {
                            for lane in active.iter().copied() {
                                workspace.stack[parameter * stride + lane]
                                    .set_from(&stack[arg * stride + lane]);
                            }
                        }
                        Self::evaluate_program(
                            &body.instructions,
                            workspace,
                            callees,
                            callee_workspaces,
                            active,
                            stride,
                        )?;
                        for lane in active.iter().copied() {
                            stack[out * stride + lane]
                                .set_from(&workspace.stack[body.result_index * stride + lane]);
                        }
                    } else if let Some(function) = &external.imp {
                        if external.stack.len() < args.len() {
                            external.stack.resize_with(args.len(), T::new_zero);
                        }
                        for lane in active.iter().copied() {
                            for (value, arg) in external.stack.iter_mut().zip(args) {
                                value.set_from(&stack[arg * stride + lane]);
                            }
                            stack[out * stride + lane] = function(&external.stack[..args.len()]);
                        }
                    } else {
                        return Err(EvaluationError::EvaluationFailed {
                            expression: external.symbol.call(&external.tags),
                            reason: format!(
                                "No function implementation for {}",
                                std::any::type_name::<T>()
                            ),
                        });
                    }
                }
            }
        }
        Ok(())
    }
}

