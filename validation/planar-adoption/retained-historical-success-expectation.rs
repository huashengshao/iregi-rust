    #[test]
    fn certified_planar_groups_charts_and_isolates_failed_rows() {
        let configuration = settings(2);
        let plan = CertifiedPlanarReductionPlan::new(configuration.clone()).unwrap();
        let first = row(&0., &points(), 1);
        let alternate = [
            [0, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [2, 0, 1, 1],
        ];
        let second = row(&0., &alternate, 1);
        let mut transverse = first.clone();
        transverse[16].re = 1.;
        let mut bad_scale = first.clone();
        bad_scale[25].re = -1.;
        let input = KinematicsBatch {
            rows: 7,
            components: 1,
            values: [
                first.clone(),
                transverse,
                second.clone(),
                bad_scale,
                first.clone(),
                second.clone(),
                first,
            ]
            .concat(),
        };
        let mut workspace = CertifiedPlanarWorkspace::new(&plan, 0.).unwrap();
        let reduced = workspace.reduce_batch(&input).unwrap();
        eprintln!("primary planar binary64 statuses: {:?}", reduced.statuses);
        let successful = KinematicsBatch {
            rows: 2,
            components: 1,
            values: [row(&0., &points(), 1), second].concat(),
        };
        let expected = box_identity(
            &configuration,
            0.,
            53,
            &None,
            &successful,
            &[constant_weights(&0., 6, 1), constant_weights(&0., 6, 1)].concat(),
        );
        for lane in [0, 2, 4, 5, 6] {
            assert_eq!(reduced.statuses[lane], LaneStatus::Success);
        }
        for lane in [1, 3] {
            assert!(matches!(
                reduced.statuses[lane],
                LaneStatus::InvalidInput(_)
            ));
            assert!(reduced.lane(lane).is_err());
        }
        assert_eq!(workspace.last_certificate_execution().reduction_batches, 2);
        assert_eq!(workspace.last_execution().reduction_rows, 5);
        assert_eq!(workspace.last_execution().analytic_rows, 5);
        assert_eq!(reduced.lane(0).unwrap(), reduced.lane(4).unwrap());
        assert_eq!(reduced.lane(0).unwrap(), reduced.lane(6).unwrap());
        assert_eq!(reduced.lane(2).unwrap(), reduced.lane(5).unwrap());
        let slots = plan.basis.len() * 4;
        for (position, lane) in [0, 2].into_iter().enumerate() {
            for (slot, (actual, expected)) in reduced
                .lane(lane)
                .unwrap()
                .iter()
                .zip(&expected[position * slots..(position + 1) * slots])
                .enumerate()
            {
                let scale = dimensional_reference(
                    &0_f64,
                    &input.values[lane * 26..(lane + 1) * 26],
                    1,
                    &reduced.basis[slot / 4],
                    expected,
                );
                let difference = (actual.re - expected.re).hypot(actual.im - expected.im);
                assert!(difference <= 1e-10 * scale);
            }
        }
    }

