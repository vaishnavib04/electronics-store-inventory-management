## 7. Availability and Usability

### Availability

A basic manual availability check was performed by accessing available application pages and refreshing them during a test session. The pages remained accessible during this check.

This provides limited evidence of availability during the test session. Sustained availability, recovery after failures, and behavior under extended operation have not been established.

### Usability

Manual browser checks covered login, inventory viewing, product search, low-stock viewing, product creation/editing, supplier creation/editing, purchase, sales, reports, navigation, and logout. The tested workflows completed without critical usability errors.

These checks provide practical usability evidence, but they do not establish formal user-study metrics.

## 8. Automated NFR Test Results

The focused NFR suite contains 20 tests in [`test_nfr_performance.py`](../../tests/test_nfr_performance.py) and [`test_nfr_security.py`](../../tests/test_nfr_security.py). It verifies the 90% response-time criterion for inventory and product reads, purchase and sales recording, protected routes, inactive-user rejection, password hashing, invalid input handling, logout session invalidation, and unauthenticated modification attempts.

The focused suite completed with 20 passing tests. The complete automated suite completed with 169 passing tests and 3 skipped MySQL-specific tests. Performance results apply to the isolated SQLite test fixture and the measured requests only.

## 9. Conclusion

The focused NFR suite passed all 20 tests. Existing module tests also cover purchase, sales, inventory, authentication, and validation behavior.

A basic manual availability check and browser usability checks were completed for the currently available interfaces. However, sustained availability, formal usability-study metrics, role-specific authorization, concurrent transactions, and database-specific checks skipped during testing require further verification.

The application is accessed through `/login`; the root `/` route currently returns 404 because no root route is defined. The results demonstrate progress toward the project's non-functional requirements, but role-specific authorization and continuous availability are not fully verified.