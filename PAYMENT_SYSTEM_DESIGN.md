# Eaglens Subscription and Payment System Design

This document outlines the architecture for implementing an invite-only access model and integrating Paystack for subscription management.

## 1. Access Control and Invite System

### 1.1 User Data Model
A new SQLite database table (`users`) will be used to store user-specific access information.

| Field | Data Type | Description |
| :--- | :--- | :--- |
| `telegram_id` | INTEGER (PK) | Unique Telegram user ID. |
| `invite_code` | TEXT | The one-time code used for registration. |
| `is_subscribed` | BOOLEAN | True if the user has an active subscription. |
| `expiry_date` | TEXT (ISO 8601) | Date and time when the subscription expires. |
| `trial_used` | BOOLEAN | True if the user has used the $7.99 trial. |

### 1.2 Invite Code Logic
1.  **Generation**: A separate utility will be needed to generate and manage a pool of one-time invite codes.
2.  **Verification**: On the `/start` command, if the user is not in the `users` table, the bot will prompt for an invite code.
3.  **Access**: Only users with a valid, unused invite code can proceed to the payment/trial initiation stage.

## 2. Paystack Integration

### 2.1 Pricing Structure
| Plan | Price (USD) | Duration | Paystack Plan Code |
| :--- | :--- | :--- | :--- |
| **Monthly Subscription** | $349.00 | 1 Month | `PLAN_MONTHLY` (to be created) |
| **One-Month Trial** | $7.99 | 1 Month | `PLAN_TRIAL` (to be created) |

*Note: Paystack primarily handles Nigerian Naira (NGN) and Ghanaian Cedi (GHS). For USD pricing, the bot will need to convert the USD amount to NGN using a live exchange rate before calling the Paystack API, or ensure the Paystack account is configured for USD transactions.*

### 2.2 Payment Flow

1.  **Initiation**: User selects a plan (Trial or Monthly). The bot calls the Paystack **Transaction Initialize API** with the user's email and the plan code.
2.  **Redirection**: Paystack returns an `authorization_url`. The bot sends this URL to the user for payment.
3.  **Verification (Webhook)**: This is the critical step for 24/7 access.
    *   A public-facing server (e.g., Render, not GitHub Actions) must be set up to receive Paystack **Webhooks**.
    *   When a payment is successful, Paystack sends a `transaction.success` event to this server.
    *   The server endpoint verifies the transaction and updates the user's `is_subscribed` and `expiry_date` in the SQLite database.

## 3. Implementation Steps

1.  **Database Setup**: Create the SQLite database and `users` table.
2.  **Paystack Utility**: Implement functions to initialize and verify transactions.
3.  **Middleware**: Create a decorator (`@subscription_required`) to wrap all prediction functions, checking the user's status.
4.  **Bot Logic**: Update `/start` and add a `/subscribe` command to handle the invite and payment flow.
5.  **Webhook Simulation**: Since the sandbox cannot host a public webhook, the final implementation will require the user to manually verify the transaction using the Paystack **Transaction Verify API** after payment, or deploy to a service that supports webhooks.
