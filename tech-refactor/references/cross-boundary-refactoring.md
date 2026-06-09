# Cross-Boundary Refactoring

Patterns for refactoring across module, package, or service boundaries. Load when
a refactoring touches more than one module or requires coordinated interface changes.

## Contents

1. [Extract Module](#1-extract-module)
2. [Move Function/Class to Better Home](#2-move-functionclass-to-better-home)
3. [Re-export for Backwards Compatibility](#3-re-export-for-backwards-compatibility)
4. [Expand-and-Contract Interface](#4-expand-and-contract-interface)
5. [Dependency Direction Cleanup](#5-dependency-direction-cleanup)
6. [Strangler Fig Pattern](#6-strangler-fig-pattern)
7. [Internal API Migration](#7-internal-api-migration)

---

## 1. Extract Module

```diff
# BAD: God module mixing unrelated concerns
- // utils/order-utils.ts
- export function validateOrder(order) { /* ... */ }
- export function calculateShipping(order) { /* ... */ }
- export function formatShippingLabel(shipment) { /* ... */ }
- export function checkInventory(items) { /* ... */ }
- export function reserveStock(items) { /* ... */ }
- export function calculateTax(order, region) { /* ... */ }

# GOOD: Each module owns one concern
+ // orders/validation.ts
+ export function validateOrder(order) { /* ... */ }
+
+ // shipping/calculator.ts
+ export function calculateShipping(order) { /* ... */ }
+ export function formatShippingLabel(shipment) { /* ... */ }
+
+ // inventory/stock.ts
+ export function checkInventory(items) { /* ... */ }
+ export function reserveStock(items) { /* ... */ }
+
+ // billing/tax.ts
+ export function calculateTax(order, region) { /* ... */ }
```

Split when a module has groups of functions that change for different reasons.
Shipping logic changes when carriers change; inventory logic changes when
warehouse rules change. Different rates of change signal different modules.

---

## 2. Move Function/Class to Better Home

```diff
# BAD: Function lives in module A but is used mostly by module B
- // auth/session.ts
- export function formatUserDisplayName(user: User): string {
-   return `${user.firstName} ${user.lastName}`.trim();
- }
-
- // profile/profile-card.ts
- import { formatUserDisplayName } from '../auth/session';
- // profile/settings.ts
- import { formatUserDisplayName } from '../auth/session';
- // profile/avatar.ts
- import { formatUserDisplayName } from '../auth/session';

# GOOD: Move to where it is most used
+ // profile/display.ts
+ export function formatUserDisplayName(user: User): string {
+   return `${user.firstName} ${user.lastName}`.trim();
+ }
+
+ // auth/session.ts — one import instead of three
+ import { formatUserDisplayName } from '../profile/display';
```

Count the import sites. If module B has 3+ imports and module A has 1,
the function probably belongs in B.

---

## 3. Re-export for Backwards Compatibility

```diff
# BAD: Move and break all consumers at once
- // Deleted from auth/session.ts, added to profile/display.ts
- // Every consumer now has a broken import

# GOOD: Re-export from old location during transition
+ // auth/session.ts — transitional re-export
+ /**
+  * @deprecated Moved to profile/display.ts. Remove this re-export by 2026-Q2.
+  */
+ export { formatUserDisplayName } from '../profile/display';
```

The re-export lets consumers migrate on their own schedule. Set a concrete
removal date so the bridge does not become permanent. Grep for the old import
path periodically to track remaining consumers.

---

## 4. Expand-and-Contract Interface

Use when a shared interface has multiple consumers and needs to evolve without
breaking them. Three phases: expand (add new alongside old), migrate (update
consumers), contract (remove old).

```diff
# Phase 1 — Expand: add new fields as optional
  interface OrderEvent {
    orderId: string;
-   timestamp: number;        // epoch millis — hard to work with
+   timestamp: number;        // deprecated, kept for compatibility
+   occurredAt?: Date;        // new: proper Date object
  }

# Phase 2 — Migrate: update all consumers to use new field
- const when = new Date(event.timestamp);
+ const when = event.occurredAt ?? new Date(event.timestamp);

# Phase 3 — Contract: remove old field once all consumers migrated
  interface OrderEvent {
    orderId: string;
-   timestamp: number;
-   occurredAt?: Date;
+   occurredAt: Date;         // now required, old field removed
  }
```

Never jump to Phase 3 until every consumer is migrated. Use a type-checker
or grep to verify zero remaining references to the old field.

---

## 5. Dependency Direction Cleanup

### Inverting a dependency

```diff
# BAD: Low-level module imports high-level module
- // database/connection.ts
- import { Logger } from '../app/logger';
-
- export class Connection {
-   query(sql: string) {
-     Logger.info(`Executing: ${sql}`);
-     // ...
-   }
- }

# GOOD: Depend on an abstraction, not the concrete logger
+ // database/types.ts
+ export interface LogSink {
+   info(message: string): void;
+ }
+
+ // database/connection.ts
+ import { LogSink } from './types';
+
+ export class Connection {
+   constructor(private log: LogSink) {}
+   query(sql: string) {
+     this.log.info(`Executing: ${sql}`);
+   }
+ }
+
+ // app/bootstrap.ts — wiring happens at the composition root
+ import { Logger } from './logger';
+ const conn = new Connection(Logger);
```

### Breaking circular dependencies

```diff
# BAD: A imports B, B imports A
- // orders/order.ts
- import { Invoice } from '../billing/invoice';
- // billing/invoice.ts
- import { Order } from '../orders/order';

# GOOD: Extract shared types into a neutral module
+ // shared/types.ts
+ export interface OrderSummary {
+   id: string;
+   total: number;
+   lineItems: LineItem[];
+ }
+
+ // orders/order.ts — imports shared types, not billing
+ import { OrderSummary } from '../shared/types';
+
+ // billing/invoice.ts — imports shared types, not orders
+ import { OrderSummary } from '../shared/types';
```

The neutral module should contain only types and interfaces, no behaviour.
This keeps it dependency-free.

---

## 6. Strangler Fig Pattern

Gradually replace legacy code by routing through a new implementation one
slice at a time. Avoids risky big-bang rewrites.

```diff
# BAD: Rewrite everything at once
- // Deleted legacy/payment-processor.ts (2000 lines)
- // Created new/payment-processor.ts (800 lines)
- // Hope nothing breaks

# GOOD: Facade routes traffic, migrate one payment type at a time
+ // payments/processor-facade.ts
+ import { legacyProcess } from '../legacy/payment-processor';
+ import { processCard } from './card-processor';
+
+ const NEW_PROCESSORS: Record<string, (payment: Payment) => Promise<Result>> = {
+   credit_card: processCard,
+   // Add more as they are ready:
+   // debit: processDebit,
+   // wire: processWire,
+ };
+
+ export async function processPayment(payment: Payment): Promise<Result> {
+   const handler = NEW_PROCESSORS[payment.type];
+   if (handler) {
+     return handler(payment);    // new path
+   }
+   return legacyProcess(payment); // old path — shrinks over time
+ }
```

Each new handler is independently testable. The legacy code is never modified,
only bypassed. Once all payment types route to new handlers, delete the legacy
module.

---

## 7. Internal API Migration

```diff
# BAD: Delete old function, break all callers
- export function createUser(name: string, email: string) { /* ... */ }
- // 47 call sites now broken

# GOOD: Deprecate and forward
+ /**
+  * @deprecated Use createUserAccount instead. Will be removed 2026-Q3.
+  */
+ export function createUser(name: string, email: string): User {
+   return createUserAccount({ name, email });
+ }
+
+ export function createUserAccount(params: CreateUserParams): User {
+   // new implementation with richer parameter object
+ }
```

For complex signature changes, add an adapter layer:

```diff
# Adapter for callers that cannot migrate immediately
+ export function adaptLegacyCreateUser(
+   name: string,
+   email: string,
+   role?: string
+ ): CreateUserParams {
+   return {
+     name,
+     email,
+     role: role ?? 'member',
+     source: 'legacy-adapter',
+   };
+ }
```

The adapter makes the mapping explicit and testable. Grep for adapter usage
to track migration progress.
