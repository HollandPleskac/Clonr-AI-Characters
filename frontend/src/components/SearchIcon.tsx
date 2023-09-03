'use client'

type SvgIconProps = {
  svgClasses?: string
  strokeClasses?: string
}

export default function SearchIcon({
  svgClasses,
  strokeClasses,
}: SvgIconProps) {
  return (
    <svg
      width='24'
      height='24'
      viewBox='0 0 24 24'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
      className={svgClasses}
    >
      <path
        d='M16.6725 16.6412L21 21M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z'
        className={strokeClasses || 'stroke-[#dbdbdb]'}
        strokeWidth='1.8'
        strokeLinecap='round'
        strokeLinejoin='round'
      />
    </svg>
  )
}
