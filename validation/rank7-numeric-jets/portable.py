"""Small saved-byte transport shared by the N2 capsule packager/checker."""
from pathlib import Path, PurePosixPath
import gzip
import hashlib
import importlib.util
import io
import json
import sys
import tarfile

sys.dont_write_bytecode = True
ROOT_ID = "/shared/external/iregi/iregi-rust/"
PREFIX = "target/rank7-numeric-jets-execution"
SOURCE_PARENT = "validation/public-rank7-ibp-n2-postfix"
SOURCE_PARENT_SHA = "a53da3c6f8af203c3bf486a7313f26ed0a0e547dad061d35d7c41cfd3d25dceb"
QUAD_PARENT = "validation/quad-original-iregi-generalized-rank7"
QUAD_PARENT_SHA = "ccda92bdd0be40484b2d8762d479658ada0beb98eb610df7c96b44f7f521a0b0"
INITIAL_AUDIT = "d183d6df7305a7529aee47c29b142c9877c40608ba3226ab411fb83633dc9658"
BEYOND_AUDIT = "e568eb842d56c48f63ddeb0296338ba1bd63dd6a8f2411adbb6b0be587cecb54"
MUTATION_AUDIT = "a5bc5cfff7620b922f4dca65d9ce4d8cf3355b52d96cda62e17323ac9b46db50"
INITIAL_REPLAY = "c572e9696d903e88890379a257585aabd2050ba3d549f79313296bdfb59a005a"
BEYOND_REPLAY = "c33ac0b516194541b1e3af713ecdccf02c727171a10d84a390f52837443af918"
CASES = ["plain-f64","plain-dd","first-float128","first-float256","mixed-float128","mixed-float256",
         "dot0-float128","dot0-float256","triple0-float128","triple0-float256","fd-float384"]
BEYOND_CASES = ["f64-rejection","beyond-dd","beyond-float128","beyond-float256"]
CODE = ["package.py","check.py","portable.py","initial_replay.py","beyond_replay.py","README.md"]
NATIVE_SUFFIXES={".rlib",".rmeta",".so",".a",".o",".dylib",".dll",".exe"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def describe(body):
    return dict(sha256=digest(body),bytes=len(body))


def plain_saved_file(path):
    """Read selected source/text evidence, rejecting native/archive products first."""
    path=Path(path)
    require(path.is_file() and not path.is_symlink() and path.suffix not in NATIVE_SUFFIXES,
            "unsafe/native saved file: "+str(path))
    with path.open("rb") as stream:
        head=stream.read(8)
        require(not any(head.startswith(magic) for magic in [b"\x7fELF",b"!<arch>\n",b"\x1f\x8b",b"PK\x03\x04",b"MZ"]),
                "native/archive product cannot enter text evidence payload: "+str(path))
        return head+stream.read()


def document(body):
    def pairs(items):
        value = {}
        for key,item in items:
            require(key not in value,"duplicate JSON key")
            value[key] = item
        return value
    def invalid(value):
        raise ValueError("nonfinite JSON token "+value)
    return json.loads(body,object_pairs_hook=pairs,parse_float=str,parse_constant=invalid)


def normalized(name):
    if name.startswith(ROOT_ID):
        name = name[len(ROOT_ID):]
    path = PurePosixPath(name)
    require(str(path)==name and name and not path.is_absolute() and ".." not in path.parts,
            "unsafe nominal project alias: "+name)
    return name


def archive_bytes(entries):
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw,mode="wb",mtime=0,filename="") as compressed:
        with tarfile.open(fileobj=compressed,mode="w") as archive:
            for name,body in sorted(entries.items()):
                normalized(name)
                info = tarfile.TarInfo(name)
                info.size=len(body);info.mode=0o644;info.mtime=0
                archive.addfile(info,io.BytesIO(body))
    return raw.getvalue()


def unpack(body,expected):
    result = {}
    with tarfile.open(fileobj=io.BytesIO(body),mode="r:gz") as archive:
        for member in archive:
            normalized(member.name)
            require(member.isfile() and member.name not in result,"unsafe/duplicate archive member")
            content = archive.extractfile(member).read()
            require(member.name in expected and describe(content)==expected[member.name],"archive member descriptor mismatch")
            result[member.name] = content
    require(set(result)==set(expected),"closed archive inventory mismatch")
    return result


def import_checked(path,expected,label):
    path = Path(path)
    require(digest(path.read_bytes())==expected,"reviewed saved-only module changed: "+str(path))
    spec = importlib.util.spec_from_file_location(label,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_parents(root,expected=None):
    """Restore one committed source parent, borrow the exact quad payload.

    No old checker numerical replay is invoked. No compiled/native artifact or
    transitive source/dependency tree is accessed. Parent files stay in their
    committed capsules and are pinned individually for relocation.
    """
    root = Path(root)
    source_manifest_path = root/SOURCE_PARENT/"manifest.json"
    quad_manifest_path = root/QUAD_PARENT/"manifest.json"
    source_body,quad_body = source_manifest_path.read_bytes(),quad_manifest_path.read_bytes()
    require(digest(source_body)==SOURCE_PARENT_SHA and digest(quad_body)==QUAD_PARENT_SHA,"committed parent manifest changed")
    sm,qm = document(source_body),document(quad_body)
    pins = {SOURCE_PARENT+"/manifest.json":describe(source_body),QUAD_PARENT+"/manifest.json":describe(quad_body)}
    for name,sha in sm["capsule_files"].items():
        body=(root/SOURCE_PARENT/name).read_bytes()
        require(digest(body)==sha,"source parent capsule changed")
        pins[SOURCE_PARENT+"/"+name]=describe(body)
    # These are the directly used committed quad parent files, not a request to
    # recursively package or rehash its historical build/dependency closure.
    for name in ["payload.tar.gz","check.py","qualification.json"]:
        body=(root/QUAD_PARENT/name).read_bytes()
        require(describe(body)==qm["capsule_files"][name],"quad parent capsule changed")
        pins[QUAD_PARENT+"/"+name]=describe(body)
    adjacent = "validation/quad-original-iregi-generalized-rank7-independent-copy-review.json"
    body = (root/adjacent).read_bytes()
    require(digest(body)=="1d804b0e13eff3136f1c7fac6733e5a5512a3eb655e70a9eee4bb4764424ccc4","quad parent independent copy review changed")
    pins[adjacent]=describe(body)
    if expected is not None:
        require(pins==expected,"closed committed-parent file inventory changed")
    parent = import_checked(root/SOURCE_PARENT/"check.py",sm["capsule_files"]["check.py"],"_n2_source_parent_restore")
    sources = parent.restore_files(sm)
    borrowed = {name:(root/name).read_bytes() for name in pins}
    # Expose exact selected archived quad aliases required by saved guard maps.
    selected = {"target/quad-generalized-rank7-anchors/protocol.json"}
    selected.update("target/quad-generalized-rank7-anchors/capture-001/request-"+str(i)+".stdout" for i in [0,2,4])
    seen=set()
    with tarfile.open(fileobj=io.BytesIO(borrowed[QUAD_PARENT+"/payload.tar.gz"]),mode="r:gz") as archive:
        for member in archive:
            normalized(member.name)
            require(member.isfile() and member.name not in seen and member.name in qm["payload_members"],
                    "unsafe/extra committed quad member")
            require(member.size==qm["payload_members"][member.name]["bytes"],"quad member length changed")
            seen.add(member.name)
            if member.name in selected:
                require(member.isfile(),"quad selected alias is not a file")
                body=archive.extractfile(member).read()
                require(describe(body)==qm["payload_members"][member.name],"selected quad member changed")
                borrowed[member.name]=body
    require(seen==set(qm["payload_members"]),"closed committed quad payload inventory differs")
    require(selected<=borrowed.keys(),"selected quad aliases incomplete")
    return pins,sources,borrowed


def materialize(manifest,blobs,parent_sources,borrowed):
    files = dict(borrowed)
    def value(entry):
        if entry["origin"]=="payload":
            body=blobs["blobs/"+entry["sha256"]]
        elif entry["origin"]=="source_parent":
            body=parent_sources[entry["key"]]
        elif entry["origin"]=="committed_parent":
            body=borrowed[entry["key"]]
        else:
            raise ValueError("unknown byte origin")
        require(describe(body)=={k:entry[k] for k in ["sha256","bytes"]},"alias descriptor/body mismatch")
        return body
    for name,entry in manifest["aliases"].items():
        normalized(name)
        body=value(entry)
        require(name not in files or files[name]==body,"conflicting inherited alias")
        files[name]=body
    for context,source_set in manifest["source_sets"].items():
        require(context in ["build-001","build-002"] and len(source_set)==71,"exact source snapshot envelope")
        for name,entry in source_set.items():
            normalized(name)
            alias=PREFIX+"/"+context+"/source-snapshot/"+name
            body=value(entry)
            require(alias in files and files[alias]==body,"source snapshot alias does not match context")
    return files,value
