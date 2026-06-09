# Parse, Don't Validate

Refactoring strategies for replacing scattered defensive checks with stronger data
representations. Load when code has repeated null/status/length checks, weak input
types, or validation logic mixed into business logic.

Based on Alexis King's "Parse, don't validate" (2019). The core insight: a parser
is just a function that consumes less-structured input and produces more-structured
output. Validation that discards its proof is wasted work.

**When not to apply:** Not every primitive needs a wrapper type. Creating bespoke
types for every string in the codebase leads to type proliferation without payoff.
Apply this principle where repeated defensive checks or actual bugs exist, not
prophylactically everywhere. If a value is only checked once and never rechecked,
a plain validation function is fine.

## Contents

1. [Strengthen Inputs, Don't Weaken Outputs](#1-strengthen-inputs-dont-weaken-outputs)
2. [Eliminate Shotgun Validation](#2-eliminate-shotgun-validation)
3. [Push Parsing to Boundaries](#3-push-parsing-to-boundaries)
4. [Replace Booleans and Strings with Sum Types](#4-replace-booleans-and-strings-with-sum-types)
5. [Propagate Stronger Types Outward](#5-propagate-stronger-types-outward)
6. [Smart Constructors for Validation](#6-smart-constructors-for-validation)

---

## 1. Strengthen Inputs, Don't Weaken Outputs

When a function cannot handle all inputs, strengthen what it accepts rather than
weakening what it returns. This pushes the burden of proof to callers, where it
belongs.

```diff
# BAD: Weaken the return type to handle impossible cases
- function getFirst(items: string[]): string | undefined {
-   return items[0];
- }
-
- // Caller must handle undefined even when it "knows" the list is non-empty
- const dir = getFirst(configDirs);
- if (dir === undefined) throw new Error('should never happen');

# GOOD: Strengthen the input type to make impossible cases unrepresentable
+ type NonEmptyArray<T> = [T, ...T[]];
+
+ function getFirst<T>(items: NonEmptyArray<T>): T {
+   return items[0];
+ }
+
+ // Caller proves non-emptiness once; no defensive check needed downstream
+ const dir = getFirst(configDirs); // configDirs is NonEmptyArray<string>
```

Apply when functions return `T | undefined` or `T | null` and callers routinely
discard the failure case with comments like "should never happen."

---

## 2. Eliminate Shotgun Validation

Shotgun validation scatters checks throughout business logic. Each function
re-verifies assumptions that should have been established once at admission time.

```diff
# BAD: Every function re-checks the same assumptions
- function calculateTotal(order: Order) {
-   if (!order.items || order.items.length === 0) throw new Error('No items');
-   if (!order.customer) throw new Error('No customer');
-   return order.items.reduce((sum, item) => sum + item.price, 0);
- }
-
- function applyDiscount(order: Order) {
-   if (!order.items || order.items.length === 0) throw new Error('No items');
-   if (!order.customer) throw new Error('No customer');
-   const rate = getDiscountRate(order.customer.tier);
-   return calculateTotal(order) * (1 - rate);
- }

# GOOD: Parse once at the boundary, then trust the structure
+ interface ValidatedOrder {
+   items: NonEmptyArray<OrderItem>;
+   customer: Customer;  // not optional
+ }
+
+ function parseOrder(raw: Order): ValidatedOrder {
+   if (!raw.items || raw.items.length === 0) throw new Error('No items');
+   if (!raw.customer) throw new Error('No customer');
+   return { items: raw.items as NonEmptyArray<OrderItem>, customer: raw.customer };
+ }
+
+ function calculateTotal(order: ValidatedOrder) {
+   return order.items.reduce((sum, item) => sum + item.price, 0);
+ }
+
+ function applyDiscount(order: ValidatedOrder) {
+   const rate = getDiscountRate(order.customer.tier);
+   return calculateTotal(order) * (1 - rate);
+ }
```

Apply when two or more functions repeat the same defensive checks on the same data.
The checks should live in one parse function; everything downstream trusts the result.

---

## 3. Push Parsing to Boundaries

Parse into the strongest useful representation as early as possible, ideally at the
system boundary (API handler, CLI entry, file reader) before any business logic runs.
The rule: as far outward as possible, but no further.

```diff
# BAD: Parsing buried deep in business logic
- // controller.ts
- function handleRequest(body: unknown) {
-   processOrder(body as Order);  // hope for the best
- }
-
- // service.ts — validation buried here
- function processOrder(order: Order) {
-   if (!order.id) throw new Error('Missing ID');
-   if (!order.items?.length) throw new Error('No items');
-   // ... business logic mixed with checks
- }

# GOOD: Parse at the boundary, business logic receives strong types
+ // controller.ts — parsing happens here
+ function handleRequest(body: unknown) {
+   const order = parseOrderRequest(body);  // throws if invalid
+   processOrder(order);
+ }
+
+ // service.ts — receives already-parsed data, no defensive checks
+ function processOrder(order: ValidatedOrder) {
+   // pure business logic, no validation needed
+ }
```

Apply when validation logic is interleaved with processing logic. Separate the two
phases: parsing (which can fail) runs first, execution (which trusts its inputs) runs
second.

---

## 4. Replace Booleans and Strings with Sum Types

Booleans and free-form strings often mask richer state models. When multiple flags
interact, they can represent illegal combinations that the type system should prevent.

```diff
# BAD: Boolean flags allow illegal state combinations
- interface Document {
-   isApproved: boolean;
-   isPublished: boolean;
-   isArchived: boolean;
-   // Can a document be archived AND published? Approved but not published?
-   // The type allows all 8 combinations; only 4 are valid.
- }

# GOOD: Sum type makes illegal states unrepresentable
+ type DocumentStatus =
+   | { kind: 'draft' }
+   | { kind: 'approved'; approvedBy: string }
+   | { kind: 'published'; publishedAt: Date }
+   | { kind: 'archived'; archivedAt: Date };
+
+ interface Document {
+   status: DocumentStatus;
+   // Exactly 4 states. No illegal combinations possible.
+ }
```

Apply when you see multiple boolean or string fields that represent a state machine,
especially when code checks combinations like `if (isApproved && !isPublished)`.

---

## 5. Propagate Stronger Types Outward

Refactoring toward stronger types is iterative. Start at the function that suffers
most from weak inputs, strengthen its signature, then let type errors guide you
outward to the source of the data.

```diff
# Step 1: Change the function you care about
- function processItems(items: Array<[string, number]>) {
-   // must check for duplicate keys every time
- }
+ function processItems(items: Map<string, number>) {
+   // duplicates impossible by construction
+ }

# Step 2: Compiler error at call site reveals the next change needed
- const data: Array<[string, number]> = fetchData();
- processItems(data);  // ERROR: Array<[string, number]> not assignable to Map

# Step 3: Insert parsing at the source
+ function parseToPriceMap(
+   pairs: Array<[string, number]>
+ ): Map<string, number> {
+   const map = new Map(pairs);
+   if (map.size !== pairs.length) {
+     throw new Error('Duplicate keys detected');
+   }
+   return map;
+ }
+
+ const data = parseToPriceMap(fetchData());
+ processItems(data);  // works; duplicates already handled
```

This is the recommended refactoring sequence: change one signature, follow the
compiler errors, insert the parse step where the data originates. Repeat for the
next invariant.

---

## 6. Smart Constructors for Validation

When encoding an invariant fully in the type system is impractical (e.g. "string
that is a valid email," "integer between 1 and 100"), use an opaque type with a
static parse method. The constructor is private; the only way to get a value is
through the parser.

```diff
# BAD: Email is just a string; validation can be skipped or duplicated
- function sendEmail(to: string, subject: string) {
-   if (!isValidEmail(to)) throw new Error('Invalid email');
-   // ...
- }

# GOOD: EmailAddress type guarantees validity by construction
+ class EmailAddress {
+   private constructor(public readonly value: string) {}
+
+   static parse(input: string): EmailAddress {
+     if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input)) {
+       throw new Error(`Invalid email: ${input}`);
+     }
+     return new EmailAddress(input);
+   }
+ }
+
+ function sendEmail(to: EmailAddress, subject: string) {
+   // no validation needed; EmailAddress is always valid
+ }
```

Apply when a domain concept has validation rules that cannot be expressed through
TypeScript's structural type system alone. The smart constructor "fakes" a parser
from a validator by making the validated type opaque.
