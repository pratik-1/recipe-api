# Recipe App

This containerized portable application is able to create new user, creates multiple recipes and assigns tags and ingredients to recipes. The project development follows Test driven development and configured with Github CICD.

## [1] Custom User model

- Create custom User, Superuser.
- Supports 'Token' based authentication.
- User can login using email and password.
- User can create multiple recipes in his/her account
- User APIs:
  - `Post` - /api/user/token/
  - `Get` -/api/user/me/
  - `Post` - /api/user/create/
  - `Put` -/api/user/me/
  - `Patch` - /api/user/me/

## [2] Recipe

- Accessible on authentication only.
- Role based authorisation.
- Recipe can have multiple tags, ingredients
- Filter recipes based on list of tag-ids or ingredient-ids.
- Updating recipe taglist can:
  - create new tag and assign to recipe object.
  - use existing tags to assign to recipe object.
- Updating recipe ingredients list can:
  - create new ingredient and assign to recipe object.
  - use existing ingredient to assign to recipe object.
- Recipe Apis:
  - `List` - /api/recipe/recipes/
  - `Create` - /api/recipe/recipes/
  - `Detail` - /api/recipe/recipes/{id}/
  - `Update` - /api/recipe/recipes/{id}/
  - `Partial` - /api/recipe/recipes/{id}/
  - `Delete` - /api/recipe/recipes/{id}/

## [3] Tags

- Accessible on authenticated only.
- Role based authorisation.
- Filter tags based on 'assigned_only' param
- Tags Apis:
  - `List` - /api/recipe/tags/
  - `Put` - /api/recipe/tags/{id}/
  - `Patch` - /api/recipe/tags/{id}/
  - `Delete` - /api/recipe/tags/{id}/

## [4] Ingredients

- Accessible on authenticated only.
- Role based authorisation.
- Filter ingredients based on 'assigned_only' param
- Ingredients Apis:
  - `List` - /api/recipe/ingredients/
  - `Put` - /api/recipe/ingredients/{id}/
  - `Patch` - /api/recipe/ingredients/{id}/
  - `Delete` - /api/recipe/ingredients/{id}/

## [5] Images

- Upload an image for a recipe.
- Image Apis:
  - `Post` - /api/recipe/recipes/{id}/upload-image/

## [6] Techstack

- Python
- Django
- Django Rest Framework
- Postgres DB
- Docker

## [7] OpenAPI Standards

- Creates schema using DRF-spectacular.
- Configured Swagger UI with OpenAPI.
