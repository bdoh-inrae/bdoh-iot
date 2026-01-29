






🧭 Règle mnémotechnique

L’ORM est un détail d’implémentation.
L’API est un contrat public.
Le core est la vérité.

✅ Ce qu’on VEUT à la place (le bon flux)
HTTP
 ↓
Pydantic (API)
 ↓
Core (métier)
 ↓
Mapper
 ↓
ORM (DB)


Et dans l’autre sens :

ORM
 ↓
Mapper
 ↓
Core
 ↓
Schema API
 ↓
JSON