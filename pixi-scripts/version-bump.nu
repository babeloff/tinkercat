#!/usr/bin/env nu
# Bump the patch component of the project version, then sync all files.
#
# The version in pixi.toml (workspace.version, X.Y.Z) is the canonical source.
# After bumping, version-sync.nu propagates the new value to every file
# that replicates it.
#
# Requires: toml-cli (pip), yq (conda-forge)
#
# Examples:
#   nu pixi-scripts/version-bump.nu
#   pixi run version-bump

def main [] {
    let current = (open pixi.toml | get workspace.version)

    let parts = ($current | split row ".")
    if ($parts | length) != 3 {
        error make { msg: $"Cannot parse version \"($current)\" — expected X.Y.Z" }
    }

    let major = ($parts | get 0 | into int)
    let minor = ($parts | get 1 | into int)
    let patch = ($parts | get 2 | into int)
    let next  = ($major | into string) + "." + ($minor | into string) + "." + (($patch + 1) | into string)

    print $"── Bumping version ($current) → ($next) ────────────────────────────"

    # toml-cli edits pixi.toml in-place and produces no stdout output.
    ^toml set --toml-path pixi.toml workspace.version $next
    print "  ✓ pixi.toml"

    nu pixi-scripts/version-sync.nu
}
