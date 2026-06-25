---
title: "Users & roles"
description: "Manage users and assign roles (Admin/Operator/Viewer)."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Users & roles

> In **User management** (`/users`, admin only) you create users, assign roles, reset
> passwords and enable/disable accounts.

**Audience:** administrators.

## Create a user

1. In the form provide a **username**, **password** (min. 8 chars), optional **email** and
   a **role**.
2. **Create**. The user can sign in afterwards; their language can be changed per user
   later under [Settings](/docs/en/user-guide/settings.md).

## Change roles

Toggle the roles **admin**, **operator**, **viewer** per user right in the table. At least
one role is kept. Role meanings: [Roles](/docs/en/reference/roles.md).

## Account active/inactive

Use the **active** checkbox to lock or unlock an account. A **disabled** user cannot sign
in.

## Reset password

**Reset password** → enter a new password (min. 8 chars).

## Notes

> 🔐 Actions like create/delete are recorded in the
> [audit log](/docs/en/admin-guide/security.md). You cannot disable or delete your **own**
> account.

> ⚠️ Passwords are hashed with **argon2id** and never stored in clear text.

## Related pages

- [Roles](/docs/en/reference/roles.md)
- [Permissions](/docs/en/reference/permissions.md)
- [Security best practices](/docs/en/admin-guide/security.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
