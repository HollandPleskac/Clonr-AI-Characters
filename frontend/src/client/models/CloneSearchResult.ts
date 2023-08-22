/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Tag } from './Tag';

export type CloneSearchResult = {
    id: string;
    created_at: string;
    updated_at: string;
    creator_id: string;
    name: string;
    short_description: (string | null);
    long_description: (string | null);
    avatar_uri: (string | null);
    num_messages: number;
    num_conversations: number;
    tags: Array<Tag>;
};

