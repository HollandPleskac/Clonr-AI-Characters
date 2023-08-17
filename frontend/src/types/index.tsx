const BreakpointValues: Record<Breakpoint, number> = {
  XS: 480,
  SM: 640,
  MD: 768,
  LG: 1025,
  XL: 1280,
  XXL: 1536,
}

enum Breakpoint {
  XS = 'XS',
  SM = 'SM',
  MD = 'MD',
  LG = 'LG',
  XL = 'XL',
  XXL = 'XXL',
}

export type Maybe<T> = T | null

export type Dimension = {
  height: number
  width: number
}

export type DimensionDetail = {
  dimension: Dimension
  breakpoint: Breakpoint
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
}

export enum MediaType {
  MOVIE = 'movie',
  TV = 'tv',
}

export type Tag = {
  id: string
  created_at: Date
  updated_at: Date
  color_code: string
  name: string
}

// export type Character = {
//   id: string
//   created_at: Date
//   updated_at: Date
//   creator_id: string
//   name: string
//   short_description: string
//   avatar_uri: string
//   num_messages: number
//   num_conversations: number
//   tags: Tag[]
// }

export type Character = {
  id: string;
  created_at: string;
  updated_at: string;
  creator_id: string;
  name: string;
  short_description: string;
  long_description
  avatar_uri: string;
  num_messages: number;
  num_conversations: number;
  tags: Tag[];
}

// TODO: EDIT
// TODO: make call for this 
export type CharacterChat = {
  character: Character
  lastMessage: string
  lastConversationId: string
}


// export type Conversation = {
//   id: string
//   character: Character
//   lastBotMessage: string
//   lastUserMessage: string
//   lastChatTime: Date
//   memoryType: 'long' | 'short'
// }

// TODO: add character: Clone field here
// TODO: lastBotMsg and lastUserMsg?
export type Conversation = {
  id: string;
  name: string;
  user_name: string;
  memory_strategy: string;
  information_strategy: string,
  adaptation_strategy: string,
  clone_id: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  is_active: boolean
}

// export type Message = {
//   id: string
//   img: string
//   alt: string
//   name: string
//   content: string
//   timeStamp: Date
//   senderType: 'bot' | 'user'
// }

export type Message = {
  id: string;
  content: string;
  created_at: string;
  updated_at: string;
  sender_name: string;
  timestamp: string;
  is_clone: boolean;
  is_main: boolean;
  is_active: boolean;
  parent_id: string;
  clone_id: string;
  user_id: string;
  conversation_id: string;
}

export type ImageType = 'poster' | 'original'

export type Section = {
  heading: string
  endpoint: string
  defaultCard?: boolean
  topList?: boolean
}
