declare global {
    export namespace JSX {
      interface IntrinsicElements {
        'stripe-pricing-table': {
          key: string;
          'pricing-table-id': string;
          'publishable-key': string;
          'client-reference-id': string;
        };
      }
    }
  }