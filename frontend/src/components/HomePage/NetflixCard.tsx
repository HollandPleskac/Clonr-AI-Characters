/* eslint-disable @next/next/no-img-element */
'use client'

import React from 'react'
import { Character } from '@/types'
import styles from '@/styles/Cards.module.scss'
import { formatNumber } from '@/utils/formatNumber'
import { Tag } from '@/types'
import TagsComponent from './Tags'
import { CloneSearchResult } from '@/client/models/CloneSearchResult'
import { useSession } from 'next-auth/react'

interface CardsProps {
  defaultCard?: boolean
  item: CloneSearchResult
  edgeCard?: 'left' | 'right' | undefined
  onClick?: () => void
}

export default function Cards({
  defaultCard = true,
  item,
  edgeCard,
  onClick,
}: CardsProps): React.ReactElement {
  const { status } = useSession();
  const style = defaultCard ? styles.card : styles.longCard
  const infoStyle = defaultCard ? styles.cardInfo : styles.more
  const { name, short_description, num_messages, tags, avatar_uri, num_conversations } = item

  let edgeClass = ''
  if (edgeCard === 'left') {
    edgeClass = 'origin-left'
  } else if (edgeCard === 'right') {
    edgeClass = 'origin-right'
  }

  const options = status !== 'authenticated' ? { 'data-hs-overlay': '#hs-slide-down-animation-modal' } : { 'onClick': onClick }
  
  return (
    <div
      className={`${style} ${edgeClass}`}
      {...options}
    >
      <div className={styles.cardPoster}>
        <img
          src={avatar_uri ? avatar_uri : '/img/avatars/avatar-1.jpg'}
          alt='img'
          className={`absolute ${styles.cardPoster}`}
        />
        {/* bg used to be black */}
        <div className='absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[rgba(37,37,37)] from-0% to-transparent to-50% opacity-80 rounded-t-[6px]'></div>
        <strong className='text-white absolute bottom-1 left-2 line-clamp-1'>
          {name}
        </strong>
      </div>
      <div className={infoStyle}>
        <div className={styles.textDetails}>
          {/* <strong className='text-white'>{name}</strong> */}
          <div className={`${styles.row} justify-between`}>
            {/* <span className={styles.greenText}>{`${rating * 10}% match`}</span> */}
            <span className={styles.greenText}>{`${formatNumber(
              num_conversations
            )} chats`}</span>
          </div>
          <div className={styles.row}>
            <span className='text-gray-400 text-[11px] py-[0.2rem] line-clamp-2'>
              {short_description}
            </span>
          </div>
          <TagsComponent tags={tags} />
        </div>
      </div>
    </div>
  )
}

