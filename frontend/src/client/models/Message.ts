/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type Message = {
    /**
     * Message content. Messages may not contain <| or |>.
     */
    content: string;
    id: string;
    created_at: string;
    updated_at: string;
    sender_name: string;
    timestamp: string;
    is_clone: boolean;
    is_main: boolean;
    is_active: boolean;
    parent_id: (string | null);
    clone_id: string;
    user_id: string;
    conversation_id: string;
};

