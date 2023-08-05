'use client'

import { ReactNode } from 'react'

interface FadeTransitionProps {
  loaded: boolean
  children: ReactNode
  duration?: number
}

export default function ScaleFadeIn(props: FadeTransitionProps) {
  const visibility = props.loaded ? 'visible' : 'hidden'
  const duration = props?.duration != undefined ? props.duration : 500

  return (
    <div
      className={`transition-all ${
        props.loaded ? 'opacity-100' : 'opacity-0 scale-75'
      } duration-${duration} ease-in-out transform-gpu`}
      style={{ visibility: visibility }}
    >
      {props.children}
    </div>
  )
}
