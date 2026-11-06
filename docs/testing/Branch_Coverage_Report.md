# Branch Coverage Report

## 1. Introduction

This report presents the branch coverage analysis of the Electronics Store Inventory Management System (ESIMS). Branch coverage measures whether the different decision outcomes in the application code have been executed during testing.

The analysis was performed using pytest and the pytest-cov plugin with branch coverage enabled.

## 2. Testing Environment

| Parameter | Details |
|---|---|
| Project | Electronics Store Inventory Management System |
| Testing Framework | pytest |
| Coverage Tool | pytest-cov |
| Coverage Version | 7.17.2 |
| Python Version | 3.15.0 |
| Operating System | Windows |
| Testing Date | 6 November 2026 |

## 3. Testing Command

The following command was executed to measure branch coverage and generate HTML and XML reports:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  --cov=app `
  --cov-branch `
  --cov-report=term-missing `
  --cov-report=html:docs/testing/branch-coverage-html `
  --cov-report=xml:docs/testing/branch-coverage.xml
```

## 4. Test Execution Summary

| Metric | Result |
|---|---:|
| Tests Passed | 155 |
| Tests Skipped | 3 |
| Tests Failed | 0 |
| Warnings | 769 |
| Execution Time | 16.55 seconds |

The three skipped tests require a MySQL DATABASE_URL to execute the database-specific constraint checks.

## 5. Overall Coverage Results

| Coverage Metric | Result |
|---|---:|
| Total Statements | 796 |
| Statements Covered | 728 |
| Statements Missed | 68 |
| Line Coverage | 91.46% |
| Total Branches | 190 |
| Branches Covered | 154 |
| Branches Missed | 36 |
| Branch Coverage | 81.05% |
| Partially Covered Branch Lines | 32 |
| Combined Coverage | 89% |

Branch coverage was calculated as:

Branch Coverage = (Covered Branches / Total Branches) × 100

= (154 / 190) × 100

= **81.05%**

## 6. Module-wise Coverage Results

| Module | Statements | Missed | Branches | Partial Branches | Combined Coverage |
|---|---:|---:|---:|---:|---:|
| app/__init__.py | 40 | 2 | 4 | 2 | 91% |
| app/auth/__init__.py | 17 | 2 | 0 | 0 | 88% |
| app/auth/routes.py | 38 | 12 | 12 | 4 | 64% |
| app/extensions.py | 6 | 0 | 0 | 0 | 100% |
| app/inventory/routes.py | 73 | 0 | 22 | 0 | 100% |
| app/models.py | 108 | 1 | 0 | 0 | 99% |
| app/products/routes.py | 117 | 12 | 38 | 5 | 89% |
| app/purchases/routes.py | 109 | 15 | 32 | 7 | 84% |
| app/reports/routes.py | 83 | 0 | 22 | 0 | 100% |
| app/sales/routes.py | 101 | 2 | 20 | 2 | 97% |
| app/suppliers/routes.py | 93 | 22 | 40 | 12 | 73% |

## 7. Analysis of Results

- The inventory and reports modules achieved 100% combined coverage, indicating that all measured statements and branch outcomes in these modules were exercised.
- The sales module achieved 97% combined coverage.
- The products module achieved 89% combined coverage.
- The purchases module achieved 84% combined coverage.
- The suppliers module achieved 73% combined coverage and has additional untested statements and branch outcomes.
- The authentication routes achieved 64% combined coverage, indicating scope for additional tests involving authentication and access-control decision paths.
- Overall branch coverage was 81.05%, with 154 out of 190 branch outcomes executed.

## 8. Generated Reports

The following coverage reports were generated:

- HTML Report: `docs/testing/branch-coverage-html/`
- XML Report: `docs/testing/branch-coverage.xml`

The HTML report provides a detailed, module-wise view of covered and uncovered statements and branches. The XML report contains machine-readable coverage statistics.

## 9. Observations

The test execution completed successfully with 155 passed tests and 3 skipped tests. No test failures were reported.

A SQLite database ResourceWarning concerning an unclosed database connection was displayed after execution. It did not cause test failures or prevent coverage report generation.

## 10. Conclusion

The branch coverage analysis indicates that the ESIMS application achieved 81.05% branch coverage and 91.46% line coverage. The results demonstrate that most application statements and decision paths were exercised by the automated test suite.

The coverage reports also identify areas where additional tests could improve coverage, particularly in authentication, supplier management, and purchase-related workflows.