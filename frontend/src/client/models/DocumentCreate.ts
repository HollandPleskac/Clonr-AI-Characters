/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type DocumentCreate = {
    content: string;
    /**
     * A human readable name for the document. If none is given, one will be automatically assigned.
     */
    name: (string | null);
    /**
     * A short description of the document
     */
    description: (string | null);
    /**
     * One word tag describing the source. Letters, numbers, underscores, and hyphens allowed.
     */
    type: string;
    /**
     * The resource URL if applicable
     */
    url?: (string | null);
};

