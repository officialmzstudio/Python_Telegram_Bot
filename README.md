This project is an automated Telegram bot designed to manage the entire sales and configuration delivery process for various proxy services (V2Ray, OpenVPN, SSH). It focuses on high efficiency and security by minimizing manual administrative tasks.

## Technical Features & Implementation

The bot's core functionality is built upon the robust `python-telegram-bot` library, leveraging specialized handlers for a seamless user experience.

## Core Libraries & Dependencies

| Library | Purpose |
| :--- | :--- |
| **`python-telegram-bot`** | Handles all interactions with the Telegram Bot API. |

## Key Implementation Concepts

The smooth workflow is managed by strategically combining state control and precise message handling:

1.  **ConversationHandler (State Machine):**
    * The entire purchase flow (from `/start` to receipt submission) is managed by the `ConversationHandler`.
    * This component ensures the bot tracks the user's specific **state** (`SELECT_SERVICE`, `WAIT_FOR_RECEIPT`) and only accepts expected input (e.g., waiting only for a photo when in the receipt state), providing a robust, error-resistant flow.

2.  **Inline Keyboards & Callback Queries:**
    * All customer navigation (menu display, service selection) uses **Inline Keyboards**.
    * Button presses are handled by **`CallbackQueryHandler`** for editing existing messages, thus maintaining a clean chat history for the user.

3.  **Filtered Message Handlers:**
    * **Payment Receipt:** A dedicated **`MessageHandler(filters.PHOTO, ...)`** is used to capture and process the user's payment receipt photo.
    * **Admin File Delivery:** Critical admin functions use specific filters (**`filters.Document & filters.User(ADMIN_ID)`**) to ensure that only files sent by the administrator with the correct command caption are processed for customer delivery.

4.  **Admin Protection:**
    * Administrative delivery commands (`/send` text and file delivery) are strictly secured using a filter based on the defined **`ADMIN_ID`**, preventing unauthorized usage by customers.
