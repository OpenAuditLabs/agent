# Schema Validation Rules for ItemCreate and ItemUpdate

This document outlines the validation rules applied to `ItemCreate` and `ItemUpdate` schemas, including `min_length` and `max_length` constraints, and their implications for API consumers.

## Purpose of Validation Rules

The `min_length` and `max_length` constraints are implemented to:
*   **Ensure Data Integrity:** Maintain consistency and quality of data stored in the system.
*   **Align with Database Schema:** Database-level enforcement of these constraints is a pending task and requires separate implementation (e.g., using an ORM with migrations). This will ensure that `name` (VARCHAR(50)) and `description` (VARCHAR(500)) constraints for the Item entity are enforced at the database level. A follow-up task will be created to track this work.
*   **Enforce Business Rules:** Reflect specific business requirements regarding the acceptable length of item names and descriptions.

## ItemCreate Schema Validation

When creating a new item, the following rules apply:

* **`name` (string, required):**
  * Must have a minimum length of `3` characters.
  * Must have a maximum length of `50` characters.
* **`description` (string, optional):**
  * If provided, must have a minimum length of `10` characters.
  * If provided, must have a maximum length of `500` characters.
  * Empty strings (`""`) are **not** considered valid if a description is provided. To omit a description, do not include the field or send `null`.

## ItemUpdate Schema Validation

When updating an existing item, the following rules apply:

* **`name` (string, optional):**
  * Must have a minimum length of `3` characters.
  * Must have a maximum length of `50` characters.
  * Empty strings (`""`) are **not** considered valid for updating the name. To clear the name, `null` must be explicitly sent.
* **`description` (string, optional):**
  * Must have a minimum length of `10` characters.
  * Must have a maximum length of `500` characters.
  * Empty strings (`""`) are **not** considered valid for updating the description. To clear the description, `null` must be explicitly sent.
* **Partial Update Semantics:**
  * The `ItemUpdate` schema enforces that at least one of `name` or `description` must be provided in the request body. An update request with an empty body or only `null` values for both fields will be rejected.
  * **Important Behavioral Change:** Unlike some partial update patterns, sending an empty string (`""`) for an optional field like `name` or `description` will result in a validation error due to the `min_length` constraint. To explicitly remove or clear the value of an optional field, clients **must** send `null` for that field.

## Impact on Existing Clients and Justification

The introduction of `min_length` and `max_length` constraints, along with the stricter handling of empty strings for optional fields in `ItemUpdate`, represents a **breaking change** for any clients that:
*   Send `name` values shorter than 3 or longer than 50 characters.
*   Send `description` values shorter than 10 or longer than 500 characters.
*   Attempt to clear optional fields (`name`, `description`) in `ItemUpdate` by sending an empty string (`""`).

**Justification:** These changes are intentional to enforce data quality and consistency at the API boundary. By rejecting invalid lengths and clarifying the mechanism for clearing optional fields (using `null`), the API promotes more robust data handling and reduces ambiguity.

**Action Required for Clients:**
Clients consuming these endpoints must be updated to adhere to the new validation rules. Specifically, for `ItemUpdate`, ensure that `null` is sent to clear optional fields, rather than an empty string.

## Further Verification

It is crucial to:
1.  **Verify Database Alignment:** Confirm that the `min_length` and `max_length` values specified in the schemas accurately reflect the column sizes and constraints in the underlying database.
2.  **Confirm Business Rules:** Validate these length constraints with business stakeholders to ensure they align with current and future business requirements.
