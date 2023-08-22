/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AdaptationStrategy } from '../models/AdaptationStrategy';
import type { Conversation } from '../models/Conversation';
import type { ConversationCreate } from '../models/ConversationCreate';
import type { ConversationUpdate } from '../models/ConversationUpdate';
import type { ConvoSortType } from '../models/ConvoSortType';
import type { InformationStrategy } from '../models/InformationStrategy';
import type { MemoryStrategy } from '../models/MemoryStrategy';
import type { Message } from '../models/Message';
import type { MessageCreate } from '../models/MessageCreate';
import type { MessageGenerate } from '../models/MessageGenerate';
import type { MsgSortType } from '../models/MsgSortType';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ConversationsService {

    /**
     * Get Queried Convos
     * @param tags
     * @param cloneName
     * @param cloneId
     * @param sort
     * @param memoryStrategy
     * @param adaptationStrategy
     * @param informationStrategy
     * @param updatedAfter
     * @param updatedBefore
     * @param offset
     * @param limit
     * @returns Conversation Successful Response
     * @throws ApiError
     */
    public static getQueriedConvosConversationsGet(
        tags?: (Array<number> | null),
        cloneName?: (string | null),
        cloneId?: (string | null),
        sort?: ConvoSortType,
        memoryStrategy?: (MemoryStrategy | null),
        adaptationStrategy?: (AdaptationStrategy | null),
        informationStrategy?: (InformationStrategy | null),
        updatedAfter?: (string | null),
        updatedBefore?: (string | null),
        offset?: number,
        limit: number = 10,
    ): CancelablePromise<Array<Conversation>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/conversations/',
            query: {
                'tags': tags,
                'clone_name': cloneName,
                'clone_id': cloneId,
                'sort': sort,
                'memory_strategy': memoryStrategy,
                'adaptation_strategy': adaptationStrategy,
                'information_strategy': informationStrategy,
                'updated_after': updatedAfter,
                'updated_before': updatedBefore,
                'offset': offset,
                'limit': limit,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Conversation
     * @param requestBody
     * @param maxFreeMessages
     * @returns Conversation Successful Response
     * @throws ApiError
     */
    public static createConversationConversationsPost(
        requestBody: ConversationCreate,
        maxFreeMessages: number = 10,
    ): CancelablePromise<Conversation> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/conversations/',
            query: {
                'max_free_messages': maxFreeMessages,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Conversation By Id
     * @param conversationId
     * @returns Conversation Successful Response
     * @throws ApiError
     */
    public static getConversationByIdConversationsConversationIdGet(
        conversationId: string,
    ): CancelablePromise<Conversation> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/conversations/{conversation_id}',
            path: {
                'conversation_id': conversationId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Patch Conversation
     * @param conversationId
     * @param requestBody
     * @returns Conversation Successful Response
     * @throws ApiError
     */
    public static patchConversationConversationsConversationIdPatch(
        conversationId: string,
        requestBody: ConversationUpdate,
    ): CancelablePromise<Conversation> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/conversations/{conversation_id}',
            path: {
                'conversation_id': conversationId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Conversation
     * @param conversationId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteConversationConversationsConversationIdDelete(
        conversationId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/conversations/{conversation_id}',
            path: {
                'conversation_id': conversationId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Messages
     * @param conversationId
     * @param q
     * @param sort
     * @param sentAfter
     * @param sentBefore
     * @param offset
     * @param limit
     * @param isActive
     * @param isMain
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static getMessagesConversationsConversationIdMessagesGet(
        conversationId: string,
        q?: (string | null),
        sort?: MsgSortType,
        sentAfter?: (string | null),
        sentBefore?: (string | null),
        offset?: number,
        limit: number = 20,
        isActive: boolean = true,
        isMain: boolean = true,
    ): CancelablePromise<Array<Message>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/conversations/{conversation_id}/messages',
            path: {
                'conversation_id': conversationId,
            },
            query: {
                'q': q,
                'sort': sort,
                'sent_after': sentAfter,
                'sent_before': sentBefore,
                'offset': offset,
                'limit': limit,
                'is_active': isActive,
                'is_main': isMain,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Receive Message
     * @param conversationId
     * @param requestBody
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static receiveMessageConversationsConversationIdMessagesPost(
        conversationId: string,
        requestBody: MessageCreate,
    ): CancelablePromise<Message> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/conversations/{conversation_id}/messages',
            path: {
                'conversation_id': conversationId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Generate Clone Message
     * @param conversationId
     * @param requestBody
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static generateCloneMessageConversationsConversationIdGeneratePost(
        conversationId: string,
        requestBody: MessageGenerate,
    ): CancelablePromise<Message> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/conversations/{conversation_id}/generate',
            path: {
                'conversation_id': conversationId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Current Revisions
     * @param conversationId
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static getCurrentRevisionsConversationsConversationIdCurrentRevisionsGet(
        conversationId: string,
    ): CancelablePromise<Array<Message>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/conversations/{conversation_id}/current_revisions',
            path: {
                'conversation_id': conversationId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Message
     * @param messageId
     * @param conversationId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteMessageConversationsConversationIdMessagesMessageIdDelete(
        messageId: string,
        conversationId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/conversations/{conversation_id}/messages/{message_id}',
            path: {
                'message_id': messageId,
                'conversation_id': conversationId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Message By Id
     * @param messageId
     * @param conversationId
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static getMessageByIdConversationsConversationIdMessagesMessageIdGet(
        messageId: string,
        conversationId: string,
    ): CancelablePromise<Message> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/conversations/{conversation_id}/messages/{message_id}',
            path: {
                'message_id': messageId,
                'conversation_id': conversationId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Set Revision As Main
     * @param messageId
     * @param conversationId
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static setRevisionAsMainConversationsConversationIdMessagesMessageIdIsMainPost(
        messageId: string,
        conversationId: string,
    ): CancelablePromise<Message> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/conversations/{conversation_id}/messages/{message_id}/is_main',
            path: {
                'message_id': messageId,
                'conversation_id': conversationId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

}
