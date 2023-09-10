

'use client';

import useSWR from 'swr';
import { ConversationsService } from '@/client';

export function useRevisions(queryParams: { conversationId: string }) {
    const {
        conversationId
    } = queryParams;

    const fetcher = async () => {
        try {
            const messages = await ConversationsService.getCurrentRevisionsConversationsConversationIdCurrentRevisionsGet(conversationId)
            
            console.log("revisions from fetcher", messages)
            return messages
        } catch (error) {
            console.log("error getting revisions")
            throw new Error('Error getting revisions: ' + error.message);
        }
    };

    const { data, isLoading, error, mutate } = useSWR('revisions'+conversationId, fetcher);

    return {
        data: data,
        isLoading: isLoading,
        error: error,
        mutate: mutate
    };
}