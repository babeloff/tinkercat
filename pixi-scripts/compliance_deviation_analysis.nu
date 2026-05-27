#!/usr/bin/env nu
# TinkerPop Compliance Test Deviation Analysis
#
# Compares upstream Apache TinkerPop compliance tests with local TinkerCat
# compliance tests and generates a deviation report.
#
# Usage (via pixi):
#   pixi run compliance
#   pixi run compliance -- --format html
#   pixi run compliance -- --download
#   pixi run compliance -- --format json --output path/to/report.json

# ── utilities ─────────────────────────────────────────────────────────────────

def find-project-root [start: string]: nothing -> string {
    mut current = ($start | path expand)
    loop {
        if ($current | path join "build.gradle.kts" | path exists) {
            return $current
        }
        let parent = ($current | path dirname)
        if $parent == $current { return $start }
        $current = $parent
    }
}

# Return the first regex capture group from $in, or fallback if no match.
def extract-first [pattern: string, fallback: string = ""]: string -> string {
    let matches = ($in | parse --regex $pattern)
    if ($matches | is-empty) { $fallback } else { $matches | first | get capture0 }
}

# Return the first element of $in, or fallback if the list is empty.
def first-or [fallback: any]: list -> any {
    if ($in | is-empty) { $fallback } else { $in | first }
}

def priority-rank []: string -> int {
    match $in {
        "CRITICAL" => 0
        "HIGH"     => 1
        "MEDIUM"   => 2
        "LOW"      => 3
        _          => 4
    }
}

def priority-emoji []: string -> string {
    match $in {
        "CRITICAL" => "🚨"
        "HIGH"     => "⚠️"
        "MEDIUM"   => "📝"
        _          => "ℹ️"
    }
}

# ── file parsers ──────────────────────────────────────────────────────────────

# Parse a Java source file and return {name, file_path, package, methods}.
# methods is a list of {name, class_name, file_path, line}.
def parse-java-tests [file_path: string]: nothing -> record {
    let content = try { open --raw $file_path } catch { "" }
    let lines = $content | lines

    let package = (
        $lines
        | where { $in =~ 'package\s+[\w.]+\s*;' }
        | first-or ""
        | extract-first 'package\s+([\w.]+)\s*;'
    )

    let cls_lines = $lines | where { $in =~ 'public\s+class\s+\w+' }
    let class_name = if ($cls_lines | is-not-empty) {
        $cls_lines | first | extract-first 'public\s+class\s+(\w+)' ($file_path | path basename | str replace --all '.java' '')
    } else {
        $file_path | path basename | str replace --all '.java' ''
    }

    let indexed = $lines | enumerate
    let methods = $indexed | each { |row|
        if ($row.item | str trim | str starts-with "@Test") {
            let ahead = $indexed
                | where { $in.index > $row.index and $in.index <= ($row.index + 5) }
                | get item
            let method_lines = $ahead | where { $in =~ '\bvoid\s+\w+\s*\(' }
            if ($method_lines | is-not-empty) {
                let name = ($method_lines | first | extract-first '\bvoid\s+(\w+)\s*\(')
                if ($name | is-not-empty) {
                    {name: $name, class_name: $class_name, file_path: $file_path, line: $row.index}
                }
            }
        }
    } | compact

    {name: $class_name, file_path: $file_path, package: $package, methods: $methods}
}

# Parse a Kotlin source file and return the same structure as parse-java-tests.
def parse-kotlin-tests [file_path: string]: nothing -> record {
    let content = try { open --raw $file_path } catch { "" }
    let lines = $content | lines

    let package = (
        $lines
        | where { $in =~ 'package\s+[\w.]+' }
        | first-or ""
        | extract-first 'package\s+([\w.]+)'
    )

    let cls_lines = $lines | where { $in =~ '\bclass\s+\w+' }
    let class_name = if ($cls_lines | is-not-empty) {
        $cls_lines | first | extract-first '\bclass\s+(\w+)' ($file_path | path basename | str replace --all '.kt' '')
    } else {
        $file_path | path basename | str replace --all '.kt' ''
    }

    let indexed = $lines | enumerate
    let methods = $indexed | each { |row|
        if ($row.item | str trim | str starts-with "@Test") {
            let ahead = $indexed
                | where { $in.index > $row.index and $in.index <= ($row.index + 5) }
                | get item
            # Kotlin test functions may use backtick-quoted names
            let method_lines = $ahead | where { $in =~ '\bfun\s+`?[\w ]+`?\s*\(' }
            if ($method_lines | is-not-empty) {
                let name = ($method_lines | first | extract-first '\bfun\s+`?([\w ]+)`?\s*\(')
                if ($name | is-not-empty) {
                    {name: ($name | str trim), class_name: $class_name, file_path: $file_path, line: $row.index}
                }
            }
        }
    } | compact

    {name: $class_name, file_path: $file_path, package: $package, methods: $methods}
}

# Parse a Python test file.
def parse-python-tests [file_path: string]: nothing -> record {
    let content = try { open --raw $file_path } catch { "" }
    let lines = $content | lines

    let cls_lines = $lines | where { $in =~ '^\s*class\s+\w+' }
    let class_name = if ($cls_lines | is-not-empty) {
        $cls_lines | first | extract-first 'class\s+(\w+)' ($file_path | path basename | str replace --all '.py' '')
    } else {
        $file_path | path basename | str replace --all '.py' ''
    }

    let methods = $lines | enumerate | each { |row|
        if ($row.item =~ '^\s*def\s+test_\w+\s*\(') {
            let name = ($row.item | extract-first '\bdef\s+(test_\w+)\s*\(')
            if ($name | is-not-empty) {
                {name: $name, class_name: $class_name, file_path: $file_path, line: $row.index}
            }
        }
    } | compact

    {name: $class_name, file_path: $file_path, package: "", methods: $methods}
}

# ── file discovery ────────────────────────────────────────────────────────────

# Walk a directory for test files of a given extension and parse them.
# Returns a list of {key, class} records (key = "package.ClassName").
def collect-tests [dir: string, ext: string, parse_cmd: string]: nothing -> list<record> {
    if not ($dir | path exists) { return [] }
    let pattern = $"($dir)/**/*.($ext)"
    try {
        glob $pattern
        | where { |p|
            let base = ($p | path basename)
            ($base | str contains --ignore-case "compliance")
            or ($base | str contains --ignore-case "test")
        }
        | each { |p|
            let tc = if $parse_cmd == "java" {
                parse-java-tests ($p | into string)
            } else if $parse_cmd == "kotlin" {
                parse-kotlin-tests ($p | into string)
            } else {
                parse-python-tests ($p | into string)
            }
            if ($tc.methods | length) > 0 {
                let key = if ($tc.package | is-not-empty) {
                    $"($tc.package).($tc.name)"
                } else { $tc.name }
                {key: $key, class: $tc}
            }
        }
        | compact
    } catch { [] }
}

# ── download ──────────────────────────────────────────────────────────────────

def download-upstream-tests [cache_dir: string]: nothing -> bool {
    print "📥 Downloading upstream Apache TinkerPop tests..."
    let url = "https://github.com/apache/tinkerpop/archive/refs/heads/master.zip"
    let zip_path = $cache_dir | path join "tinkerpop-master.zip"
    let extract_dir = $cache_dir | path join "extracted"

    mkdir $cache_dir
    print $"   Fetching ($url)..."
    try {
        http get --raw $url | save --force $zip_path
        mkdir $extract_dir
        ^unzip -q -o $zip_path -d $extract_dir
        print "✅ Upstream tests downloaded and extracted"
        true
    } catch { |e|
        print $"❌ Download failed: ($e.msg)"
        false
    }
}

# ── analysis ──────────────────────────────────────────────────────────────────

def analyze-upstream-tests [cache_dir: string]: nothing -> list<record> {
    print "🔍 Analyzing upstream Apache TinkerPop tests..."
    let extract_dir = $cache_dir | path join "extracted"

    if not ($extract_dir | path exists) {
        print "❌ Upstream tests not found. Run with --download first."
        return []
    }

    let patterns = [
        $"($extract_dir)/**/gremlin-test/src/main/**/*Test*.java"
        $"($extract_dir)/**/gremlin-core/src/test/**/*.java"
        $"($extract_dir)/**/*Structure*Test*.java"
        $"($extract_dir)/**/*Process*Test*.java"
        $"($extract_dir)/**/*Compliance*.java"
    ]

    let classes = $patterns | each { |pattern|
        try {
            glob $pattern | each { |p|
                let tc = parse-java-tests ($p | into string)
                if ($tc.methods | length) > 0 {
                    let key = if ($tc.package | is-not-empty) {
                        $"($tc.package).($tc.name)"
                    } else { $tc.name }
                    print $"   upstream: ($key) \(($tc.methods | length) methods\)"
                    {key: $key, class: $tc}
                }
            } | compact
        } catch { [] }
    } | flatten

    print $"✅ ($classes | length) upstream test classes"
    $classes
}

def analyze-local-tests [project_root: string]: nothing -> list<record> {
    print "🔍 Analyzing local TinkerCat compliance tests..."
    mut results = []

    for dir in [
        ($project_root | path join "src" "jvmCompliance" "java")
        ($project_root | path join "src" "jvmTest" "java")
        ($project_root | path join "src" "test" "java")
    ] {
        let found = collect-tests $dir "java" "java"
        for item in $found { print $"   Java: ($item.key) \(($item.class.methods | length) methods\)" }
        $results = $results | append $found
    }

    for dir in [
        ($project_root | path join "src" "jvmTest" "kotlin")
        ($project_root | path join "src" "jsTest" "kotlin")
        ($project_root | path join "src" "nativeTest" "kotlin")
        ($project_root | path join "src" "commonTest" "kotlin")
    ] {
        let found = collect-tests $dir "kt" "kotlin"
        for item in $found { print $"   Kotlin: ($item.key) \(($item.class.methods | length) methods\)" }
        $results = $results | append $found
    }

    let py_dir = $project_root | path join "python" "tests"
    if ($py_dir | path exists) {
        let found = try {
            glob $"($py_dir)/**/*.py"
            | where { |p|
                let base = ($p | path basename)
                ($base | str starts-with "test_") or ($base | str contains --ignore-case "compliance")
            }
            | each { |p|
                let tc = parse-python-tests ($p | into string)
                if ($tc.methods | length) > 0 {
                    let key = $"python.($tc.name)"
                    print $"   Python: ($key) \(($tc.methods | length) methods\)"
                    {key: $key, class: $tc}
                }
            } | compact
        } catch { [] }
        $results = $results | append $found
    }

    print $"✅ ($results | length) local test classes"
    $results
}

# ── comparison ────────────────────────────────────────────────────────────────

def flatten-methods [classes: list<record>]: nothing -> list<string> {
    $classes | each { |entry|
        $entry.class.methods | each { |m| $"($entry.key).($m.name)" }
    } | flatten
}

def categorize-missing [missing: list<string>]: nothing -> list<record> {
    let defs = [
        {name: "Structure API",      pattern: "structure",  priority: "CRITICAL", description: "Core Graph Structure API compliance tests"}
        {name: "Process API",        pattern: "process",    priority: "CRITICAL", description: "Graph traversal and processing API tests"}
        {name: "TinkerCat Specific", pattern: "tinkercat",  priority: "HIGH",     description: "TinkerCat implementation specific tests"}
        {name: "Algorithm",          pattern: "algorithm",  priority: "MEDIUM",   description: "Graph algorithm implementation tests"}
        {name: "Scripting JSR223",   pattern: "jsr223",     priority: "MEDIUM",   description: "Scripting engine and language binding tests"}
        {name: "Utilities",          pattern: "util",       priority: "LOW",      description: "Utility classes and helper tests"}
    ]

    let categorized = $defs | each { |cat|
        let matched = $missing | where { ($in | str downcase) | str contains $cat.pattern }
        {name: $cat.name, priority: $cat.priority, description: $cat.description, count: ($matched | length), tests: $matched}
    }

    let already_matched = $categorized | each { |c| $c.tests } | flatten
    let other = $missing | where { |t| not ($already_matched | any { $in == $t }) }

    $categorized | append {
        name: "Other"
        priority: "LOW"
        description: "Uncategorized tests"
        count: ($other | length)
        tests: $other
    }
}

def compare-tests [upstream: list<record>, local: list<record>]: nothing -> record {
    print "📊 Comparing upstream vs local tests..."

    let up_methods  = flatten-methods $upstream
    let loc_methods = flatten-methods $local

    let missing = $up_methods  | where { |m| not ($loc_methods | any { $in == $m }) }
    let extra   = $loc_methods | where { |m| not ($up_methods  | any { $in == $m }) }

    let total_up     = $up_methods | length
    let common_count = $up_methods | where { |m| $loc_methods | any { $in == $m } } | length
    let coverage_pct = if $total_up > 0 { ($common_count / $total_up) * 100.0 } else { 0.0 }

    {
        timestamp:        (date now | format date '%Y-%m-%dT%H:%M:%S')
        upstream_classes: $upstream
        local_classes:    $local
        missing:          $missing
        extra:            $extra
        categories:       (categorize-missing $missing)
        coverage: {
            total_upstream: $total_up
            total_local:    ($loc_methods | length)
            matching:       $common_count
            pct:            $coverage_pct
        }
    }
}

# ── recommendations ───────────────────────────────────────────────────────────

def make-recommendations [report: record]: nothing -> list<string> {
    let pct = $report.coverage.pct
    let pct_r = $pct | math round --precision 1

    mut recs = []

    $recs = $recs | append (if $pct < 10 {
        $"🚨 CRITICAL: Coverage is only ($pct_r)%%. Immediate action required."
    } else if $pct < 50 {
        $"⚠️  WARNING: Coverage is ($pct_r)%%. Major compliance gaps."
    } else if $pct < 80 {
        $"📈 PROGRESS: Coverage is ($pct_r)%%. Continue implementing missing tests."
    } else {
        $"✅ EXCELLENT: Coverage is ($pct_r)%%. Focus on remaining edge cases."
    })

    let critical = $report.categories | where { $in.priority == "CRITICAL" and $in.count > 0 }
    if ($critical | is-not-empty) {
        let names = $critical | get name | str join ", "
        $recs = $recs | append $"🚨 CRITICAL MISSING: ($names) — foundational TinkerPop APIs."
    }

    let sorted_cats = $report.categories
        | where { $in.count > 0 }
        | sort-by { |c| $c.priority | priority-rank }
    for cat in $sorted_cats {
        let emoji = $cat.priority | priority-emoji
        $recs = $recs | append $"($emoji) ($cat.priority): ($cat.name) — ($cat.count) missing tests. ($cat.description)"
    }

    let n = $report.missing | length
    if $n > 2000 {
        $recs = $recs | append $"📋 MASSIVE GAP: ($n) missing tests. Estimated 8–12 weeks of work."
    } else if $n > 500 {
        $recs = $recs | append $"📋 LARGE GAP: ($n) missing tests. Plan multi-phase approach."
    } else if $n > 50 {
        $recs = $recs | append $"📝 MEDIUM GAP: ($n) missing tests. Schedule for next cycle."
    } else if $n > 0 {
        $recs = $recs | append $"✏️  SMALL GAP: ($n) missing tests. Consider implementing."
    }

    let extra_n = $report.extra | length
    if $extra_n > 0 {
        $recs = $recs | append $"🎯 LOCAL EXTENSIONS: ($extra_n) tests beyond upstream — review value."
    }

    let struct_n  = $report.missing | where { ($in | str downcase) | str contains "structure" } | length
    let process_n = $report.missing | where { ($in | str downcase) | str contains "process"   } | length
    if $struct_n  > 0 { $recs = $recs | append $"🏗️  STRUCTURE API: ($struct_n) missing tests." }
    if $process_n > 0 { $recs = $recs | append $"⚙️  PROCESS API: ($process_n) missing tests." }

    $recs
}

# ── AsciiDoc report ───────────────────────────────────────────────────────────

def adoc-status [pct: float]: nothing -> string {
    if $pct < 70 { "🚨 CRITICAL DEVIATIONS" } else if $pct < 90 { "⚠️ MINOR DEVIATIONS" } else { "✅ GOOD ALIGNMENT" }
}

def generate-adoc [report: record, recs: list<string>]: nothing -> string {
    let pct   = $report.coverage.pct
    let pct_r = $pct | math round --precision 1
    let n_mis = $report.missing | length
    let n_ext = $report.extra   | length
    let n_up  = $report.coverage.total_upstream
    let n_loc = $report.coverage.total_local
    let n_mat = $report.coverage.matching

    let cov_status = if $pct >= 90 { "✅ Good" } else if $pct >= 70 { "⚠️ Needs Improvement" } else { "🚨 Critical" }
    let loc_status = if $n_loc >= $n_up { "✅" } else { "⚠️" }
    let mis_status = if $n_mis == 0 { "✅ None" } else { "⚠️ Review Required" }
    let ext_status = if $n_ext == 0 { "✅ Aligned" } else { "ℹ️ Additional Coverage" }

    mut doc = [
        "= TinkerPop Compliance Test Deviation Analysis Report"
        ":toc:"
        ":toclevels: 3"
        ":sectanchors:"
        ":sectlinks:"
        ""
        "== Executive Summary"
        ""
        $"*Analysis Date:* ($report.timestamp) +"
        $"*Report Status:* (adoc-status $pct) +"
        $"*Coverage Level:* ($pct_r)%%"
        ""
        "This report analyzes the deviation between upstream Apache TinkerPop compliance tests and local TinkerCat compliance test implementations."
        ""
        "== Coverage Analysis"
        ""
        "[cols=\"2,1,3\"]"
        "|==="
        "| Metric | Value | Status"
        ""
        "| Total Upstream Tests"
        $"| ($n_up)"
        "| Baseline"
        ""
        "| Total Local Tests"
        $"| ($n_loc)"
        $"| ($loc_status)"
        ""
        "| Matching Tests"
        $"| ($n_mat)"
        "| Implementation"
        ""
        "| Coverage Percentage"
        $"| ($pct_r)%%"
        $"| ($cov_status)"
        ""
        "| Missing Tests"
        $"| ($n_mis)"
        $"| ($mis_status)"
        ""
        "| Extra Tests"
        $"| ($n_ext)"
        $"| ($ext_status)"
        "|==="
        ""
        "== Missing Tests Analysis"
        ""
        (if $n_mis > 0 { $"⚠️ *($n_mis) tests are missing from local implementation:*" } else { "✅ *No missing tests detected.*" })
        ""
    ] | str join "\n"

    if $n_mis > 0 {
        $doc = $doc + "=== Missing Tests by Category\n\n"
        for priority in ["CRITICAL" "HIGH" "MEDIUM" "LOW"] {
            let cats = $report.categories | where { $in.priority == $priority and $in.count > 0 }
            if ($cats | is-not-empty) {
                let emoji = $priority | priority-emoji
                $doc = $doc + $"*($emoji) ($priority) Priority Tests:*\n\n"
                for cat in $cats {
                    $doc = $doc + $"* *($cat.name)* \(($cat.count) tests\)\n"
                    $doc = $doc + $"  - ($cat.description)\n"
                    let show_n = [$cat.count 5] | math min
                    for t in ($cat.tests | first $show_n) { $doc = $doc + $"  - `($t)`\n" }
                    if $cat.count > 5 { $doc = $doc + $"  - ... and ($cat.count - 5) more\n" }
                    $doc = $doc + "\n"
                }
            }
        }
    }

    $doc = $doc + "== Implementation Recommendations\n\n"
    for rec in $recs { $doc = $doc + $"* ($rec)\n" }
    $doc = $doc + "\n"

    # Priority matrix
    $doc = $doc + "=== Implementation Priority Matrix\n\n[cols=\"2,1,1,2\"]\n|===\n| Category | Priority | Missing Tests | Effort\n\n"
    for priority in ["CRITICAL" "HIGH" "MEDIUM" "LOW"] {
        let cats = $report.categories | where { $in.priority == $priority and $in.count > 0 }
        for cat in $cats {
            let effort = match $priority {
                "CRITICAL" => "🔥 Urgent"
                "HIGH"     => "⚡ High"
                "MEDIUM"   => "📅 Medium"
                _          => "🕐 Low"
            }
            $doc = $doc + $"| ($cat.name)\n| ($priority)\n| ($cat.count)\n| ($effort)\n\n"
        }
    }
    $doc = $doc + "|===\n\n"

    # Extra tests
    $doc = $doc + $"== Extra Tests Analysis\n\n"
    $doc = $doc + (if $n_ext > 0 { $"ℹ️ *($n_ext) additional tests found in local implementation:*\n\n" } else { "✅ *No extra tests beyond upstream.*\n\n" })
    if $n_ext > 0 {
        $doc = $doc + "=== Additional Local Tests\n\n"
        let show_n = [$n_ext 20] | math min
        for t in ($report.extra | sort | first $show_n) { $doc = $doc + $"* `($t)`\n" }
        if $n_ext > 20 { $doc = $doc + $"* ... and ($n_ext - 20) more\n" }
        $doc = $doc + "\n"
    }

    # Class tables
    let up_classes  = $report.upstream_classes
    let loc_classes = $report.local_classes
    let show_up  = [($up_classes  | length) 15] | math min
    let show_loc = [($loc_classes | length) 15] | math min

    $doc = $doc + "== Test Class Analysis\n\n=== Upstream Test Classes\n\n[cols=\"3,1,4\"]\n|===\n| Class | Methods | Package\n\n"
    for entry in ($up_classes | first $show_up) {
        $doc = $doc + $"| `($entry.class.name)`\n| ($entry.class.methods | length)\n| `($entry.class.package)`\n\n"
    }
    $doc = $doc + "|===\n\n"
    if ($up_classes | length) > 15 { $doc = $doc + $"_And ($($up_classes | length) - 15) more upstream classes..._\n\n" }

    $doc = $doc + "=== Local Test Classes\n\n[cols=\"3,1,4\"]\n|===\n| Class | Methods | Package\n\n"
    for entry in ($loc_classes | first $show_loc) {
        $doc = $doc + $"| `($entry.class.name)`\n| ($entry.class.methods | length)\n| `($entry.class.package)`\n\n"
    }
    $doc = $doc + "|===\n\n"
    if ($loc_classes | length) > 15 { $doc = $doc + $"_And ($($loc_classes | length) - 15) more local classes..._\n\n" }

    # Numbered recommendations
    $doc = $doc + "== Recommendations\n\n"
    let indexed_recs = $recs | enumerate
    for item in $indexed_recs { $doc = $doc + $"($item.index + 1). ($item.item)\n\n" }

    let conclusion = if $pct < 70 {
        "🚨 *CRITICAL:* Significant deviations detected requiring immediate attention."
    } else if $pct < 90 {
        "⚠️ *WARNING:* Some deviations detected requiring review and planning."
    } else {
        "✅ *SUCCESS:* Good alignment with upstream tests, minor improvements possible."
    }

    $doc = $doc + $"== Conclusion\n\n($conclusion)\n\n*Next Steps:*\n\n1. Review missing critical tests and plan implementation\n2. Validate modified tests maintain TinkerPop compliance\n3. Implement additional tests for enhanced coverage\n4. Schedule regular deviation analysis to maintain alignment\n\n---\n\n*Generated:* ($report.timestamp) +\n*Tool:* TinkerCat Compliance Deviation Analyzer +\n*Upstream Source:* Apache TinkerPop (github.com/apache/tinkerpop)\n"

    $doc
}

# ── JSON report ───────────────────────────────────────────────────────────────

def generate-json [report: record, recs: list<string>]: nothing -> string {
    {
        timestamp:       $report.timestamp
        coverage:        $report.coverage
        missing:         $report.missing
        extra:           $report.extra
        categories:      ($report.categories | select name priority description count)
        recommendations: $recs
        upstream_classes: ($report.upstream_classes | get key)
        local_classes:    ($report.local_classes    | get key)
    } | to json --indent 2
}

# ── HTML report ───────────────────────────────────────────────────────────────

def generate-html [report: record, recs: list<string>]: nothing -> string {
    let pct   = $report.coverage.pct
    let pct_r = $pct | math round --precision 1
    let n_mis = $report.missing | length
    let n_ext = $report.extra   | length
    let color = if $pct < 70 { "#dc3545" } else if $pct < 90 { "#ffc107" } else { "#28a745" }

    let rec_li = $recs | each { |r| $"                <li>($r)</li>" } | str join "\n"

    let show_mis = [$n_mis 50] | math min
    let missing_divs = $report.missing | sort | first $show_mis
        | each { |t| $"                <div class=\"item\">($t)</div>" } | str join "\n"
    let more_mis = if $n_mis > 50 {
        $"                <div class=\"item\"><em>... and ($n_mis - 50) more</em></div>"
    } else { "" }

    let show_ext = [$n_ext 30] | math min
    let extra_divs = $report.extra | sort | first $show_ext
        | each { |t| $"                <div class=\"item\">($t)</div>" } | str join "\n"

    $"<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <title>TinkerPop Compliance Deviation Analysis</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
    .wrap { max-width: 1200px; margin: 0 auto; }
    .hdr  { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,.1); margin-bottom: 20px; }
    .badge { display: inline-block; padding: 8px 16px; border-radius: 20px; color: white; font-weight: bold; background: ($color); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(200px,1fr)); gap: 20px; margin: 20px 0; }
    .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,.1); }
    .val  { font-size: 2em; font-weight: bold; }
    .lbl  { color: #666; margin-bottom: 8px; }
    .sec  { background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,.1); }
    .lst  { max-height: 300px; overflow-y: auto; background: #f8f9fa; padding: 10px; border-radius: 4px; }
    .item { padding: 4px 0; font-family: monospace; border-bottom: 1px solid #eee; }
    .bar  { background: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden; margin-top: 8px; }
    .fill { height: 100%; background: ($color); }
    footer { text-align: center; margin-top: 40px; color: #666; font-size: .9em; }
  </style>
</head>
<body><div class=\"wrap\">
  <div class=\"hdr\">
    <h1>🔍 TinkerPop Compliance Deviation Analysis</h1>
    <p><strong>Date:</strong> ($report.timestamp)</p>
    <p><strong>Status:</strong> <span class=\"badge\">($pct_r)%% Coverage</span></p>
  </div>
  <div class=\"grid\">
    <div class=\"card\"><div class=\"lbl\">Coverage</div><div class=\"val\">($pct_r)%%</div><div class=\"bar\"><div class=\"fill\" style=\"width:($pct_r)%%\"></div></div></div>
    <div class=\"card\"><div class=\"lbl\">Upstream Tests</div><div class=\"val\">($report.coverage.total_upstream)</div></div>
    <div class=\"card\"><div class=\"lbl\">Local Tests</div><div class=\"val\">($report.coverage.total_local)</div></div>
    <div class=\"card\"><div class=\"lbl\">Missing Tests</div><div class=\"val\" style=\"color:#dc3545\">($n_mis)</div></div>
  </div>
  <div class=\"sec\">
    <h2>📋 Recommendations</h2>
    <ul>
($rec_li)
    </ul>
  </div>
  <div class=\"sec\">
    <h2>❌ Missing Tests \(($n_mis)\)</h2>
    <div class=\"lst\">
($missing_divs)
($more_mis)
    </div>
  </div>
  <div class=\"sec\">
    <h2>➕ Extra Tests \(($n_ext)\)</h2>
    <div class=\"lst\">
($extra_divs)
    </div>
  </div>
  <footer>
    <p>Generated by TinkerCat Compliance Deviation Analyzer</p>
    <p>Upstream: Apache TinkerPop (github.com/apache/tinkerpop)</p>
  </footer>
</div></body></html>"
}

# ── entry point ───────────────────────────────────────────────────────────────

def main [
    --format (-f): string = "adoc"  # Output format: adoc (default), html, json
    --download (-d)                  # Force fresh download of upstream tests
    --output (-o): string = ""       # Explicit output file path
    --project-root (-p): string = "" # Project root directory (default: auto-detect)
] {
    if $format not-in ["adoc" "html" "json"] {
        print $"❌ Unknown format '($format)'. Choose adoc, html, or json."
        exit 1
    }

    let root = if ($project_root | is-not-empty) {
        $project_root | path expand
    } else {
        find-project-root $env.PWD
    }
    print $"📁 Project root: ($root)"

    let cache_dir  = $root | path join "build" "upstream_tests"
    let report_dir = $root | path join "build" "reports" "compliance"
    mkdir $report_dir

    let need_dl = $download or not ($cache_dir | path join "extracted" | path exists)
    if $need_dl {
        if not (download-upstream-tests $cache_dir) { exit 1 }
    }

    let upstream = analyze-upstream-tests $cache_dir
    let local    = analyze-local-tests $root

    if ($upstream | is-empty) and ($local | is-empty) {
        print "❌ No tests found to analyse"
        exit 1
    }

    let report = compare-tests $upstream $local
    let recs   = make-recommendations $report

    let ts = date now | format date '%Y%m%d_%H%M%S'
    let out_path = if ($output | is-not-empty) {
        $output
    } else {
        $report_dir | path join $"compliance_deviation_report_($ts).($format)"
    }

    let content = match $format {
        "adoc" => (generate-adoc $report $recs)
        "json" => (generate-json $report $recs)
        "html" => (generate-html $report $recs)
        _      => ""
    }
    $content | save --force $out_path

    let icon = match $format { "json" => "📊" "html" => "🌐" _ => "📄" }
    print $"($icon) Report written: ($out_path)"

    let pct_r = $report.coverage.pct | math round --precision 1
    print $"\n📊 Analysis Complete:"
    print $"   Coverage : ($pct_r)%%"
    print $"   Missing  : ($report.missing | length) tests"
    print $"   Extra    : ($report.extra   | length) tests"
}
