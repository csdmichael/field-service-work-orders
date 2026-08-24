# Field Service Work Orders — UI

Angular 18 + Ionic 8 standalone components. Talks to the API over REST; never queries the database directly.

`npm start` runs the dev server, `npm run build` produces `dist/`.

## Screens

- Work Order Queue mockup with specification panel]
- Asset Detail and Diagnostics mockup with specification panel
- Service Log and Parts mockup with specification panel]
- Completion and Sign-off mockup with specification panel]

## API base URL

`index.html` declares `window.__API_BASE_URL__`. The deploy pipeline rewrites the placeholder with the published API URL, so the UI and API can live on separate App Services.
