use std::{
    path::{Path, PathBuf},
    process::Command,
};

pub(crate) fn git_metadata_paths(directory: &Path) -> Vec<PathBuf> {
    ["HEAD", "refs", "packed-refs"]
        .into_iter()
        .filter_map(|entry| {
            let output = Command::new("git")
                .current_dir(directory)
                .args(["rev-parse", "--path-format=absolute", "--git-path", entry])
                .output()
                .ok()?;
            if !output.status.success() {
                return None;
            }
            let path = PathBuf::from(String::from_utf8(output.stdout).ok()?.trim());
            path.exists().then_some(path)
        })
        .collect()
}

fn get_git_version() -> Option<String> {
    let output = Command::new("git")
        .args(["describe", "--tags", "--always"])
        .output()
        .ok()?;

    if output.status.success() {
        let git_desc = String::from_utf8(output.stdout).ok()?;
        Some(git_desc.trim().to_string())
    } else {
        None
    }
}

fn main() {
    let cargo_version = std::env::var("CARGO_PKG_VERSION").unwrap();

    // A vendored source snapshot must not inherit its embedding project's
    // Git description. The explicit file identifies its upstream and patch.
    let version = std::fs::read_to_string("IREGI_UPSTREAM_VERSION")
        .ok()
        .map(|value| value.trim().to_owned())
        .filter(|value| !value.is_empty())
        .unwrap_or_else(|| {
            // Only the Git fallback depends on the embedding repository.
            for path in git_metadata_paths(Path::new(".")) {
                println!("cargo:rerun-if-changed={}", path.display());
            }
            get_git_version().unwrap_or(cargo_version)
        });
    println!("cargo:rerun-if-changed=IREGI_UPSTREAM_VERSION");

    println!("cargo:rustc-env=SYMBOLICA_VERSION=symbolica-{}", version);
    println!("cargo:rerun-if-changed=build.rs");
}
