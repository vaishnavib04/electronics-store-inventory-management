# Code Coverage Report

## 1. Introduction

This report presents the code coverage analysis of the Electronics Store Inventory Management System (ESIMS). Code coverage measures how much of the application's source code was executed during automated testing.

The analysis was performed using pytest and the pytest-cov plugin.

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

The following command was executed to measure code coverage and generate HTML and XML reports:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  --cov=app `
  --cov-report=term-missing `
  --cov-report=html:docs/testing/code-coverage-html `
  --cov-report=xml:docs/testing/code-coverage.xml
```

## 4. Test Execution Summary

| Metric | Result |
|---|---:|
| Tests Passed | 155 |
| Tests Skipped | 3 |
| Tests Failed | 0 |
| Warnings | 772 |
| Execution Time | 20.34 seconds |

The three skipped tests require a MySQL DATABASE_URL to execute database-specific constraint checks.

## 5. Overall Code Coverage Results

| Metric | Result |
|---|---:|
| Total Statements | 796 |
| Statements Covered | 728 |
| Statements Missed | 68 |
| Overall Line Coverage | 91.46% |

The line coverage percentage was calculated as:

Line Coverage = (Covered Statements / Total Statements) × 100

= (728 / 796) × 100

= **91.46%**

## 6. Module-wise Coverage Results

| Module | Line Coverage |
|---|---:|
| app/__init__.py | 95.00% |
| app/extensions.py | 100.00% |
| app/models.py | 99.07% |
| app/auth/__init__.py | 88.24% |
| app/auth/routes.py | 68.42% |
| app/inventory/routes.py | 100.00% |
| app/products/routes.py | 89.92% |
| app/purchases/routes.py | 86.49% |
| app/reports/routes.py | 100.00% |
| app/sales/routes.py | 98.06% |
| app/suppliers/routes.py | 77.08% |

## 7. Analysis of Results

- The application achieved an overall line coverage of 91.46%.
- The inventory and reports modules achieved 100% line coverage.
- The extensions module achieved 100% coverage.
- The sales module achieved 98.06% coverage.
- The models module achieved 99.07% coverage.
- The products and purchases modules achieved 89.92% and 86.49% coverage, respectively.
- The authentication routes and supplier routes have comparatively lower coverage, indicating opportunities for additional test cases.

## 8. Generated Reports

The following reports were generated successfully:

- HTML Report: `docs/testing/code-coverage-html/`
- XML Report: `docs/testing/code-coverage.xml`

The HTML report provides a detailed view of covered and uncovered source code lines. The XML report provides machine-readable coverage statistics.

## 9. Observations

The test execution completed successfully with 155 passed tests and 3 skipped tests. No test failures were reported.

A SQLite ResourceWarning regarding an unclosed database connection was displayed after execution. This warning did not cause test failures or prevent coverage report generation.

## 10. Conclusion

The code coverage analysis indicates that the ESIMS application achieved 91.46% line coverage, with 728 out of 796 statements executed during automated testing.

The results indicate substantial test coverage across the application's major modules. The generated reports also identify areas where additional test cases could further improve coverage, particularly in authentication and supplier management.