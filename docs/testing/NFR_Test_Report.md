# Non-Functional Requirements Test Report

**Project:** Electronics Store Inventory Management System (ESIMS)  
**Testing Period:** 2 November 2026 – 6 November 2026  
**Report Date:** 6 November 2026  
**Testing Type:** Non-Functional Testing

## 1. Introduction

This report presents the results of non-functional testing performed on the Electronics Store Inventory Management System (ESIMS).

The purpose of testing was to evaluate the system's performance, reliability, availability, usability, and security based on the implemented functionality and available test cases.

## 2. Testing Summary

The following testing activities were completed:

- Automated unit testing using pytest.
- Performance checks on selected application endpoints.
- Reliability checks for purchase and sales workflows.
- Basic availability checks on accessible application pages.
- Manual usability checks on available interfaces.
- Authentication and input-validation testing.
- Manual system validation covering 40 test cases.

### Automated Test Execution

| Test Run | Passed | Skipped | Failed | Description |
|---|---:|---:|---:|---|
| Recorded unit-test run | 153 | 3 | 0 | Initial automated test execution |
| Code coverage run | 155 | 3 | 0 | Separate execution with line coverage measurement |
| Branch coverage run | 155 | 3 | 0 | Separate execution with branch coverage measurement |

The three skipped tests were MySQL-specific constraint tests that required a configured MySQL `DATABASE_URL`. They covered negative product prices, negative reorder levels, and duplicate product SKUs.

The different passing counts correspond to separate test executions and are not combined into one result.

### Manual System Validation

| Metric | Result |
|---|---:|
| Total system validation cases | 40 |
| Passed | 40 |
| Failed | 0 |
| Not executed | 0 |

All 40 manual system validation cases were reported as passed, including the tested application workflows, navigation, UI, and session-related checks.

## 3. Performance Testing

**Requirement:** ESIMS-NF-001

Performance testing was conducted on three selected application endpoints:

1. Inventory listing.
2. Product search.
3. Low-stock information.

**Expected Result:** Each tested endpoint should respond within 3 seconds.

**Actual Result:** All three tested endpoints completed in under 3 seconds.

**Status:** Passed

The tested endpoints met the defined response-time target. However, this result is limited to the selected endpoints and does not establish that 90% of all application requests meet the same target under different workloads.

## 4. Reliability Testing

**Requirement:** ESIMS-NF-002

Reliability testing focused on purchase and sales operations and the handling of invalid data.

| Test Area | Expected Result | Actual Result | Status |
|---|---|---|---|
| Purchase processing | Valid purchase operations should be handled correctly. | Existing purchase-related automated tests passed. | Passed |
| Invalid purchase handling | Invalid purchase data should be rejected. | Existing invalid-purchase tests passed. | Passed |
| Sales workflow | Valid sales operations should work as expected. | Sales-related automated tests and manual system validation passed. | Passed |

These results support the tested purchase and sales functionality.

Dedicated concurrent transaction testing, simultaneous last-item sales, and complete rollback verification should be recorded separately before claiming that these reliability scenarios have been fully verified.

## 5. Availability Testing

**Requirement:** ESIMS-NF-003

Basic availability testing was performed by accessing the available application pages and refreshing pages during an active session.

**Expected Result:** Available pages should load without unexpected application failures during the test.

**Actual Result:** The tested pages remained accessible during the basic manual check.

**Status:** Passed - Basic Check

This testing confirms basic accessibility during the observed checks. It does not establish sustained uptime, long-duration availability, or availability under heavy load.

## 6. Usability Testing

**Requirement:** ESIMS-NF-004

Usability checks were performed on the available application interfaces.

The following areas were covered:

- Login interface.
- Inventory interface.
- Product search.
- Low-stock information.
- Product management forms.
- Supplier management forms.
- Purchase forms.
- Tested navigation and session-related flows.

**Expected Result:** The available interfaces should support their intended operations and allow users to navigate the tested workflows.

**Actual Result:** The tested interfaces and forms worked during the manual checks. The navigation, UI, and session-related cases were also included in the 40 system validation cases reported as passed.

**Status:** Passed - Tested Flows

The results represent preliminary functional usability checks rather than a formal usability study involving multiple end users.

## 7. Security Testing

Security testing focused on authentication, access control, and input validation.

| Test Area | Expected Result | Actual Result | Status |
|---|---|---|---|
| Authentication and access control | Protected pages should not be accessible without authentication. | Existing authentication and access-control tests passed. | Passed |
| Input validation | Invalid or incomplete form data should be rejected. | Existing validation tests passed. | Passed |
| Invalid purchase handling | Invalid purchase operations should be rejected safely. | Existing invalid-purchase tests passed. | Passed |

**Status:** Passed for the tested security cases.

These results cover the security scenarios exercised by the available automated tests. They do not represent a complete security audit or penetration test.

## 8. Limitations and Further Verification

Although the planned basic non-functional checks were completed, the following areas require additional testing for more comprehensive verification:

1. **Sustained availability:** Longer-duration testing is required to evaluate application uptime.
2. **Concurrent transactions:** Multiple simultaneous inventory and sales operations should be tested.
3. **Transaction rollback:** Database consistency should be verified when purchase or sales operations fail partway through.
4. **Broader performance testing:** Additional endpoints and different workloads should be evaluated.
5. **Usability evaluation:** Formal user feedback can be collected to assess ease of use across different user groups.
6. **MySQL-specific constraints:** The three skipped database constraint tests should be executed with a configured MySQL `DATABASE_URL`.

These areas are recorded as limitations or further verification activities and are not represented as completed tests.

## 9. Conclusion

Non-functional testing of ESIMS demonstrated satisfactory results for the tested performance, reliability, availability, usability, and security scenarios.

All three selected performance endpoints responded in under 3 seconds. Existing automated tests passed for the tested purchase, sales, authentication, and validation functionality. Basic availability and usability checks were also successful.

The automated test executions recorded no failures. Three MySQL-specific constraint tests were skipped because a MySQL `DATABASE_URL` was not configured for those executions. Additionally, all 40 manual system validation cases were reported as passed.

Overall, the tested functionality met the stated expectations within the scope of the executed checks. Further verification of sustained availability, concurrent transactions, rollback behavior, broader performance, and MySQL-specific constraints is recommended before claiming complete non-functional requirement verification.