"""Posthoc revision2: separate clean termination from one row's short block.

This changes admission metadata only. Numerical and statistical gates remain in
the frozen analyzer. It never launches kernels and does not modify producer data.
"""
import math

ERROR_FIELDS=('error','guard_error','raw_hash_error')

def validate_terminal(receipt):
    assert receipt['mode']=='timing', 'not a timing receipt'
    assert receipt['status'] in ('completed','inconclusive-or-failed'), 'nonterminal status'
    assert not any(key in receipt for key in ERROR_FIELDS), 'global error field present'
    assert receipt['cleanup_errors']==[], 'cleanup failed'
    assert receipt['deadline_exceeded'] is False, 'deadline exceeded'
    assert receipt['inputs_unchanged'] is True, 'input guards failed'
    assert receipt['process_exit_codes']=={'probe':0,'iregi':0,'collier':0}, 'child exit failure'
    assert type(receipt['raw_sha256']) is str and len(receipt['raw_sha256'])==64, 'missing raw digest'
    assert receipt['initialization']['status']=='passed', 'initialization failed'
    assert receipt['controls_before']['status']==receipt['controls_after']['status']=='passed', 'controls failed'
    elapsed=[receipt[key]for key in ['numerical_elapsed_seconds','cleanup_finished_elapsed_seconds','elapsed_seconds']]
    assert all(type(value)in[int,float]and math.isfinite(value)for value in elapsed), 'invalid elapsed time'
    assert 0<=elapsed[0]<=elapsed[1]<=elapsed[2]<=700, 'elapsed time out of bounds'

def validate_rows(receipt,raw,coordinates,orders):
    """Require all eight fully measured rows; derive short status from raw data."""
    assert len(coordinates)==8 and len(set(coordinates))==8
    assert [(r['id'],r['outer_batch'])for r in receipt['rows']]==coordinates, 'row inventory differs'
    assert len(orders)==48
    any_short=False
    for row,(family,batch)in zip(receipt['rows'],coordinates):
        assert type(row['outer_batch'])is int and row['outer_batch']==batch
        assert not any(key in row for key in ERROR_FIELDS), 'row error field present'
        assert row['before_after_qualification']=='passed', 'row numerical admission failed'
        assert type(row['iterations'])is int and row['iterations']>0, 'invalid shared iteration count'
        blocks=row['blocks'];assert len(blocks)==48, 'incomplete family'
        short=0
        for index,(block,order)in enumerate(zip(blocks,orders)):
            assert type(block['index'])is int and block['index']==index
            assert block['order']==list(order), 'quartet order differs'
            assert [v['engine']for v in block['engines']]==list(order), 'incomplete quartet'
            for value in block['engines']:
                serial=value['raw_serial'];assert type(serial)is int and 0<=serial<len(raw)
                rr=raw[serial]
                assert type(rr['serial'])is int and rr['serial']==serial
                assert rr['stage']=='acceptance' and rr['id']==family
                assert type(rr['batch'])is int and rr['batch']==batch
                assert type(rr['block'])is int and rr['block']==index
                assert rr['engine']==value['engine']
                assert type(value['iterations'])is int and type(rr['iterations'])is int
                assert value['iterations']==rr['iterations']==row['iterations']
                response=rr['response'];total=response['total_ns']
                assert type(total)is list and len(total)==1
                ns=total[0];assert type(ns)in[int,float]and math.isfinite(ns)and ns>0
                if value['engine']in ('baselineTIRust','candidateTIRust'):
                    elapsed_values=response['elapsed_ns'];assert type(elapsed_values)is list and len(elapsed_values)==1
                    elapsed=elapsed_values[0]
                    assert type(elapsed)is int and elapsed>0
                    assert ns==elapsed/row['iterations']
                else:
                    assert value['engine']in ('iregi','collier')
                    elapsed=ns*row['iterations']
                assert type(value['elapsed_ns'])in[int,float]and math.isfinite(value['elapsed_ns'])
                assert value['elapsed_ns']==elapsed and value['ns_per_call']==ns, 'raw duration differs'
                short+=elapsed<100_000_000
        assert type(row['short_blocks'])is int and row['short_blocks']==short, 'stored short count differs'
        expected='short-block-inconclusive'if short else'completed'
        assert row['status']==expected, 'row status does not follow raw blocks'
        any_short|=short>0
    expected='inconclusive-or-failed'if any_short else'completed'
    assert receipt['status']==expected, 'aggregate status has an unexplained failure'
