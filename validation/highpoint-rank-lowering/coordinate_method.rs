    /// Private experiment: require coordinates and distances to describe the
    /// same preserved four-vectors. Callers inside plan.rs enforce this domain.
    pub(crate) fn enable_highpoint_rank_lowering(&mut self) -> Result<(), String> {
        if !self.moments.is_empty() || !self.coefficients.is_empty() {
            return Err("enable high-point rank lowering before compiling moments".into());
        }
        self.highpoint_rank_lowering = true;
        Ok(())
    }

    /// Exact Cartesian q^mu = sum_i w_i^mu D_i. One inverse and one four-RHS
    /// matrix product per chart, reused by every moment and Laurent coefficient.
    /// The scalar rank-zero identity intentionally remains the existing path.
    fn highpoint_coordinate_identity(
        &mut self,
        active: &[usize],
    ) -> Result<Option<[Vec<Atom>; 4]>, String> {
        if let Some(value) = self.highpoint_coordinate_identities.get(active) {
            return Ok(value.clone());
        }
        if !(6..=7).contains(&active.len()) {
            return Ok(None);
        }
        let origin = self.shifts[active[0]].clone();
        let mut rows = coordinate_rows(&self.shifts, active);
        rows.push(self.f_values(active));
        let rhs = Matrix::from_nested_vec(
            (0..5)
                .map(|row| {
                    (0..4)
                        .map(|mu| {
                            if row == 4 {
                                -&origin[mu]
                            } else if row == mu {
                                Atom::num(if mu == 0 { 1 } else { -1 }) / Atom::num(2)
                            } else {
                                Atom::new()
                            }
                        })
                        .collect()
                })
                .collect(),
            field(),
        )
        .map_err(|e| format!("PV Cartesian identity RHS: {e}"))?;
        // Same deterministic order as the existing seven-point identity.
        // Every chart remains lazy; an all-singular numerical lane retains an
        // active inverse denominator and is rejected by the ordinary guards.
        let selections: Vec<Vec<usize>> = if active.len() == 6 {
            vec![(0..5).collect()]
        } else {
            (0..6)
                .rev()
                .map(|omitted| (0..6).filter(|&j| j != omitted).collect())
                .collect()
        };
        let mut charts = Vec::new();
        for columns in selections {
            let matrix = Matrix::from_nested_vec(
                rows.iter()
                    .map(|row| columns.iter().map(|&j| row[j].clone()).collect())
                    .collect(),
                field(),
            )
            .map_err(|e| format!("PV Cartesian identity matrix: {e}"))?;
            let determinant = matrix
                .det()
                .map_err(|e| format!("PV Cartesian identity determinant: {e:?}"))?;
            if determinant.is_zero() {
                continue;
            }
            let inverse = matrix
                .inv()
                .map_err(|e| format!("PV Cartesian identity inverse: {e:?}"))?;
            let solution = &inverse * &rhs;
            let mut factors: [Vec<Atom>; 4] =
                std::array::from_fn(|_| vec![Atom::new(); active.len()]);
            for mu in 0..4 {
                for (row, &column) in columns.iter().enumerate() {
                    factors[mu][column + 1] = solution[(row as u32, mu as u32)].clone();
                }
                factors[mu][0] = -Atom::add_many(&factors[mu][1..]);
            }
            charts.push((self.bind_alias(determinant), factors));
        }
        let result = charts.pop().map(|(_, mut factors)| {
            for (determinant, candidate) in charts.into_iter().rev() {
                for mu in 0..4 {
                    for (factor, alternate) in factors[mu].iter_mut().zip(&candidate[mu]) {
                        *factor = conditional(&determinant, alternate, factor);
                    }
                }
            }
            factors.map(|direction| direction.into_iter().map(|x| self.bind_alias(x)).collect())
        });
        // A structurally deficient K may still admit the old constant RHS.
        // None explicitly requests that unchanged path; it is never zero data.
        self.highpoint_coordinate_identities.insert(active.to_vec(), result.clone());
        Ok(result)
    }
