# Recipe App

## Containerized application

### [1] Custom User model

- Create custom User, Superuser
- Login using email and password
- Token based authentication
- User APIs:
  - `POST-` /api/user/token/
  - `GET-`/api/user/me/
  - `POST-` /api/user/create/
  - `PUT-`/api/user/me/
  - `PATCH-` /api/user/me/

### [2] Recipe APIs

- Accessible on authenticated only
- Role based authorisation
- Recipe Apis:
  - `List-` /api/recipe/recipes/
  - `Create-` /api/recipe/recipes/
  - `Detail-` /api/recipe/recipes/{id}/
  - `Update-` /api/recipe/recipes/{id}/
  - `Partial-` /api/recipe/recipes/{id}/
  - `Delete-` /api/recipe/recipes/{id}/
