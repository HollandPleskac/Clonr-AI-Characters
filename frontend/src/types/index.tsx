import { type } from "os"

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
  id: number
  created_at: string
  updated_at: string
  color_code: string
  name: string
}

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

export type CharacterChat = {
  characterId: string
  characterName: string
  characterAvatarUri: string
  lastUpdatedAt: string
  lastMessage: string
  lastConversationId: string
}


export type Conversation = {
  name: string,
  user_name: string,
  memory_strategy: string,
  information_strategy: string,
  adaptation_strategy: string,
  clone_id: string,
  id: string,
  created_at: string,
  updated_at: string,
  user_id: string,
  is_active: boolean,
  num_messages_ever: number,
  last_message: string,
  clone_name: string
}

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

export type User = {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  private_chat_name: string;
  is_banned: boolean;
  nsfw_enabled: boolean;
  num_free_messages_sent: number;
  is_subscribed: boolean;
  is_allowed_beta_tester: boolean;
}



export type SidebarClone = {
  name: string,
  user_name: string,
  memory_strategy: string,
  information_strategy: string,
  adaptation_strategy: string,
  clone_id: string,
  id: string,
  created_at: string,
  updated_at: string,
  user_id: string,
  is_active: boolean,
  num_messages_ever: number,
  last_message: string,
  clone_name: string,
  rank: number,
  avatar_uri: string,
  group_updated_at: string
}