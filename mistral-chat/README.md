# Chat Mistral — app web minimale

App web de chat minimaliste qui appelle l'API Mistral avec le [SDK TypeScript officiel](https://github.com/mistralai/client-ts) (`@mistralai/mistralai`), avec le modèle `mistral-small-latest`.

- **Backend** : Node.js + TypeScript, serveur HTTP natif (`node:http`, zéro dépendance web supplémentaire).
- **Frontend** : une seule page `public/index.html` en JavaScript vanilla (aucun framework).
- **Sécurité** : `MISTRAL_API_KEY` ne quitte jamais le serveur. Le navigateur n'appelle que `POST /api/chat`, qui fait l'appel à l'API Mistral côté serveur.

## Prérequis

- Node.js >= 18 (testé avec Node 22)
- Une clé API Mistral, à créer sur [console.mistral.ai](https://console.mistral.ai) (section « API keys »)

## Installation

```bash
npm install
cp .env.example .env
```

Puis éditez `.env` et renseignez votre clé :

```bash
MISTRAL_API_KEY=votre_cle_api_ici
```

## Lancer en local (développement)

```bash
npm run dev
```

Puis ouvrez <http://localhost:3000> dans votre navigateur.

## Lancer en production

```bash
npm run build
npm start
```

Le serveur compilé tourne alors depuis `dist/` sur <http://localhost:3000> (port modifiable via la variable d'environnement `PORT`).

## Structure

```
├── package.json          # scripts + dépendances
├── tsconfig.json
├── .env.example          # modèle de fichier .env (la vraie clé va dans .env, ignoré par git)
├── src/
│   └── server.ts         # serveur HTTP + endpoint POST /api/chat (appelle le SDK Mistral)
└── public/
    └── index.html        # interface de chat
```

## Fonctionnement

1. Le navigateur envoie l'historique de la conversation à `POST /api/chat` (`{ "messages": [{ "role": "user", "content": "..." }] }`).
2. Le serveur valide la requête, puis appelle `client.chat.complete({ model: 'mistral-small-latest', messages })`.
3. Le serveur renvoie `{ "reply": "..." }` au navigateur, qui l'affiche.

`MISTRAL_API_KEY` est lue uniquement côté serveur (depuis `.env` ou l'environnement) et n'est jamais exposée au client.
