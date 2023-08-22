/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AdaptationStrategy } from './AdaptationStrategy';
import type { InformationStrategy } from './InformationStrategy';
import type { MemoryStrategy } from './MemoryStrategy';

export type ConversationCreate = {
    /**
     * A name to assign to the conversation to later remember it.
     */
    name?: (string | null);
    /**
     * The display name that the user wants to use for the conversation. This cannot be changed once you start the conversation. If your user name collides with the clone name, then an additional digit will be added
     */
    user_name?: (string | null);
    /**
     * Whether to turn off memory (old messages removed at context length limit), use short-term memory, or use the advanced Clonr long-term memory
     */
    memory_strategy?: MemoryStrategy;
    /**
     * The level of factual accuracy to give your bot. Internal enables creator knowledge sources. External allows for pulling information on current events.
     */
    information_strategy?: InformationStrategy;
    /**
     * How flexible the clone is on changing its long description. Static means never chaning. Fluid means completely adaptive. Dynamic means partial adaption.
     */
    adaptation_strategy?: (AdaptationStrategy | null);
    /**
     * The clone that a user will chat with
     */
    clone_id: string;
};

