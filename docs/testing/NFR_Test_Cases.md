# Non-Functional Requirements Test Cases

## 1. Performance Testing

| Test Case ID | Requirement | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-Perf-01 | ESIMS-NF-001 | Measure 10 requests each for inventory listing, inventory search, low-stock listing, and product search. | At least 90% of tested requests complete within 3 seconds. | All tested read requests met the 3-second threshold in the focused NFR run. | Passed |
| TC-Perf-02 | ESIMS-NF-001 | Measure 10 purchase and 10 sales recording requests. | At least 90% of tested requests complete within 3 seconds. | All tested transaction requests met the 3-second threshold in the focused NFR run. | Passed |

## 2. Reliability Testing

| Test Case ID | Requirement | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-Rel-01 | ESIMS-NF-002 | Record a purchase and verify inventory, purchase, purchase-item, and stock-movement records. | Records remain consistent and inventory quantities update correctly. | Existing purchase tests passed. | Passed |
| TC-Rel-02 | ESIMS-NF-002 | Submit invalid purchase data and inspect the database state. | Invalid transactions do not leave partial transaction records or incorrect inventory updates. | Existing invalid-purchase tests passed. | Passed |

## 3. Availability Testing

| Test Case ID | Requirement | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-Avail-01 | ESIMS-NF-003 | Access available application pages and refresh them during a test session. | The application remains accessible during the test session. | Available pages loaded and remained accessible during manual testing. | Basic check passed; continuous availability not established. |

## 4. Usability Testing

| Test Case ID | Requirement | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-UX-01 | ESIMS-NF-004 | Use the available login, inventory, search, low-stock, product, supplier, purchase, sales, and report interfaces. | Available tasks can be completed without critical usability errors. | The listed workflows were completed during manual browser testing without critical usability errors. | Passed |
| TC-UX-02 | ESIMS-NF-004 | Navigate between integrated pages and verify logout behavior. | Navigation and logout work correctly across the application. | Navigation and logout were verified manually; protected pages redirected to login after logout. | Passed |

## 5. Security Testing

| Test Case ID | Requirement | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-Sec-01 | ESIMS-SR-001 | Attempt to access protected pages without authentication. | Unauthenticated access is rejected or redirected to login. | Automated NFR security tests passed. | Passed |
| TC-Sec-02 | ESIMS-SR-003 | Inspect a stored user password and verify it is hashed. | Passwords are not stored as plaintext. | Automated NFR security test passed. | Passed |
| TC-Sec-03 | ESIMS-SR-004 | Submit invalid product input. | Invalid input is rejected without modifying the product. | Automated NFR security test passed. | Passed |
| TC-Sec-04 | ESIMS-SR-005 | Attempt unauthenticated product, purchase, and sales modifications. | Unauthorized modification attempts are rejected. | Automated NFR security tests passed. | Passed |
| TC-Sec-05 | ESIMS-SR-001 | Log out and then access the protected dashboard. | The session is invalidated and the dashboard redirects to login. | Automated NFR security test passed. | Passed |
| TC-Sec-06 | ESIMS-SR-002 | Attempt restricted administrative functions as an unauthorized role. | Unauthorized users cannot access restricted functions. | No separate role-restricted routes are currently implemented; this remains pending. | Pending |

## 6. Pending Tests and Limitations

- Sales-related reliability tests are covered by the existing sales module tests.
- Availability testing so far is a basic manual check, not a sustained availability test.
- Usability testing covered the available interfaces and workflows manually; it does not establish formal user-study metrics.
- Performance measurements apply to the tested endpoints and isolated SQLite test conditions.
- Role-specific authorization remains pending because the current application does not expose separate restricted administrative routes.
- The results above reflect the focused NFR tests and manual checks performed so far.