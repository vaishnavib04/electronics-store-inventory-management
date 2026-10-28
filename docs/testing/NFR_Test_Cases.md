# Non-Functional Requirements Test Cases

## 1. Performance Testing

| Test Case ID | Requirement | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-Perf-01 | ESIMS-NF-001 | Measure response times for inventory listing, product search, and low-stock endpoints. | Each tested request completes within 3 seconds. | All three tested endpoints completed within the 3-second threshold. | Passed |

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
| TC-UX-01 | ESIMS-NF-004 | Use the available login, inventory, search, low-stock, product, supplier, and purchase interfaces. | Available tasks can be completed without critical usability errors. | Available pages and forms appeared to work during manual testing. | Basic check passed. |
| TC-UX-02 | ESIMS-NF-004 | Navigate between integrated pages and verify logout behavior. | Navigation and logout work correctly across the application. | Full integration is not yet available. | Pending integration. |

## 5. Security Testing

| Test Case ID | Requirement | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-Sec-01 | ESIMS-SR-001 | Attempt to access protected pages without authentication. | Unauthenticated access is rejected or redirected to login. | Existing security-related tests passed. | Passed |
| TC-Sec-02 | ESIMS-SR-004 | Submit invalid data to supported forms. | Invalid input is rejected with appropriate validation. | Existing validation tests passed. | Passed |
| TC-Sec-03 | ESIMS-SR-005 | Submit invalid purchase transactions and inspect database state. | Invalid operations do not leave inconsistent transaction records. | Existing invalid-purchase tests passed. | Passed |

## 6. Pending Tests and Limitations

- Sales-related reliability tests must be completed when the sales functionality is available.
- Integrated navigation and logout behavior must be retested after the relevant pages are connected.
- Availability testing so far is a basic manual check, not a sustained availability test.
- Usability testing so far covers the available interfaces; it does not establish that every common workflow is free of critical usability errors.
- Performance measurements apply to the tested endpoints and test conditions. They do not independently establish that 90% of all tested requests meet the response-time requirement.
- The results above reflect the existing automated tests and manual checks performed so far. They should be updated when additional tests are completed.