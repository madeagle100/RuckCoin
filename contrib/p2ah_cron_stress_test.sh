#!/usr/bin/env bash
# P2AH continuous validation harness for cron/CI.
#
# Example crontab (every 5 minutes):
#   */5 * * * * /opt/Ravencoin/contrib/p2ah_cron_stress_test.sh >> /opt/Ravencoin/logs/p2ah-stress/cron.log 2>&1
#
# Environment overrides:
#   P2AH_REPO          — repo root (default: parent of contrib/)
#   P2AH_LOG_DIR       — log directory (default: $P2AH_REPO/logs/p2ah-stress)
#   P2AH_STRESS_ROUNDS — rounds for feature_assetauth_stress.py (default: 3)
#   P2AH_FUNCTIONAL_LOOPS — repeats of each functional test per run (default: 2)
#   P2AH_RUN_RELATED     — set to 0 to skip adjacent asset functional tests (default: 1)
#   P2AH_SKIP_BUILD      — set to 1 to skip auto-build when binaries missing
#   P2AH_JOBS          — parallel make jobs (default: nproc)

set -euo pipefail

P2AH_REPO="${P2AH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
P2AH_LOG_DIR="${P2AH_LOG_DIR:-${P2AH_REPO}/logs/p2ah-stress}"
P2AH_STRESS_ROUNDS="${P2AH_STRESS_ROUNDS:-3}"
P2AH_FUNCTIONAL_LOOPS="${P2AH_FUNCTIONAL_LOOPS:-2}"
P2AH_RUN_RELATED="${P2AH_RUN_RELATED:-1}"
P2AH_JOBS="${P2AH_JOBS:-$(nproc)}"
LOCK_FILE="${P2AH_LOCK_FILE:-/tmp/p2ah_cron_stress_test.lock}"
PTHREAD_SHIM="${P2AH_PTHREAD_SHIM:-/tmp/pthread_yield_compat.c}"

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_LOG="${P2AH_LOG_DIR}/run-${RUN_ID}.log"
SUMMARY_LOG="${P2AH_LOG_DIR}/summary.log"

mkdir -p "${P2AH_LOG_DIR}"

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) SKIP already running (lock ${LOCK_FILE})" | tee -a "${SUMMARY_LOG}"
    exit 0
fi

exec > >(tee -a "${RUN_LOG}") 2>&1

echo "================================================================"
echo "P2AH stress run ${RUN_ID}"
echo "repo=${P2AH_REPO} rounds=${P2AH_STRESS_ROUNDS} functional_loops=${P2AH_FUNCTIONAL_LOOPS}"
echo "================================================================"

cd "${P2AH_REPO}"

TEST_BIN="${P2AH_REPO}/src/test/test_raven"
RAVEND_BIN="${P2AH_REPO}/src/ravend"
CONFIG_INI="${P2AH_REPO}/test/config.ini"
PYTHON="${PYTHON:-python3}"

TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0

ensure_pthread_shim() {
    if [[ ! -f /tmp/pthread_yield_compat.o ]]; then
        if [[ ! -f "${PTHREAD_SHIM}" ]]; then
            cat > "${PTHREAD_SHIM}" <<'EOF'
#include <sched.h>
int pthread_yield(void) { return sched_yield(); }
EOF
        fi
        gcc -c "${PTHREAD_SHIM}" -o /tmp/pthread_yield_compat.o
    fi
}

ensure_binaries() {
    if [[ -x "${TEST_BIN}" && -x "${RAVEND_BIN}" ]]; then
        return 0
    fi
    if [[ "${P2AH_SKIP_BUILD:-0}" == "1" ]]; then
        echo "ERROR: binaries missing and P2AH_SKIP_BUILD=1"
        return 1
    fi
    echo "Building ravend + test_raven..."
    ensure_pthread_shim
    if [[ ! -f Makefile ]]; then
        ./autogen.sh
        BDB_LIBS='-L/opt/db4/lib -ldb_cxx-4.8 -lpthread' \
        BDB_CFLAGS='-I/opt/db4/include' \
        LDFLAGS='-lpthread' \
        ./configure --disable-shared --with-pic --enable-benchmark=no --with-bignum=no --enable-module-recovery
    fi
    make -j"${P2AH_JOBS}" -C src ravend test/test_raven LIBS="/tmp/pthread_yield_compat.o"
}

run_step() {
    local name="$1"
    shift
    TOTAL=$((TOTAL + 1))
    local start end elapsed rc
    start=$(date +%s)
    echo ""
    echo "---- [${TOTAL}] ${name} ----"
    set +e
    "$@"
    rc=$?
    set -e
    end=$(date +%s)
    elapsed=$((end - start))
    if [[ ${rc} -eq 0 ]]; then
        PASSED=$((PASSED + 1))
        echo "PASS ${name} (${elapsed}s)"
        printf '%s PASS %s (%ss)\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${name}" "${elapsed}" >> "${SUMMARY_LOG}"
    else
        FAILED=$((FAILED + 1))
        echo "FAIL ${name} exit=${rc} (${elapsed}s)"
        printf '%s FAIL %s exit=%s (%ss)\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${name}" "${rc}" "${elapsed}" >> "${SUMMARY_LOG}"
    fi
    return 0
}

run_boost_suite() {
    local suite="$1"
    "${TEST_BIN}" --run_test="${suite}"
}

run_functional() {
    local script="$1"
    shift || true
    (cd "${P2AH_REPO}" && "${PYTHON}" test/functional/test_runner.py "${script}" "$@")
}

ensure_binaries

echo "ravend: $("${RAVEND_BIN}" --version | head -1)"
echo "test_raven: ${TEST_BIN}"

# --- Unit tests: P2AH core and nearby consensus/wallet surface ---
UNIT_SUITES=(
    assetauth_tests
    base58_tests
    asset_tests
    asset_tx_tests
    script_standard_tests
    script_tests
    transaction_tests
    serialization_tests
)

for suite in "${UNIT_SUITES[@]}"; do
    run_step "unit:${suite}" run_boost_suite "${suite}"
done

# --- Functional: canonical suite (looped) ---
for loop in $(seq 1 "${P2AH_FUNCTIONAL_LOOPS}"); do
    run_step "functional:feature_assetauth.py#${loop}" run_functional feature_assetauth.py
done

# --- Functional: stress harness (looped with configurable rounds) ---
for loop in $(seq 1 "${P2AH_FUNCTIONAL_LOOPS}"); do
    run_step "functional:feature_assetauth_stress.py#${loop}" \
        run_functional feature_assetauth_stress.py --stress-rounds="${P2AH_STRESS_ROUNDS}"
done

# --- Functional: asset RPC/regression neighbors ---
RELATED_FUNCTIONAL=(
    feature_assets.py
    feature_rawassettransactions.py
    rpc_signrawtransaction.py
    rpc_rawtransaction.py
)

for script in "${RELATED_FUNCTIONAL[@]}"; do
    if [[ "${P2AH_RUN_RELATED}" == "1" ]]; then
        run_step "functional:${script}" run_functional "${script}"
    else
        SKIPPED=$((SKIPPED + 1))
        echo "SKIP functional:${script} P2AH_RUN_RELATED=0"
    fi
done

# --- Repeated P2AH unit hammer (catch flaky/intermittent issues) ---
for loop in $(seq 1 3); do
    run_step "unit:assetauth_tests:repeat${loop}" run_boost_suite assetauth_tests
done

echo ""
echo "================================================================"
echo "P2AH stress run ${RUN_ID} complete"
echo "total=${TOTAL} passed=${PASSED} failed=${FAILED} skipped=${SKIPPED}"
echo "log=${RUN_LOG}"
echo "================================================================"

printf '%s DONE total=%s passed=%s failed=%s log=%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${TOTAL}" "${PASSED}" "${FAILED}" "${RUN_LOG}" >> "${SUMMARY_LOG}"

if [[ ${FAILED} -gt 0 ]]; then
    exit 1
fi

exit 0
