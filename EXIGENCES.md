# Exigences de sécurité de l'application des notes

| # | Exigence : « Le système doit… » | Vérification | Étape du SDLC | Test |
|---|---|---|---|---|
| 1 | protéger la recherche des étudiants contre les injections SQL. | Vérifier que les entrées utilisateur sont traitées sans exécuter du SQL non autorisé. | Développement | S1 |
| 2 | refuser la modification d'une note si l'utilisateur n'est pas authentifié. | Vérifier que l'API retourne le code HTTP 401 sans jeton valide. | Développement | S2 |
| 3 | interdire aux étudiants de modifier les notes. | Vérifier que l'API retourne le code HTTP 403 pour un étudiant. | Développement | S3 |
| 4 | autoriser un enseignant à modifier uniquement les notes de son module. | Vérifier que l'API refuse la modification d'une note d'un autre module. | Développement | S4 |
| 5 | accepter uniquement les notes numériques comprises entre 0 et 20. | Vérifier que l'API retourne le code HTTP 400 pour une note invalide. | Développement | S5 |
| 6 | permettre à un enseignant authentifié de modifier une note de son module. | Vérifier que l'API retourne HTTP 200 et que la note est bien modifiée. | Tests | S6 |
| 7 | ne pas révéler les détails techniques en cas d'erreur interne. | Vérifier que la réponse HTTP 500 ne révèle pas d'informations sensibles. | Tests | S7 |