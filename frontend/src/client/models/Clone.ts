/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Tag } from './Tag';

export type Clone = {
    id: string;
    created_at: string;
    updated_at: string;
    name: string;
    short_description: string;
    long_description: (string | null);
    greeting_message: (string | null);
    avatar_uri: (string | null);
    is_active: boolean;
    is_public: boolean;
    is_short_description_public: boolean;
    is_long_description_public: boolean;
    is_greeting_message_public: boolean;
    creator_id: string;
    num_messages: number;
    num_conversations: number;
    tags: Array<Tag>;
};

