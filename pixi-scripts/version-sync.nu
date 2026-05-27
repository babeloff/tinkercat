#!/usr/bin/env nu
# Propagate the canonical version from pixi.toml to all files that replicate it.
#
# pixi.toml is the single source of truth.  The following files are updated:
#
#   recipes/recipe.yaml          conda_version and gradle_version context vars
#   build.gradle.kts             Kotlin project version + embedded package.json
#   python/tinkercat/__init__.py  Python __version__ string
#
# Gradle artifacts carry a "-SNAPSHOT" suffix; the conda/Python packages use
# the bare X.Y.Z form.
#
# Requires: toml-cli (pip), yq (conda-forge)
#
# Usage:
#   nu pixi-scripts/version-sync.nu
#   pixi run version-sync

def main [] {
    let version  = (open pixi.toml | get workspace.version)
    let snapshot = ($version + "-SNAPSHOT")

    print $"── Syncing project version to ($version) ───────────────────────────"

    # ── recipes/recipe.yaml ── yq: syntax-aware YAML editing, preserves comments
    ^yq e $".context.conda_version = \"($version)\""  -i recipes/recipe.yaml
    ^yq e $".context.gradle_version = \"($snapshot)\"" -i recipes/recipe.yaml
    print "  ✓ recipes/recipe.yaml"

    # ── build.gradle.kts ── no Kotlin DSL parser available; targeted regex on
    # two known patterns: the top-level `version =` assignment and the embedded
    # package.json literal string.
    let gradle_path     = "build.gradle.kts"
    let gradle_ver_pat  = '(?m)^version = "\d+\.\d+\.\d+(-SNAPSHOT)?"'
    let gradle_json_pat = '"version": "\d+\.\d+\.\d+(-SNAPSHOT)?"'
    open --raw $gradle_path
        | str replace --regex $gradle_ver_pat  ("version = \"" + $snapshot + "\"")
        | str replace --regex $gradle_json_pat ("\"version\": \"" + $snapshot + "\"")
        | save --force $gradle_path
    print $"  ✓ ($gradle_path)"

    # ── python/tinkercat/__init__.py ── no Python AST round-trip writer available;
    # targeted regex on the single `__version__` assignment.
    let python_path    = "python/tinkercat/__init__.py"
    let python_ver_pat = '__version__ = "\d+\.\d+\.\d+"'
    open --raw $python_path
        | str replace --regex $python_ver_pat ("__version__ = \"" + $version + "\"")
        | save --force $python_path
    print $"  ✓ ($python_path)"

    print $"── Done  version=($version)  gradle=($snapshot) ───────────────────"
}
