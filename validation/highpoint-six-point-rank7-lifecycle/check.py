"""Portable saved-data replay. No Rust, Symbolica, masters or integral runs.

The original frozen numerical comparator is replayed against an in-memory
filesystem populated from hashed evidence and an inherited source archive.
Original independent audit scripts/receipts are preserved, not reinterpreted
as new independent audits or current-host process-group checks.
"""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def require(ok, why):
    if not ok:
        raise ValueError(why)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def archive(path, expected):
    require(digest(path.read_bytes()) == expected, "archive checksum "+str(path))
    result = {}
    with tarfile.open(path, "r:gz") as stream:
        for item in stream.getmembers():
            require(item.isfile() and not item.issym() and not item.islnk(), "regular archive member required")
            name = PurePosixPath(item.name)
            require(not name.is_absolute() and ".." not in name.parts and item.name not in result,
                    "unsafe/duplicate archive name")
            result[item.name] = stream.extractfile(item).read()
    return result


def main():
    manifest = json.loads((HERE/"manifest.json").read_text())
    for name, expected in manifest["capsule_files"].items():
        require(digest((HERE/name).read_bytes()) == expected, "capsule checksum "+name)
    parent = ROOT/manifest["parent"]["directory"]
    for name, expected in manifest["parent"]["files"].items():
        require(digest((parent/name).read_bytes()) == expected, "inherited parent checksum "+name)
    data = archive(HERE/"evidence.tar.gz", manifest["capsule_files"]["evidence.tar.gz"])
    require(set(data) == set(manifest["payload_members"]), "exact evidence member inventory")
    for name, record in manifest["payload_members"].items():
        require(len(data[name]) == record["bytes"] and digest(data[name]) == record["sha256"], "evidence bytes "+name)
    inherited_sources = archive(parent/"sources.tar.gz", manifest["parent"]["files"]["sources.tar.gz"])
    original_root = manifest["original_root"]

    def canonical(path):
        value = str(path)
        if value.startswith(original_root+"/"):
            return value[len(original_root)+1:]
        return value

    for name, provider in manifest["inherited_files"].items():
        value = (ROOT/provider["path"]).read_bytes()
        require(digest(value) == provider["sha256"], "inherited evidence "+name)
        require(name not in data, "duplicate inherited evidence name")
        data[name] = value
    for name, expected in manifest["source_files"].items():
        value = (data[manifest["source_deltas"][name]] if name in manifest["source_deltas"]
                 else inherited_sources[name])
        require(digest(value) == expected, "exact captured source "+name)
        data[name] = value
        data[manifest["snapshot_prefix"]+name] = value
    omitted = {}
    for name, expected in manifest["omitted_binary_guards"].items():
        omitted[canonical(name)] = expected

    def get(path):
        name = canonical(path)
        require(name in data, "unavailable evidence "+name)
        return data[name]

    checked_guards = omitted_guards = 0
    for receipt_name in manifest["receipts"]:
        receipt = json.loads(get(receipt_name))
        require(receipt["status"] == "passed" and receipt["inputs_unchanged"] is True
                and not receipt["cleanup_errors"], "sealed successful receipt required")
        for name, expected in receipt["inputs"].items():
            key = canonical(name)
            if key in omitted:
                require(omitted[key] == expected, "declared binary digest differs")
                omitted_guards += 1
            else:
                require(digest(get(name)) == expected, "replayed source/input guard "+key)
                checked_guards += 1
        for name, expected in receipt.get("saved_files", receipt.get("outputs", {})).items():
            key = canonical(name)
            if key in omitted:
                require(omitted[key] == expected, "declared saved binary digest differs")
            else:
                require(digest(get(name)) == expected, "saved output guard "+key)
    for name in manifest["independent_reviews"]:
        require(str(json.loads(get(name))["status"]).startswith("passed"), "independent saved review gate "+name)

    # This is a transport adapter only. It feeds the exact, previously reviewed
    # comparator bytes the same original logical paths without extracting or
    # executing any captured Rust, producer or original audit script.
    replay_output = {}

    class SavedPath:
        def __init__(self, path):
            self.name = str(path)

        def __str__(self):
            return self.name

        def __truediv__(self, other):
            return SavedPath(str(PurePosixPath(self.name)/str(other)))

        def read_text(self):
            return get(self.name).decode()

        def read_bytes(self):
            return get(self.name)

        def exists(self):
            return canonical(self.name) in data or self.name in replay_output

        def write_text(self, value):
            require(self.name == "/capsule-replay/comparison.json", "only isolated replay output allowed")
            require(self.name not in replay_output, "preserve replay output")
            replay_output[self.name] = value

    comparator = manifest["comparator"]
    namespace = {"__name__":"tirust_capsule_saved_comparison", "__file__":original_root+"/"+comparator}
    exec(compile(get(comparator), "<frozen-saved-comparator>", "exec"), namespace)
    namespace["Path"] = SavedPath
    namespace["ROOT"] = SavedPath(original_root)
    with redirect_stdout(io.StringIO()):
        code = namespace["main"](original_root+"/"+manifest["captures"]["128"],
                                 original_root+"/"+manifest["captures"]["256"], "/capsule-replay/comparison.json")
    replay = json.loads(replay_output["/capsule-replay/comparison.json"])
    original = json.loads(get(manifest["comparison"]))
    require(code == 0 and replay == original, "complete frozen numerical comparison replay")
    print(json.dumps({"status":"passed", "source_files":len(manifest["source_files"]),
        "payload_members":len(manifest["payload_members"]), "replayed_guard_bindings":checked_guards,
        "omitted_compiled_binary_guard_occurrences":omitted_guards,
        "independent_reviews_preserved":len(manifest["independent_reviews"]), "counts":replay["counts"],
        "new_integrals":0, "new_compilers":0, "current_host_process_absence_claim":False}))


if __name__ == "__main__":
    main()
