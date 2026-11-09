# System Validation Report

## 1. Introduction

This report documents the manual system validation performed for the Electronics Store Inventory Management System (ESIMS) on 6 November 2026.

The objective was to verify the integrated application's functionality through browser-based testing, including authentication, product and supplier management, inventory operations, purchase and sales transactions, reporting, navigation and validation.

## 2. Testing Environment

- Project: Electronics Store Inventory Management System
- Testing type: Manual system validation
- Interface: Web browser
- Application: Local development instance
- Testing date: 6 November 2026
- Test data: Dedicated test product and supplier

## 3. Test Execution Summary

| Metric | Result |
|---|---:|
| Total manual test cases | 40 |
| Passed | 40 |
| Failed | 0 |
| Not executed | 0 |

## 4. Detailed Test Results

| Test Case ID | Feature | Actual Result | Status |
|---|---|---|---|
| SV-01 | Valid login | Dashboard displayed after successful login. | Passed |
| SV-02 | Invalid login | Invalid credentials were rejected and an error message appeared. | Passed |
| SV-03 | Logout | User session ended and login page was displayed. | Passed |
| SV-04 | Protected route | Unauthenticated access was redirected to login. | Passed |
| SV-05 | Login after logout | User could log in again successfully. | Passed |
| SV-06 | Add product | Product was created successfully. | Passed |
| SV-07 | View product | Newly created product appeared in the listing. | Passed |
| SV-08 | Edit product | Updated product details were saved. | Passed |
| SV-09 | Search by name | Matching product was displayed. | Passed |
| SV-10 | Search by SKU | Matching product was displayed. | Passed |
| SV-11 | Invalid product | Invalid product details were rejected with validation feedback. | Passed |
| SV-12 | Deactivate product | Product was successfully deactivated. | Passed |
| SV-13 | Add supplier | Supplier was created successfully. | Passed |
| SV-14 | View supplier | Newly created supplier appeared in the listing. | Passed |
| SV-15 | Edit supplier | Updated supplier details were saved. | Passed |
| SV-16 | Invalid supplier | Missing supplier name was rejected. | Passed |
| SV-17 | Inventory listing | Inventory information was displayed. | Passed |
| SV-18 | Inventory search by name | Matching inventory item was displayed. | Passed |
| SV-19 | Inventory search by SKU | Matching inventory item was displayed. | Passed |
| SV-20 | Low-stock detection | Products meeting the low-stock condition were displayed. | Passed |
| SV-21 | Stock quantity verification | Inventory quantities were consistent with recorded operations. | Passed |
| SV-22 | Purchase creation | Purchase transaction was recorded successfully. | Passed |
| SV-23 | Purchase stock update | Inventory increased by the purchased quantity. | Passed |
| SV-24 | Purchase details | Recorded purchase information was displayed correctly. | Passed |
| SV-25 | Invalid purchase | Invalid purchase quantity was rejected without changing stock. | Passed |
| SV-26 | Sale creation | Sale transaction was recorded successfully. | Passed |
| SV-27 | Sale stock update | Inventory decreased by the sold quantity. | Passed |
| SV-28 | Sale details | Recorded sale details and total were displayed. | Passed |
| SV-29 | Insufficient stock | Sale exceeding available stock was rejected without changing stock. | Passed |
| SV-30 | Invalid sale quantity | Invalid sale quantity was rejected. | Passed |
| SV-31 | Stock movement | Stock movements were verified for purchase and sale operations. | Passed |
| SV-32 | Inventory report | Inventory report displayed the available information. | Passed |
| SV-33 | Inventory report totals | Inventory totals were consistent with inventory data. | Passed |
| SV-34 | Sales report | Recorded sales were displayed. | Passed |
| SV-35 | Sales report date filter | Sales within the selected date range were displayed. | Passed |
| SV-36 | Empty sales report | Appropriate message was displayed when no sales matched the selected range. | Passed |
| SV-37 | Navigation | Major application modules opened through navigation successfully. | Passed |
| SV-38 | UI consistency | Updated interface elements were displayed consistently. | Passed |
| SV-39 | Form validation | Invalid form inputs produced validation feedback. | Passed |
| SV-40 | Session security | Protected pages could not be accessed after logout. | Passed |

## 5. Test Data

The following dedicated test data was used during validation:

- Product: SV Test Keyboard
- SKU: SV-TEST-001
- Unit price: 750.00
- Reorder level: 5
- Supplier: SV Test Suppliers
- Purchase quantity: 5 units
- Sale quantity: 2 units

The expected inventory change was verified through the purchase and sales workflows.

## 6. Observations

- Authentication and session handling worked as expected.
- Product and supplier management operations were successful.
- Product search supported both name and SKU.
- Inventory and low-stock information was displayed correctly.
- Purchase transactions increased available stock.
- Sales transactions decreased available stock.
- Insufficient-stock and invalid-quantity scenarios were handled correctly.
- Inventory and sales reports displayed the expected information.
- Navigation and updated UI components worked correctly.

## 7. Evidence

Browser-based validation was performed for all listed test cases. Supporting screenshots should be retained in `docs/testing/evidence/`, where available, covering authentication, product and supplier management, inventory, purchase and sales transactions, reports and validation messages.

## 8. Conclusion

The manual system validation covered 40 test cases across the major application modules. All 40 test cases were reported as passed, with no failures.

The application successfully demonstrated its integrated functionality, including authentication, product and supplier management, inventory tracking, purchase and sales processing, stock validation and report generation.

Based on the completed manual validation, the application satisfied the tested functional workflows.