# ESIMS – Updated Test Case Document

**Project:** Electronics Store Inventory Management System (ESIMS)  
**Team:** 10  
**Testing Period:** 2–6 November 2026  
**Document Version:** 2.0  
**Last Updated:** 6 November 2026

---

## 1. Introduction

This document contains the updated test cases for the Electronics Store Inventory Management System (ESIMS). The test cases are derived from the Software Requirements Specification (SRS), Software Test Plan v1.1, and the functionality implemented during Sprint 1 and Sprint 2.

The document covers functional testing, integration testing, security testing, validation, transaction consistency, performance, usability and system-level behaviour.

## 2. Testing Scope

The following modules and functionalities are covered:

1. User authentication and access control.
2. Product management and product deactivation.
3. Inventory viewing, searching and low-stock identification.
4. Supplier management and supplier deactivation.
5. Purchase recording and automatic stock increases.
6. Sales recording and automatic stock deductions.
7. Inventory and sales reporting.
8. Database transaction consistency and stock movement recording.
9. Input validation and security.
10. Application navigation and user feedback.
11. Performance, reliability, availability and usability.

## 3. Test Case Design

Each test case contains an identifier, related requirement, objective, preconditions, input or test data, execution steps and expected result.

### 3.1 Authentication and Access Control

| Test Case ID | Requirement | Objective | Input / Condition | Expected Result |
|---|---|---|---|---|
| TC-Auth-01 | ESIMS-F-001 | Verify valid login | Valid username and password | User is authenticated and redirected to the dashboard. |
| TC-Auth-02 | ESIMS-F-002 | Verify invalid login | Incorrect username or password | Login is rejected and an appropriate error message is displayed. |
| TC-Auth-03 | ESIMS-SR-001 | Verify logout | Authenticated user selects logout | User session ends and protected pages require authentication again. |

### 3.2 Product Management

| Test Case ID | Requirement | Objective | Input / Condition | Expected Result |
|---|---|---|---|---|
| TC-Prod-01 | ESIMS-F-003 | Add a product | Valid product name, category, SKU and price | Product is successfully created and stored. |
| TC-Prod-02 | ESIMS-F-004 | Update product details | Existing product with modified details | Updated information is saved and displayed correctly. |
| TC-Prod-03 | ESIMS-D-001 | Reject duplicate SKU | Product submitted with an existing SKU | Product creation is rejected and no duplicate record is created. |
| TC-Prod-04 | Product Management | Deactivate a product | Existing active product | Product is deactivated without physically deleting its historical records. |

### 3.3 Inventory Management

| Test Case ID | Requirement | Objective | Input / Condition | Expected Result |
|---|---|---|---|---|
| TC-Inv-01 | ESIMS-F-005 | View stock quantity | Existing product | Correct available stock quantity is displayed. |
| TC-Inv-02 | ESIMS-F-006 | Search products | Product name or SKU | Matching products are displayed. |
| TC-Inv-03 | ESIMS-F-007 | Identify low-stock products | Product quantity at or below reorder level | Product is identified as low stock. |
| TC-Inv-04 | ESIMS-F-008 | Prevent negative stock | Sale quantity greater than available stock | Transaction is rejected and stock remains unchanged. |
| TC-Inv-05 | ESIMS-F-008, ESIMS-NF-002 | Verify concurrent stock handling | Two simultaneous sale requests for a product with one unit remaining | Exactly one sale succeeds, the other is rejected, and stock never becomes negative. |
| TC-Inv-06 | ESIMS-NF-002 | Verify inventory after transactions | Purchase and sale transactions for an existing product | Inventory displays the correct updated quantity. |

### 3.4 Supplier Management

| Test Case ID | Requirement | Objective | Input / Condition | Expected Result |
|---|---|---|---|---|
| TC-Sup-01 | ESIMS-F-009 | Add and update supplier | Valid supplier details | Supplier information is successfully saved or updated. |
| TC-Sup-02 | Supplier Management | Deactivate a supplier | Existing active supplier | Supplier is deactivated while historical purchase records remain preserved. |

### 3.5 Purchase Management

| Test Case ID | Requirement | Objective | Input / Condition | Expected Result |
|---|---|---|---|---|
| TC-Pur-01 | ESIMS-F-010 | Record a purchase | Valid supplier, product and purchase quantity | Purchase transaction is successfully recorded. |
| TC-Pur-02 | ESIMS-F-011 | Verify stock increase | Existing stock and a valid purchase quantity | Inventory increases by exactly the purchased quantity. |
| TC-Pur-03 | ESIMS-F-010, ESIMS-F-011 | View purchase details | Existing purchase record | Purchase details and associated purchase items are displayed correctly. |
| TC-Pur-04 | ESIMS-NF-002 | Verify purchase transaction consistency | Purchase operation encounters a failure during processing | Incomplete purchase and stock changes are rolled back; database records remain consistent. |

### 3.6 Sales Management

| Test Case ID | Requirement | Objective | Input / Condition | Expected Result |
|---|---|---|---|---|
| TC-Sale-01 | ESIMS-F-012 | Record a sale | Available product and valid sale quantity | Sale and associated sale items are successfully recorded. |
| TC-Sale-02 | ESIMS-F-013 | Verify sale total calculation | Known product prices and quantities | Sale total matches the calculated sum of item prices multiplied by quantities. |
| TC-Sale-03 | ESIMS-F-014 | Verify stock deduction | Existing stock and a valid sale | Inventory decreases by exactly the quantity sold. |
| TC-Sale-04 | ESIMS-F-012 | View sale details | Existing sale record | Sale details and associated sale items are displayed correctly. |
| TC-Sale-05 | ESIMS-NF-002 | Verify sale transaction consistency | Sale operation encounters a failure during processing | Incomplete sale and stock changes are rolled back; database records remain consistent. |

### 3.7 Reporting

| Test Case ID | Requirement | Objective | Input / Condition | Expected Result |
|---|---|---|---|---|
| TC-Report-01 | ESIMS-F-015 | Generate inventory report | Existing products and stock quantities | Report displays current product and inventory information. |
| TC-Report-02 | ESIMS-F-016 | Generate sales report | Selected date or date range | Report displays sales records corresponding to the selected period. |

### 3.8 Non-Functional Testing

| Test Case ID | Requirement | Objective | Input / Condition | Expected Result |
|---|---|---|---|---|
| TC-Perf-01 | ESIMS-NF-001 | Verify response time | Product search and inventory lookup under normal load | At least 90% of tested requests complete within 3 seconds. |
| TC-Rel-01 | ESIMS-NF-002 | Verify inventory consistency | Sequence of purchase and sales transactions | Final stock quantities remain correct, with no partial transaction updates. |
| TC-Avail-01 | ESIMS-NF-003 | Verify availability | Application running in the normal test environment | Application remains accessible during testing. |
| TC-UX-01 | ESIMS-NF-004 | Verify usability | Common user operations | Users can complete common tasks without critical usability errors. |
| TC-Sec-01 | ESIMS-NF-005 | Verify data protection | Unauthorized access or modification attempt | Unauthorized operation is rejected. |

### 3.9 Security Testing

| Test Case ID | Requirement | Objective | Input / Condition | Expected Result |
|---|---|---|---|---|
| TC-Sec-02 | ESIMS-SR-001 | Verify authentication enforcement | Unauthenticated user attempts to access a protected page | Access is denied or the user is redirected to login. |
| TC-Sec-03 | ESIMS-SR-002 | Verify role restrictions | Store Staff attempts product or supplier management; Administrator attempts the same operations | Store Staff receives HTTP 403 for restricted operations; Administrator access is allowed. |
| TC-Sec-04 | ESIMS-SR-003 | Verify password hashing | Inspect stored user credentials | Passwords are stored as hashes rather than plaintext. |
| TC-Sec-05 | ESIMS-SR-004 | Verify input validation | Malformed or invalid form data | Invalid input is safely rejected with suitable validation feedback. |
| TC-Sec-06 | ESIMS-SR-005 | Verify transaction protection | Unauthorized update or delete attempt | Operation is rejected and existing records remain unchanged. |
| TC-Sec-07 | ESIMS-SR-004 | Verify server-side sale total integrity | Sale request containing a client-modified unit price or total | Server recalculates the total using stored product prices and does not persist the tampered value. |

Role-based authorization is implemented with two roles: **Administrator** and
**Store Staff**. Administrators may manage products and suppliers. Store Staff
may view products and suppliers and perform inventory, purchase, sales and
reporting operations, but cannot create, edit or deactivate products or add or
edit suppliers.

### 3.10 User Interface and Integration Testing

| Test Case ID | Requirement | Objective | Input / Condition | Expected Result |
|---|---|---|---|---|
| TC-UI-01 | ESIMS-NF-004 | Verify application navigation | Navigate between available modules | Correct pages open and common navigation remains consistent. |
| TC-UI-02 | ESIMS-NF-004 | Verify user feedback | Submit valid and invalid forms | Suitable success or error messages are displayed. |

---

## 4. Test Data

The following sample data can be used for functional and system testing.

| Data Item | Sample Value |
|---|---|
| Product Name | SV Test Keyboard |
| Product SKU | SV-TEST-001 |
| Product Unit Price | 750.00 |
| Reorder Level | 5 |
| Supplier Name | SV Test Suppliers |
| Purchase Quantity | 5 |
| Sale Quantity | 2 |
| Invalid Sale Quantity | Greater than available stock |
| Product Search | Product name or SKU |
| Report Filter | Selected date range |
| Duplicate SKU | Existing product SKU |

Only dummy test data should be used during testing.

## 5. Test Execution and Result Recording

Test cases are designed to verify the functionality and requirements of the ESIMS application. Execution results and supporting evidence are maintained in the corresponding test reports.

The following fields are used when recording individual test execution results:

- Test Case ID
- Execution Date
- Preconditions
- Test Input
- Actual Result
- Expected Result
- Status (Pass/Fail/Not Executed)
- Defect ID, if applicable
- Evidence or screenshot reference

The automated unit test results are documented in the Unit Test Report. Manual system-level execution results are documented in the System Validation Report. Code and branch coverage results are documented in their respective coverage reports.

## 6. Sprint-wise Test Coverage

| Sprint | Features Covered | Related Test Cases |
|---|---|---|
| Sprint 1 | Database models, authentication, product management, supplier management, inventory viewing, validation and deactivation | TC-Auth, TC-Prod, TC-Inv, TC-Sup |
| Sprint 2 | Purchase transactions, sales transactions, automatic stock updates, reporting, integration, security and non-functional testing | TC-Pur, TC-Sale, TC-Report, TC-Sec, TC-Perf, TC-Rel, TC-Avail, TC-UX, TC-UI |

## 7. Requirements Traceability Summary

| Requirement | Related Test Cases |
|---|---|
| ESIMS-F-001 | TC-Auth-01 |
| ESIMS-F-002 | TC-Auth-02 |
| ESIMS-F-003 | TC-Prod-01 |
| ESIMS-F-004 | TC-Prod-02 |
| ESIMS-D-001 | TC-Prod-03 |
| ESIMS-F-005 | TC-Inv-01 |
| ESIMS-F-006 | TC-Inv-02 |
| ESIMS-F-007 | TC-Inv-03 |
| ESIMS-F-008 | TC-Inv-04, TC-Inv-05 |
| ESIMS-F-009 | TC-Sup-01 |
| ESIMS-F-010 | TC-Pur-01, TC-Pur-03 |
| ESIMS-F-011 | TC-Pur-02, TC-Pur-03 |
| ESIMS-F-012 | TC-Sale-01, TC-Sale-04 |
| ESIMS-F-013 | TC-Sale-02 |
| ESIMS-F-014 | TC-Sale-03 |
| ESIMS-F-015 | TC-Report-01 |
| ESIMS-F-016 | TC-Report-02 |
| ESIMS-NF-001 | TC-Perf-01 |
| ESIMS-NF-002 | TC-Inv-05, TC-Inv-06, TC-Pur-04, TC-Sale-05, TC-Rel-01 |
| ESIMS-NF-003 | TC-Avail-01 |
| ESIMS-NF-004 | TC-UX-01, TC-UI-01, TC-UI-02 |
| ESIMS-NF-005 | TC-Sec-01 |
| ESIMS-SR-001 | TC-Auth-03, TC-Sec-02 |
| ESIMS-SR-002 | TC-Sec-03 |
| ESIMS-SR-003 | TC-Sec-04 |
| ESIMS-SR-004 | TC-Sec-05, TC-Sec-07 |
| ESIMS-SR-005 | TC-Sec-06 |

## 8. Conclusion

The updated test case document incorporates the functional and non-functional requirements of ESIMS along with the implementation work completed during Sprint 1 and Sprint 2.

It includes test coverage for authentication, product and supplier management, inventory, purchase and sales transactions, reporting, database consistency, security, and user interface integration.

The updated test cases provide a structured basis for verifying the application and maintaining traceability between requirements, implementation and testing activities.