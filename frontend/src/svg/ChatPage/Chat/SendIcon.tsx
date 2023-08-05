type SvgIconProps = {
  svgClasses?: string
  strokeClasses?: string
}

export default function SendIcon({ svgClasses, strokeClasses }: SvgIconProps) {
  return (
    <svg
      width='26'
      height='26'
      viewBox='0 0 26 26'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
      className={svgClasses}
    >
      <path
        fill-rule='evenodd'
        clip-rule='evenodd'
        d='M3.07686 5.08586C2.84107 5.67596 3.16502 6.63393 3.81291 8.54989L4.97958 12H11.458C12.0103 12 12.458 12.4477 12.458 13C12.458 13.5523 12.0103 14 11.458 14H5.00931L3.83603 17.44C3.18114 19.3601 2.8537 20.3202 3.08869 20.9114C3.29276 21.4248 3.73104 21.8141 4.27186 21.9622C4.89462 22.1328 5.83524 21.7173 7.71648 20.8864L19.777 15.5594C21.6132 14.7484 22.5313 14.3428 22.8151 13.7795C23.0616 13.2901 23.0616 12.7158 22.8151 12.2264C22.5313 11.663 21.6132 11.2575 19.777 10.4465L7.69568 5.11032C5.82011 4.2819 4.88233 3.8677 4.26018 4.03761C3.71987 4.18517 3.28163 4.57339 3.07686 5.08586Z'
        className={strokeClasses}
        fill='#5848BC'
      />
    </svg>
  )
}
