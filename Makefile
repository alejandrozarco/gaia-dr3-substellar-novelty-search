# Gaia DR3 NSS Substellar Novelty Search — Makefile
#
# Single-command interface for the most common reproduction targets.
# Not all pipeline stages are wrapped — the full cascade requires
# ~100-200 GB of catalog data not redistributed here. See
# REPRODUCIBILITY.md for the full scope statement.

.PHONY: help benchmark benchmark-truth-set benchmark-v2 benchmark-v3 \
        benchmark-figures verify-catalogs verify-deps lock clean \
        info paths test test-verbose

# Configuration
PYTHON ?= python3
PIP ?= pip
CONFIG ?= config.yaml
BENCH_DIR := scripts/benchmark
OUT_DIR := benchmark_output

# ============================================================
help:  ## Show this help message
	@echo "Gaia DR3 NSS Substellar Novelty Search — make targets"
	@echo ""
	@echo "Most common:"
	@echo "  make benchmark       Run full cascade benchmark (truth set + v2 + v3 + figures)"
	@echo "  make verify-catalogs Check that required catalog files exist"
	@echo "  make verify-deps     Check Python dependencies are installed"
	@echo "  make info            Print configuration and paths"
	@echo ""
	@echo "Granular:"
	@echo "  make benchmark-truth-set  Build truth_set.csv only"
	@echo "  make benchmark-v2         Run v2 cascade benchmark (no Sahlmann tie-breaking)"
	@echo "  make benchmark-v3         Run v3 cascade benchmark (with tie-breaking)"
	@echo "  make benchmark-figures    Regenerate benchmark figures (PNG, 300 dpi)"
	@echo ""
	@echo "Tests:"
	@echo "  make test          Run cascade filter test suite (pytest, offline)"
	@echo "  make test-verbose  Run tests with verbose output"
	@echo ""
	@echo "Maintenance:"
	@echo "  make lock     Regenerate requirements-lock.txt"
	@echo "  make clean    Remove $(OUT_DIR)/ and benchmark_output/"
	@echo ""
	@echo "Reproducibility note: the FULL pipeline (filter cascade against"
	@echo "all ~26,000 candidates) requires external catalog data not"
	@echo "redistributed here. The benchmark targets only require the data"
	@echo "files in this repo (v2_scan_full_pool.csv + truth-set inputs)."
	@echo "See REPRODUCIBILITY.md."

# ============================================================
info:  ## Show configuration paths and Python version
	@echo "Python:    $$($(PYTHON) --version)"
	@echo "Config:    $(CONFIG)"
	@echo "Output:    $(OUT_DIR)/"
	@echo "Benchmark scripts: $(BENCH_DIR)/"
	@echo "Repo root: $$(pwd)"

paths: info  ## Alias for info

# ============================================================
verify-deps:  ## Verify Python dependencies are installed
	@$(PYTHON) -c "import polars, numpy, scipy, astropy, dynesty, matplotlib" \
		&& echo "All required packages importable." \
		|| (echo "Missing packages. Run: $(PIP) install -r requirements.txt" && exit 1)

verify-catalogs:  ## Check that required input CSVs are present
	@test -f v2_scan_full_pool.csv \
		&& echo "OK: v2_scan_full_pool.csv ($$(wc -l < v2_scan_full_pool.csv) rows)" \
		|| (echo "MISSING: v2_scan_full_pool.csv" && exit 1)
	@test -f novelty_candidates.csv \
		&& echo "OK: novelty_candidates.csv ($$(wc -l < novelty_candidates.csv) rows)" \
		|| (echo "MISSING: novelty_candidates.csv" && exit 1)
	@if [ -f $(CONFIG) ]; then \
		echo "OK: $(CONFIG) present"; \
		SAHL=$$($(PYTHON) -c "import yaml; print(yaml.safe_load(open('$(CONFIG)'))['benchmark']['sahlmann_verdicts'])"); \
		FPS=$$($(PYTHON) -c "import yaml; print(yaml.safe_load(open('$(CONFIG)'))['benchmark']['gaia_fp_list'])"); \
		test -f "$$SAHL" && echo "OK: $$SAHL" || echo "WARNING: external Sahlmann file not at $$SAHL"; \
		test -f "$$FPS" && echo "OK: $$FPS" || echo "WARNING: external FP list not at $$FPS"; \
	else \
		echo "WARNING: $(CONFIG) missing — copy config.yaml.example to config.yaml"; \
	fi

# ============================================================
$(OUT_DIR):
	mkdir -p $(OUT_DIR)

benchmark-truth-set: verify-deps verify-catalogs | $(OUT_DIR)  ## Build truth set
	@echo "Building truth set..."
	$(PYTHON) $(BENCH_DIR)/build_truth_set.py --config $(CONFIG) --out-dir $(OUT_DIR)

benchmark-v2: benchmark-truth-set  ## Run v2 cascade benchmark
	@echo "Running v2 benchmark..."
	$(PYTHON) $(BENCH_DIR)/run_benchmark_v2.py --out-dir $(OUT_DIR)

benchmark-v3: benchmark-v2  ## Run v3 cascade benchmark (Sahlmann tie-breaking)
	@echo "Running v3 benchmark with Sahlmann tie-breaking simulation..."
	$(PYTHON) $(BENCH_DIR)/simulate_sahlmann_tiebreaking.py --out-dir $(OUT_DIR)

benchmark-figures: benchmark-v3  ## Regenerate benchmark figures
	@echo "Generating figures..."
	$(PYTHON) $(BENCH_DIR)/make_figure.py --out-dir $(OUT_DIR)
	$(PYTHON) $(BENCH_DIR)/make_v3_figure.py --out-dir $(OUT_DIR)

benchmark: benchmark-figures  ## Run full benchmark pipeline (truth set + v2 + v3 + figures)
	@echo ""
	@echo "============================================================"
	@echo "Benchmark complete. Outputs in $(OUT_DIR)/"
	@echo "============================================================"
	@echo ""
	@if [ -f $(OUT_DIR)/v3_metrics_summary.txt ]; then cat $(OUT_DIR)/v3_metrics_summary.txt; fi

# ============================================================
lock:  ## Regenerate requirements-lock.txt from current environment
	@echo "Regenerating lockfile..."
	$(PIP) freeze > requirements-lock.txt
	@echo "Wrote requirements-lock.txt ($$(wc -l < requirements-lock.txt) packages)."

clean:  ## Remove benchmark outputs
	rm -rf $(OUT_DIR)
	@echo "Removed $(OUT_DIR)/"

# ============================================================
test:  ## Run cascade filter test suite (pytest, offline)
	PYTHONPATH=scripts $(PYTHON) -m pytest tests/

test-verbose:  ## Run tests with verbose output
	PYTHONPATH=scripts $(PYTHON) -m pytest tests/ -v
