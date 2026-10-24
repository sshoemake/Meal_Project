
#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON="${PYTHON:-python3.12}"
VENV_DIR="$ROOT_DIR/.venv-test"
PY="$VENV_DIR/bin/python"

CHECK_NAMES=()
CHECK_RESULTS=()
TEST_COUNT=""
COVERAGE_PERCENT=""

record_result() {
    CHECK_NAMES+=("$1")
    CHECK_RESULTS+=("$2")
}

print_summary() {
    local exit_code=$?
    local i
    local overall="ALL CHECKS PASSED"

    trap - EXIT

    if [[ "$exit_code" -ne 0 ]]; then
        overall="FAILED"
    fi

    echo
    echo "================ FINAL STATUS ================"
    printf "%-34s %s\n" "Check" "Result"
    printf '%s\n' "------------------------------------------------"

    for i in "${!CHECK_NAMES[@]}"; do
        printf "%-34s %s\n" \
            "${CHECK_NAMES[$i]}" "${CHECK_RESULTS[$i]}"
    done

    if [[ -n "$TEST_COUNT" ]]; then
        printf "%-34s %s\n" "Unit test count" "$TEST_COUNT"
    fi

    if [[ -n "$COVERAGE_PERCENT" ]]; then
        printf "%-34s %s\n" "Code coverage" "$COVERAGE_PERCENT"
    fi

    # Mark checks not reached after a failure.
    if [[ "$exit_code" -ne 0 ]]; then
        for i in \
            "Remaining checks"; do
            :
        done
    fi

    echo "------------------------------------------------"
    echo "Overall status: $overall"
    echo "================================================"
}

trap print_summary EXIT

run_check() {
    local name="$1"
    shift

    local log_file
    local result
    local count
    local coverage

    log_file="$(mktemp "${TMPDIR:-/tmp}/meal-test.XXXXXX")"

    echo
    echo "==> $name"

    if "$@" >"$log_file" 2>&1; then
        result="PASS"
    else
        result="FAIL"
    fi

    cat "$log_file"

    case "$name" in
        "Unit tests")
            count="$(sed -nE 's/^Ran ([0-9]+) test.*/\1/p' "$log_file" | tail -n 1)"
            if [[ -n "$count" ]]; then
                TEST_COUNT="$count passed"
            fi
            ;;
        "Code coverage")
            coverage="$(awk '/^TOTAL[[:space:]]/ {print $4}' "$log_file" | tail -n 1)"
            if [[ -n "$coverage" ]]; then
                COVERAGE_PERCENT="$coverage"
            fi
            ;;
    esac

    rm -f "$log_file"
    record_result "$name" "$result"

    if [[ "$result" == "FAIL" ]]; then
        return 1
    fi
}

echo "==> Checking Python"
run_check "Python version" "$PYTHON" --version

echo
echo "==> Rebuilding test virtual environment"
rm -rf "$VENV_DIR"
run_check "Create test environment" "$PYTHON" -m venv "$VENV_DIR"

echo
echo "==> Installing dependencies"
run_check "Upgrade pip" "$PY" -m pip install --upgrade pip
run_check "Install requirements" "$PY" -m pip install -r requirements-dev.txt

run_check "Dependency consistency" "$PY" -m pip check
run_check "Ruff" "$PY" -m ruff check .
run_check "Black formatting" "$PY" -m black --check app/ manage.py
run_check "Django configuration" "$PY" manage.py check
run_check "Migration check" "$PY" manage.py makemigrations --check --dry-run

run_check "Dependency audit" \
    env PIPAPI_PYTHON_LOCATION="$PY" "$PY" -m pip_audit --strict

run_check "Clear old coverage data" "$PY" -m coverage erase
run_check "Unit tests" "$PY" -m coverage run manage.py test
run_check "Code coverage" "$PY" -m coverage report -m --fail-under=90

echo
echo "==> All local checks passed!"
