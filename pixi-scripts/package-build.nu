#!/usr/bin/env nu
# Build all TinkerCat conda packages using rattler-build.
#
# All outputs defined in recipes/recipe.yaml are built in a single
# rattler-build invocation (rattler-build has no per-output selector).
#
# Examples:
#   nu pixi-scripts/package-build.nu
#   nu pixi-scripts/package-build.nu --output-dir /tmp/pkgs

def main [
    --output-dir: string = "build/conda-packages"  # Destination for built packages
    --no-clean                                      # Skip removing stale packages before build
] {
    print "── Building all TinkerCat packages ─────────────────────────────────"

    # Remove stale conda packages so rattler-build's channel repodata never
    # sees an old file with the same filename but different content hash.
    if not $no_clean {
        if ($output_dir | path exists) {
            print $"── Removing stale packages in ($output_dir) ────────────────────────"
            rm -rf $output_dir
        }
    }

    rattler-build build --recipe recipes/recipe.yaml --output-dir $output_dir
    print $"✓ Packages written to ($output_dir)"
}
