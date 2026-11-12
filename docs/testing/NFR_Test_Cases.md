# Non-Functional Requirements Test Cases

**Project:** Electronics Store Inventory Management System (ESIMS)  
**Testing Date:** 6 November 2026  
**Testing Type:** Non-Functional Testing

## 1. Performance Testing

| Test Case ID | Requirement ID | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-Perf-01 | ESIMS-NF-001 | Measure the response time of inventory listing, product search, and low-stock endpoints. | Each tested endpoint should respond within 3 seconds. | All three tested endpoints completed in under 3 seconds. | Passed |

## 2. Reliability Testing

| Test Case ID | Requirement ID | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-Rel-01 | ESIMS-NF-002 | Record a purchase and verify the associated purchase, purchase-item, inventory, and stock-movement updates. | Purchase details should be recorded and the corresponding inventory updates should be handled correctly. | Existing purchase-related automated tests passed. | Passed |
| TC-Rel-02 | ESIMS-NF-002 | Submit invalid purchase data and verify that invalid data is rejected without an unintended purchase update. | Invalid purchase data should be rejected and the operation should not create an unintended successful transaction. | Existing invalid-purchase tests passed. | Passed |
| TC-Rel-03 | ESIMS-NF-002 | Execute the sales workflow and verify the expected sales functionality. | Valid sales operations should complete successfully and update the relevant application data. | Sales-related automated tests and manual system validation passed. | Passed |

**Additional reliability verification:** Concurrent transactions, simultaneous sales of the last available item, and complete rollback behavior require dedicated verification if they are included in the final reliability acceptance criteria.

## 3. Availability Testing

| Test Case ID | Requirement ID | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-Avail-01 | ESIMS-NF-003 | Access the available application pages and refresh pages during an active session. | Available pages should load without unexpected application failures during the check. | The tested pages remained accessible during the basic manual check. | Passed - Basic Check |

**Limitation:** This test represents a basic availability check. It does not establish sustained uptime or availability under prolonged usage.

## 4. Usability Testing

| Test Case ID | Requirement ID | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-UX-01 | ESIMS-NF-004 | Use the login, inventory, search, low-stock, product, supplier, and purchase interfaces. | Available interfaces and forms should be understandable and usable for their intended operations. | The tested interfaces and forms worked during the manual checks. | Passed |
| TC-UX-02 | ESIMS-NF-004 | Navigate between the tested application pages and verify session-related behavior, including logout. | Navigation and session-related operations should work as expected. | The navigation, UI, and session-related system validation cases were included in the 40 manual cases reported as passed. | Passed - Tested Flows |

**Limitation:** The result applies to the tested application flows and does not represent a formal usability study with multiple end users.

## 5. Security Testing

| Test Case ID | Requirement ID | Test Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-Sec-01 | ESIMS-SR-001 | Attempt to access protected application pages without authentication. | Unauthenticated users should not be allowed to access protected pages. | Existing authentication and access-control tests passed. | Passed |
| TC-Sec-04 | ESIMS-SR-002 | Attempt product and supplier management as Store Staff and Administrator. | Store Staff should be denied restricted management operations; Administrators should be allowed. | Automated role-authorization tests passed for restricted product and supplier routes. | Passed |
| TC-Sec-02 | ESIMS-SR-004 | Submit invalid or incomplete data through application forms. | Invalid input should be rejected through appropriate validation. | Existing form and input-validation tests passed. | Passed |
| TC-Sec-03 | ESIMS-SR-005 | Submit invalid purchase data and verify that it is handled safely. | Invalid purchase operations should be rejected without unintended successful updates. | Existing invalid-purchase tests passed. | Passed |

## 6. Additional Verification and Limitations

The following checks are important for more extensive non-functional validation:

1. **Concurrent transactions:** Verify behavior when multiple users attempt to update the same inventory item simultaneously.
2. **Last-item sales:** Verify that simultaneous sales cannot cause stock quantities to become incorrect or negative.
3. **Transaction rollback:** Verify database consistency when a purchase or sales operation fails partway through.
4. **Sustained availability:** Perform longer-duration testing to assess application availability over time.
5. **Broader performance testing:** Measure response times across additional endpoints and under different workloads.
6. **Usability evaluation:** Conduct further evaluation with representative users if formal usability evidence is required.

These additional checks should not be considered passed unless their execution is separately recorded.

## 7. Overall Test Case Summary

| Category | Test Cases | Status |
|---|---:|---|
| Performance | 1 | 1 Passed |
| Reliability | 3 | 3 Passed |
| Availability | 1 | 1 Passed - Basic Check |
| Usability | 2 | 2 Passed - Tested Flows |
| Security | 4 | 4 Passed |
| **Total** | **11** | **11 Passed for the stated scope** |

## 8. Conclusion

The defined non-functional test cases cover performance, reliability, availability, usability, and security requirements of ESIMS. Security verification includes both authentication enforcement and role-based authorization for Administrator and Store Staff users.

The tested performance endpoints met the response-time target of under 3 seconds. Existing automated tests supported the purchase, sales, authentication, and validation checks. Basic availability and usability checks were also completed.

Further testing is recommended for sustained availability, concurrent transactions, transaction rollback, and broader performance workloads before claiming complete verification of all non-functional requirements.