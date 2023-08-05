/* eslint-disable @next/next/no-img-element */
'use client'

import { Character } from '@/types'
import styles from '@/styles/Cards.module.scss'
import { formatNumber } from '@/utils/formatNumber'

interface CardsProps {
  defaultCard?: boolean
  item: Character
  edgeCard?: 'left' | 'right' | undefined
}

export default function Cards({
  defaultCard = true,
  item,
  edgeCard,
}: CardsProps): React.ReactElement {
  const style = defaultCard ? styles.card : styles.longCard
  const infoStyle = defaultCard ? styles.cardInfo : styles.more
  const { name, short_description, num_messages, tags, avatar_uri } = item
  // const image = defaultCard ? banner : poster

  let edgeClass = ''
  if (edgeCard === 'left') {
    edgeClass = 'origin-left'
  } else if (edgeCard === 'right') {
    edgeClass = 'origin-right'
  }

  return (
    <div className={`${style} ${edgeClass}`}>
      <div className={styles.cardPoster}>
        <img
          src={avatar_uri}
          alt='img'
          className={`absolute ${styles.cardPoster}`}
        />
        <div className='absolute top-0 left-0 w-full h-full bg-gradient-to-t from-black to-transparent opacity-20 rounded-[6px]'></div>
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
              num_messages
            )} chats`}</span>
          </div>
          <div className={styles.row}>
            <span className='text-gray-400 text-[11px] py-[0.2rem] line-clamp-2'>
              {short_description}
            </span>
          </div>
          <GenreComponent tags={tags} />
        </div>
      </div>
    </div>
  )
}

import React from 'react'

type GenreProps = {
  tags: { name: string }[]
}

const GenreComponent: React.FC<GenreProps> = ({ tags }) => {
  return (
    <div className={`${styles.row} gap-x-1`}>
      {tags.map((tag, index) => {
        const isLast = index === tags.length - 1
        return (
          <div key={index} className={styles.row}>
            <span className={styles.regularText}>{tag.name}</span>
            {!isLast && <div className={styles.dot}>&bull;</div>}
          </div>
        )
      })}
    </div>
  )
}