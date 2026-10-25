"""Pure admission of saved ``rustc -Zls=root`` metadata identities.

Importing launches nothing and reads no files. The bounded caller is responsible
for extracting metadata from the actual new archive, binding archive/metadata
bytes, and checking compiler/sysroot, source and command provenance. This module
checks the crate identities in that saved metadata, including the flattened
transitive External Dependencies list emitted by the pinned compiler. It does
not replace those external byte guards and does not infer source equality from
an archive filename, ThinLTO linker-map visibility or a successful compiler exit.
"""
from collections.abc import Mapping
import re

_NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]*(?:-[0-9a-f]{16})?\Z')
_HASH = re.compile(r'[0-9a-f]{1,32}\Z')
_SHA256 = re.compile(r'[0-9a-f]{64}\Z')
_STABLE = re.compile(r'StableCrateId\(([0-9]+)\)\Z')
_DEP = re.compile(
    r'([1-9][0-9]*) ([A-Za-z_][A-Za-z0-9_]*(?:-[0-9a-f]{16})?) '
    r'hash ([0-9a-f]{1,32}) host_hash None '
    r'kind (?:Unconditional|Conditional|MacrosOnly) (?:public|private)'
    r'(?: linkage Some\(RequireStatic\))?\Z')
_PROJECT = ('symbolica', 'oneloop', 'iregi')
_FRESH_NAMES = frozenset({'symbolica', 'oneloop', 'iregi_masters', 'iregi_rust'})
_METADATA_KEYS = {'name', 'crate_hash', 'stable_crate_id', 'dependencies'}

class ProvenanceError(ValueError):
    """A metadata/identity binding is missing, ambiguous or outside the cohort."""


def _require(condition, message):
    if not condition:
        raise ProvenanceError(message)


def _name(value):
    _require(type(value) is str and _NAME.fullmatch(value) is not None,
             'Invalid metadata crate display name')
    return value


def _hash(value):
    _require(type(value) is str and _HASH.fullmatch(value) is not None,
             'Invalid metadata crate hash')
    return value


def _project_name(value):
    return value.lower().startswith(_PROJECT)


def _pairs(value, label):
    _require(isinstance(value, Mapping), label + ' must be a mapping')
    result = {}
    hash_names = {}
    for name, crate_hash in value.items():
        _name(name)
        _hash(crate_hash)
        _require(name not in result, label + ': duplicate crate name ' + name)
        _require(crate_hash not in hash_names,
                 label + ': one crate hash is bound to multiple display names')
        result[name] = crate_hash
        hash_names[crate_hash] = name
    return result


def _metadata(value):
    _require(type(value) is dict and set(value) == _METADATA_KEYS,
             'Metadata object has missing or extra fields')
    name = _name(value['name'])
    crate_hash = _hash(value['crate_hash'])
    stable = value['stable_crate_id']
    _require(type(stable) is str and _STABLE.fullmatch(stable) is not None,
             'Missing or invalid stable crate ID')
    stable_number = int(_STABLE.fullmatch(stable).group(1))
    _require(stable_number <= 2**64 - 1, 'Stable crate ID exceeds u64')
    dependencies = _pairs(value['dependencies'], 'Metadata dependencies')
    _require(name not in dependencies, 'Archive lists itself as a dependency')
    _require(crate_hash not in dependencies.values(),
             'Archive root hash collides with a dependency hash')
    return {'name': name, 'crate_hash': crate_hash, 'stable_crate_id': stable,
            'dependencies': dependencies}


def parse(text):
    """Parse one actual saved metadata root, rejecting duplicate/ignored rows.

    The grammar deliberately follows this experiment's pinned Rust1.99 output.
    A different compiler format must fail for review rather than silently skip
    a dependency. In particular, duplicate rows must not be hidden by dict().
    """
    _require(type(text) is str, 'Metadata text must be a string')
    lines = text.splitlines()
    _require(lines.count('Crate info:') == 1, 'Expected one Crate info header')
    _require(lines.count('=External Dependencies=') == 1,
             'Expected one External Dependencies section')
    split = lines.index('=External Dependencies=')
    header, rows = lines[:split], lines[split + 1:]
    names = [line[5:] for line in header if line.startswith('name ')]
    roots = [line for line in header if line.startswith('hash ')]
    _require(len(names) == len(roots) == 1, 'Expected one root name/hash')
    root = re.fullmatch(r'hash ([0-9a-f]{1,32}) stable_crate_id (StableCrateId\([0-9]+\))', roots[0])
    _require(root is not None, 'Malformed root hash/stable ID')
    _require(not any(re.match(r'^[0-9]+ ', line) for line in header),
             'Dependency row appeared before External Dependencies')
    dependencies = {}
    indices = []
    for line in rows:
        if not line.strip():
            continue
        match = _DEP.fullmatch(line)
        _require(match is not None, 'Malformed or unparsed dependency row: ' + line)
        index, name, crate_hash = int(match.group(1)), match.group(2), match.group(3)
        _require(name not in dependencies, 'Duplicate dependency display name: ' + name)
        dependencies[name] = crate_hash
        indices.append(index)
    _require(indices == list(range(1, len(indices) + 1)),
             'Dependency row indices are duplicated, omitted or reordered')
    return _metadata({'name': names[0], 'crate_hash': root.group(1),
                      'stable_crate_id': root.group(2), 'dependencies': dependencies})


def _fresh_pairs(required_fresh):
    """Accept exact expected root hashes or full already-observed root metadata."""
    _require(isinstance(required_fresh, Mapping), 'required_fresh must be a mapping')
    identities, metadata = {}, {}
    for name, value in required_fresh.items():
        _name(name)
        _require(name in _FRESH_NAMES, 'Fresh predecessor is not an exact expected project root: ' + name)
        _require('-' not in name, 'Fresh predecessor must use its exact plain root name')
        if isinstance(value, Mapping):
            item = _metadata(value)
            _require(item['name'] == name, 'Fresh predecessor name differs from metadata root')
            identities[name] = item['crate_hash']
            metadata[name] = item
        else:
            identities[name] = _hash(value)
    return _pairs(identities, 'Fresh predecessor roots'), metadata


def admit(actual, *, expected_root_name, allowed_lower, required_fresh,
          expected_root_hash=None):
    """Admit one actual fresh archive's complete root/dependency identity set.

    ``allowed_lower`` maps exact lower display names to crate hashes, including
    the separately scoped hash-bound trusted sysroot context where applicable.
    ``required_fresh`` maps every expected same-variant predecessor plain root
    name to its actual previously observed hash or complete metadata object.
    Every required predecessor must occur in the actual archive dependencies.
    No unexpected project identity may enter through the lower allowlist.

    This validates crate ABI metadata, not numerical execution or performance.
    Full predecessor records additionally check inherited transitive closure.
    """
    item = parse(actual) if type(actual) is str else _metadata(actual)
    expected_root_name = _name(expected_root_name)
    _require(item['name'] == expected_root_name, 'Actual archive root name differs from expected')
    if _project_name(expected_root_name):
        _require(expected_root_name in _FRESH_NAMES, 'Actual project root uses an unexpected alias')
    if expected_root_hash is not None:
        _require(item['crate_hash'] == _hash(expected_root_hash),
                 'Actual archive root hash differs from expected')
    lower = _pairs(allowed_lower, 'Allowed lower roots')
    _require(not any(_project_name(name) for name in lower),
             'Project crate identity must not be admitted as a lower dependency')
    fresh, predecessors = _fresh_pairs(required_fresh)
    _require(item['name'] not in fresh, 'Archive root also supplied as a predecessor')
    _require(item['name'] not in lower, 'Archive root collides with a lower display name')
    combined = dict(lower)
    _require(not set(combined).intersection(fresh), 'Fresh/lower display-name collision')
    combined.update(fresh)
    _pairs(combined, 'Combined allowed roots')
    _require(item['crate_hash'] not in combined.values(),
             'Actual root hash collides with an allowed dependency root')
    for name, wanted in fresh.items():
        _require(item['dependencies'].get(name) == wanted,
                 'Required actual fresh predecessor missing or wrong hash: ' + name)
    for name, observed in item['dependencies'].items():
        _require(name in combined, 'Unknown dependency identity: ' + name)
        _require(combined[name] == observed, 'Wrong dependency crate hash: ' + name)
        if _project_name(name):
            _require(name in fresh, 'Unexpected project dependency: ' + name)
    # Rust -Zls=root enumerates the flattened transitive dependency identity set.
    # With complete predecessor records, independently require all inherited
    # names/hashes to survive in this actual archive's flattened list.
    for predecessor in predecessors.values():
        for name, wanted in predecessor['dependencies'].items():
            _require(name in combined and combined[name] == wanted,
                     'Predecessor contains an unknown or conflicting dependency: ' + name)
            _require(item['dependencies'].get(name) == wanted,
                     'Actual archive omits a predecessor transitive dependency: ' + name)
    return {'status': 'passed', 'scope': 'actual archive crate ABI metadata admission only',
            'root': {key: item[key] for key in ('name', 'crate_hash', 'stable_crate_id')},
            'dependencies': dict(item['dependencies']),
            'lower_dependency_count': sum(name in lower for name in item['dependencies']),
            'fresh_predecessors': dict(fresh),
            'predecessor_full_metadata_checked': sorted(predecessors),
            'unknown_or_conflicting_dependencies': [],
            'artifact_and_metadata_bytes_guard_required_from_caller': True,
            'numerical_qualified': False, 'performance_qualified': False}


def _sha256(value):
    _require(type(value) is str and _SHA256.fullmatch(value) is not None,
             'Missing or invalid SHA256 binding')
    return value


def _absolute_path(value):
    _require(type(value) is str and value.startswith('/') and '\x00' not in value,
             'Expected an absolute bound artifact path')
    _require(all(part not in ('.', '..') for part in value.split('/')),
             'Non-normalized bound artifact path')
    return value


def _project_record(value):
    _require(type(value) is dict and _METADATA_KEYS.issubset(value),
             'Observed metadata record is incomplete')
    return _metadata({key: value[key] for key in _METADATA_KEYS})


def _record_bindings(value):
    """Validate binding declarations only; actual byte hashing belongs to caller."""
    bindings = {}
    for path_key, hash_key in [('artifact', 'sha256'), ('metadata_path', 'metadata_sha256')]:
        path, wanted = _absolute_path(value[path_key]), _sha256(value[hash_key])
        _require(path not in bindings, 'Artifact and metadata paths collide')
        bindings[path] = wanted
    if 'original_guarded_artifact' in value or 'original_guarded_sha256' in value:
        path = _absolute_path(value.get('original_guarded_artifact'))
        wanted = _sha256(value.get('original_guarded_sha256'))
        _require(path not in bindings or bindings[path] == wanted,
                 'Original artifact byte binding conflicts')
        bindings[path] = wanted
    return bindings


def lower_from_proof(proof):
    """Validate the completed 108+19 lower metadata proof and return exact pairs.

    This accepts the completed ``lower-admission-inputs.json`` schema, not the
    preserved first lower inspection receipt that contains a sysroot-stub ICE.
    The nineteen full sysroot .rmeta observations are NEW supplementary bindings;
    they are not described as old pre-run guards. All127 actual metadata roots,
    dependency edges, source/file binding declarations and108 closed-directory
    entries are checked. Call ``binding_requirements`` and actually hash those
    files in the bounded owner before/after use; this pure function reads none.
    """
    _require(type(proof) is dict and type(proof.get('schema_version')) is int and proof['schema_version'] == 1,
             'Wrong lower proof schema')
    _require(proof.get('status') == 'completed_readonly_project_dependency_identity_proof_no_build',
             'Lower proof is not the completed independently scoped identity proof')
    _require(proof.get('original_failure_preserved') is True,
             'Original failed build evidence is not preserved')
    _require(proof.get('original_full_search_directory_was_pre_guarded') is False,
             'Original broad dependency directory must not be relabelled pre-guarded')
    for key in ('numerical_qualified', 'performance_qualified', 'production_adoption_authorized'):
        _require(proof.get(key) is False, 'Metadata-only proof overclaims ' + key)
    roots = proof.get('lower_roots')
    _require(type(roots) is dict and len(roots) == 127,
             'Expected all127 observed lower roots')
    lower, records, non_sysroot, sysroot = {}, {}, {}, {}
    binding_paths = {}
    stable_ids = {}
    for name, raw in roots.items():
        _name(name)
        _require(not _project_name(name), 'Project crate found in lower proof')
        item = _project_record(raw)
        _require(item['name'] == name, 'Lower display name differs from actual root name')
        _require(item['stable_crate_id'] not in stable_ids,
                 'Lower stable crate ID collides with another root')
        stable_ids[item['stable_crate_id']] = name
        lower[name] = item['crate_hash']
        records[name] = item
        for path, wanted in _record_bindings(raw).items():
            _require(path not in binding_paths or binding_paths[path] == wanted,
                     'Conflicting lower file byte bindings')
            binding_paths[path] = wanted
        _require(raw['metadata_path'].rsplit('/', 1)[-1] == name + '.txt',
                 'Lower metadata log basename differs from actual root')
        artifact_leaf = raw['artifact'].rsplit('/', 1)[-1]
        origin = raw.get('metadata_context_origin')
        if artifact_leaf == 'lib' + name + '.rmeta':
            _require(origin == 'NEW supplemental full sysroot rmeta root identity; original guarded matching-name rlib remains separately bound. No original rmeta guard claimed.',
                     'Supplemental sysroot binding origin is missing or overstated')
            _require(raw['artifact'].startswith('/nix/store/'),
                     'Supplemental sysroot metadata is outside the pinned Nix toolchain')
            _require(raw['original_guarded_artifact'] == raw['artifact'][:-6] + '.rlib',
                     'Supplemental sysroot metadata lacks matching original rlib')
            sysroot[name] = raw
        else:
            _require(artifact_leaf in ('lib' + name + '.rlib', 'lib' + name + '.so'),
                     'Lower artifact filename differs from actual metadata root')
            _require(origin == 'actual root metadata of archive guarded before and after original build',
                     'Original lower archive provenance is not explicit')
            _require(raw['artifact'] == raw['original_guarded_artifact']
                     and raw['sha256'] == raw['original_guarded_sha256'],
                     'Original lower artifact byte binding changed')
            non_sysroot[name] = raw
    lower = _pairs(lower, 'Observed lower roots')
    _require(len(non_sysroot) == 108 and len(sysroot) == 19,
             'Lower root split is not108original+19supplemental')
    expected_counts = {'actual_guarded_non_sysroot_archives': 108,
                       'new_full_sysroot_rmeta_observations': 19,
                       'total_observed_lower_root_identities': 127}
    _require(proof.get('lower_root_counts') == expected_counts
             and all(type(value) is int for value in proof['lower_root_counts'].values()),
             'Lower proof counts differ')
    edges = 0
    for item in records.values():
        for name, wanted in item['dependencies'].items():
            _require(lower.get(name) == wanted, 'Lower dependency closure is not exact: ' + name)
            edges += 1
    fresh_raw = proof.get('fresh')
    _require(type(fresh_raw) is dict and set(fresh_raw) == {'symbolica', 'oneloop', 'iregi_masters', 'iregi_rust'},
             'Expected four actual project roots in supporting proof')
    fresh = {name: _project_record(raw) for name, raw in fresh_raw.items()}
    for name, item in fresh.items():
        _require(item['name'] == name, 'Supporting fresh metadata root name differs')
        _record_bindings(fresh_raw[name])
        required = {dep: fresh[dep] for dep in item['dependencies'] if dep in fresh}
        admit(item, expected_root_name=name, allowed_lower=lower, required_fresh=required)
        edges += len(item['dependencies'])
    _require(type(proof.get('validated_metadata_dependency_edges')) is int
             and proof['validated_metadata_dependency_edges'] == edges,
             'Supporting metadata edge count differs')
    inventory = proof.get('closed_lower_symlink_inventory')
    _require(type(inventory) is dict and len(inventory) == 108,
             'Closed lower directory does not enumerate108 allowed files')
    seen = set()
    for leaf, value in inventory.items():
        _require(type(value) is dict and set(value) == {'target', 'sha256', 'name', 'crate_hash'},
                 'Closed lower inventory record has missing or extra fields')
        name = value['name']
        _require(name in non_sysroot and name not in seen, 'Unknown or duplicate closed lower root')
        original = non_sysroot[name]
        _require(leaf == original['artifact'].rsplit('/', 1)[-1]
                 and value['target'] == original['artifact']
                 and value['sha256'] == original['sha256']
                 and value['crate_hash'] == lower[name],
                 'Closed lower inventory identity/file binding differs')
        seen.add(name)
    _require(seen == set(non_sysroot), 'Closed lower inventory omits an observed root')
    for field, expected in [('new_sysroot_rmeta_bindings', {v['artifact']: v['sha256'] for v in sysroot.values()}),
                            ('original_guarded_sysroot_rlibs', {v['original_guarded_artifact']: v['original_guarded_sha256'] for v in sysroot.values()})]:
        _require(proof.get(field) == expected, 'Supplemental/original sysroot binding split differs')
    sources = proof.get('source_sha256')
    _require(type(sources) is dict and len(sources) > 0, 'Supporting proof source bindings missing')
    for path, wanted in sources.items():
        _absolute_path(path)
        _sha256(wanted)
    _absolute_path(proof.get('original_failed_build_receipt'))
    _sha256(proof.get('original_failed_build_receipt_sha256'))
    stale = proof.get('stale_root_observations')
    _require(type(stale) is list and len(stale) == 10, 'Observed stale roots are not retained')
    stale_hashes = set()
    for raw in stale:
        item = _project_record(raw)
        _require(_project_name(item['name']), 'Non-project identity in stale project observations')
        stale_hashes.add(item['crate_hash'])
    _require(proof.get('fresh_root_hashes_disjoint_from_all_observed_stale_roots') is True
             and not stale_hashes.intersection(item['crate_hash'] for item in fresh.values()),
             'Fresh root hash overlaps an observed stale project root')
    return lower


def binding_requirements(proof):
    """Return lower/fresh/source file hashes that the caller must actually guard."""
    lower_from_proof(proof)
    bindings = {}
    def add(path, wanted):
        _absolute_path(path)
        _sha256(wanted)
        _require(path not in bindings or bindings[path] == wanted,
                 'Conflicting proof-wide file byte bindings')
        bindings[path] = wanted
    for raw in list(proof['lower_roots'].values()) + list(proof['fresh'].values()):
        for path, wanted in _record_bindings(raw).items():
            add(path, wanted)
    for path, wanted in proof['source_sha256'].items():
        add(path, wanted)
    add(proof['original_failed_build_receipt'], proof['original_failed_build_receipt_sha256'])
    return bindings
