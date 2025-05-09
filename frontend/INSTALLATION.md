# Guide d'installation de BDKids

Ce guide vous explique comment installer et exécuter le projet BDKids sur votre ordinateur en utilisant Visual Studio Code.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- [Node.js](https://nodejs.org/) (version 14.0.0 ou supérieure)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Git](https://git-scm.com/) (optionnel, pour cloner le dépôt)

## Étape 1 : Télécharger ou cloner le projet

Vous pouvez soit télécharger le projet sous forme d'archive ZIP et l'extraire, soit le cloner avec Git si vous avez accès au dépôt :

```bash
git clone [URL_DU_DEPOT]
```

## Étape 2 : Ouvrir le projet dans Visual Studio Code

1. Lancez Visual Studio Code
2. Allez dans `Fichier > Ouvrir le dossier...` (ou `File > Open Folder...`)
3. Naviguez jusqu'au dossier du projet BDKids et sélectionnez-le

## Étape 3 : Installer les dépendances

Ouvrez un terminal dans Visual Studio Code en allant dans `Terminal > Nouveau terminal` (ou `Terminal > New Terminal`), puis exécutez :

```bash
npm install
```

Cette commande installera toutes les dépendances nécessaires définies dans le fichier `package.json`.

## Étape 4 : Lancer le serveur de développement

Dans le même terminal, exécutez :

```bash
npm run dev
```

Cette commande démarre le serveur de développement Vite.

## Étape 5 : Accéder au site

Une fois le serveur démarré, vous verrez un message dans le terminal indiquant l'URL à laquelle le site est accessible, généralement :

```
  VITE v4.4.9  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.X.X:5173/
```

Vous pouvez :
- Cliquer sur l'URL dans le terminal (si votre terminal le permet)
- Ou ouvrir votre navigateur et saisir manuellement l'adresse `http://localhost:5173/`

## Extensions VS Code recommandées

Pour une meilleure expérience de développement, installez ces extensions dans Visual Studio Code :

1. **ESLint** : Pour la vérification du code JavaScript
2. **Prettier** : Pour le formatage automatique du code
3. **ES7+ React/Redux/React-Native snippets** : Pour des raccourcis de code React
4. **Vite** : Pour une meilleure intégration avec Vite

Pour installer une extension, cliquez sur l'icône des extensions dans la barre latérale de VS Code (ou appuyez sur `Ctrl+Shift+X`), recherchez l'extension et cliquez sur "Installer".

## Commandes utiles

- `npm run dev` : Démarre le serveur de développement
- `npm run build` : Compile le projet pour la production
- `npm run preview` : Prévisualise la version de production localement

## Résolution des problèmes courants

### Le serveur ne démarre pas
- Vérifiez que le port 5173 n'est pas déjà utilisé par une autre application
- Essayez de redémarrer VS Code ou votre ordinateur

### Erreurs d'installation des dépendances
- Supprimez le dossier `node_modules` et le fichier `package-lock.json`
- Exécutez à nouveau `npm install`

### Page blanche dans le navigateur
- Vérifiez la console du navigateur (F12) pour voir les erreurs
- Assurez-vous que tous les fichiers sont correctement chargés

## Structure des fichiers du projet

```
bd-enfants-ia/
├── node_modules/       # Dépendances installées (généré automatiquement)
├── public/             # Fichiers statiques accessibles publiquement
│   ├── favicon.svg
│   ├── owl-logo.svg
│   ├── pencil-logo.svg
│   └── cloud-logo.svg
├── src/                # Code source du projet
│   ├── components/     # Composants React
│   │   ├── Header.jsx
│   │   ├── Header.css
│   │   ├── ContentTypeSelector.jsx
│   │   └── ...
│   ├── App.jsx         # Composant principal
│   ├── App.css         # Styles du composant principal
│   ├── main.jsx        # Point d'entrée de l'application
│   └── index.css       # Styles globaux
├── index.html          # Page HTML principale
├── package.json        # Configuration du projet et dépendances
└── vite.config.js      # Configuration de Vite
```
