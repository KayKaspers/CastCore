---
title: "Roles"
description: "Admin, Operator, Viewer in detail."
lang: en
audience: "All roles"
status: stable
lastReviewed: 2026-06-24
---

# Roles

> CastCore uses role-based access control (RBAC). Each API route requires a specific
> role; **Admin** may always do everything.

**Audience:** all roles.

## The three roles

| Role | May … |
| --- | --- |
| **Admin** | Everything: users, settings, updates, backups, notifications, plus all streams/sources/platforms |
| **Operator** | Create/control streams, channels, sources, platforms, recordings; **no** user/system administration |
| **Viewer** | Read-only: dashboards, monitoring, logs, status |

## How is it enforced?

The check runs **server-side** for every route. A missing entitlement yields HTTP `403`
with the translatable code `auth.forbidden`.

## Related pages

- [Users & roles](/docs/en/user-guide/users-roles.md)
- [Permissions](/docs/en/reference/permissions.md)
- [Security best practices](/docs/en/admin-guide/security.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
