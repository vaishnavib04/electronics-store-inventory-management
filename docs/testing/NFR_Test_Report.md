# Non-Functional Requirements (NFR) Test Report

## 1. Objective

The objective of NFR testing is to evaluate the performance, security, reliability, and usability of the Electronics Store Inventory Management System.

## 2. Test Environment

- Application: Electronics Store Inventory Management System (ESIMS)
- Framework: Flask
- Database: SQLite in-memory database for performance tests
- Testing framework: pytest
- Python version: 3.15.0
- Test branch: `feature/nfr-testing`

## 3. Performance Testing

### Requirement

Common inventory operations should respond within 3 seconds under normal testing conditions.

### Test Method

An authenticated Flask test client was used with 100 sample products. Each inventory endpoint was requested five times after a warm-up request. Average and maximum response times were measured using Python's `time.perf_counter()`.

### Results

| Endpoint | Requests Measured | Average Response Time | Maximum Response Time | Result |
|---|---:|---:|---:|---|
| `/inventory` | 5 | 0.0019 s | 0.0023 s | PASS |
| `/inventory?q=NFR-050` | 5 | 0.0006 s | 0.0009 s | PASS |
| `/inventory/low-stock` | 5 | 0.0007 s | 0.0008 s | PASS |

### Observation

All three inventory operations responded within the required 3-second limit during testing. The maximum observed response time was 0.0023 seconds.

These measurements represent an isolated test environment and do not establish performance under production traffic or concurrent user load.

## 4. Automated Test Suite

The complete automated test suite was executed using pytest.

Command:

`py -m pytest`

Result:

- 79 tests passed.
- 3 tests skipped.
- 375 warnings reported.
- Total execution time: 3.16 seconds.

The skipped tests require separate verification of the relevant database environment before their results can be considered validated.

## 5. Security Testing

Existing automated tests cover authentication requirements for inventory, product, supplier, and purchase routes. Tests also cover product deactivation and input validation in relevant modules.

The complete suite passed. This provides evidence for the security behaviors covered by those tests but does not establish that every route or authorization scenario has been tested.

## 6. Inventory Consistency and Transaction Testing

Existing purchase and inventory tests cover inventory quantity updates, purchase totals, purchase items, and stock movement records. Invalid purchase inputs are also tested to ensure invalid transactions do not create corresponding records.

The current results demonstrate the behaviors covered by these automated tests. Additional failure-injection and concurrent transaction testing may be required to establish rollback and concurrency behavior comprehensively.

## 7. Availability and Usability

Availability under sustained operation and usability through manual user-task testing have not yet been established by the recorded results.

These areas require additional testing and documentation before they can be marked as fully verified.

## 8. Conclusion

The automated test suite completed with 79 passing tests and 3 skipped tests. All three measured inventory endpoints satisfied the 3-second response-time requirement in the isolated performance-testing environment.

Further testing is needed to assess sustained availability, usability, concurrent transactions, and any database-specific checks skipped in the current run.