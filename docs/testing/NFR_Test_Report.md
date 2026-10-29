## 7. Availability and Usability

### Availability

A basic manual availability check was performed by accessing available application pages and refreshing them during a test session. The pages remained accessible during this check.

This provides limited evidence of availability during the test session. Sustained availability, recovery after failures, and behavior under extended operation have not been established.

### Usability

Basic manual checks were performed on the available application interfaces, including login, inventory viewing, product search, low-stock viewing, and available product, supplier, and purchase forms. These interfaces appeared to function during testing.

Integrated navigation between pages and logout behavior still require verification after the relevant application pages are connected. Sales-related workflows and other unfinished features must also be tested when available.

These checks provide preliminary usability evidence but do not establish that all common tasks can be completed without critical usability errors.

## 8. Conclusion

The automated test suite completed with 79 passing tests and 3 skipped tests. All three measured inventory endpoints satisfied the 3-second response-time threshold under the isolated performance-testing conditions.

Existing automated tests also passed for the purchase, inventory, authentication, and validation behaviors they cover.

A basic manual availability check and preliminary usability checks were completed for the currently available interfaces. However, sustained availability, integrated navigation, complete usability verification, sales-related reliability, concurrent transactions, and database-specific checks skipped during testing require further verification.

The results demonstrate progress toward the project's non-functional requirements, but they do not establish that every NFR has been fully verified.