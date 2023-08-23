## Running locally

Run via docker - but if need to run local, can use:

```bash
npm run dev
```

## Generating Client
```bash
npm run generate-client
```

## Changes to make after generating client
Refer to this: https://github.com/ferdikoomen/openapi-typescript-codegen/issues/1626

Make following modifications (for both resolve and reject):

```bash
this.#resolve?.(value); -> if (this.#resolve) this.#resolve(value);
```

```bash
node fix.ts 
```
