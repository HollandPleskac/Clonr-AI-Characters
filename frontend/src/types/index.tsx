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

export type Tag = {
  name: string
}

export enum MediaType {
  MOVIE = 'movie',
  TV = 'tv',
}

// export type Character = {
//   id: number
//   name: string
//   description: string
//   poster: string
//   banner: string
//   rating: number
//   tags: Tag[]
//   messages: number
// }

export type Character = {
  id: string
  created_at: Date
  updated_at: Date
  creator_id: string
  name: string
  short_description: string
  avatar_uri: string
  num_messages: number
  num_conversations: number
  tags: Tag[]
}

export type ImageType = 'poster' | 'original'

export type Section = {
  heading: string
  endpoint: string
  defaultCard?: boolean
  topList?: boolean
}
