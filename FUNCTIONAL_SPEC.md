# Campus Supply Desk: Functional Requirements

Use these requirements when designing tests and evaluating the application's behavior. The starter implementation may not satisfy every requirement.

For your System Understanding Note, inspect the implementation and explain the system in your own words, supported by references to its files, components, and execution flow.

## Scope boundaries

- Each order has status `placed` or `cancelled`.
- Shipping workflows, payment processing, taxes, authentication, and customer personal information are outside scope.
- Only one running instance should use a given save file at a time.
- These limits are deliberate. You are not expected to add the excluded features.
- A later client change request may extend these requirements.

## Catalog

Each product has a stable product ID, display name, unit price in integer Canadian cents, and a nonnegative available-stock quantity.

A new save file starts with these products:

- **Notebook**
  - Product ID: `notebook`
  - Unit price: 500 cents ($5.00 CAD)
  - Initial stock: 20

- **Pen pack**
  - Product ID: `pen-pack`
  - Unit price: 750 cents ($7.50 CAD)
  - Initial stock: 10

- **Campus hoodie**
  - Product ID: `hoodie`
  - Unit price: 4,000 cents ($40.00 CAD)
  - Initial stock: 5

- **Campus mug**
  - Product ID: `mug`
  - Unit price: 1,500 cents ($15.00 CAD)
  - Initial stock: 8

- **Canvas bag**
  - Product ID: `bag`
  - Unit price: 2,500 cents ($25.00 CAD)
  - Initial stock: 4

Viewing the catalog returns current stock without changing it. Catalog editing is outside the initial interface.

## Requests and validation

The service provides these operations:

```python
quote(customer_type, items, fulfillment="pickup")
place_order(customer_type, items, fulfillment="pickup")