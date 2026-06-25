---
title: "Permissions"
description: "Which action requires which role."
lang: en
audience: "All roles"
status: stable
lastReviewed: 2026-06-24
---

# Permissions

> Overview of which role may use which areas. **Admin** may always do everything.

**Audience:** all roles. See also [Roles](/docs/en/reference/roles.md).

## Matrix (excerpt)

| Area | Viewer | Operator | Admin |
| --- | :---: | :---: | :---: |
| Dashboard / monitoring / logs (read) | ✅ | ✅ | ✅ |
| Stream jobs / channels / sources / profiles / destinations | – | ✅ | ✅ |
| Media library / playlists / recordings | – | ✅ | ✅ |
| Platform metadata / assets | – | ✅ | ✅ |
| User management | – | – | ✅ |
| Settings (instance) | – | – | ✅ |
| Notifications | – | – | ✅ |
| Backup / restore | – | – | ✅ |
| Audit log / updates | – | – | ✅ |

## Enforcement

The check runs **server-side** per route. A missing entitlement → HTTP `403`
(`auth.forbidden`).

## Related pages

- [Roles](/docs/en/reference/roles.md) · [Users & roles](/docs/en/user-guide/users-roles.md)

---
_Last reviewed: 2026-06-24 · Status: stable_
